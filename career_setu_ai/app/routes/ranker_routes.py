from __future__ import annotations

import csv
import io

from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user

from app.extensions import db
from app.models.job_description import JobDescription
from app.models.bulk_ranking import BulkRankingRun

from app.services.bulk_ranker_service import (
    create_bulk_run,
    save_uploaded_files,
    parse_and_store_candidate_files,
    start_bulk_processing,
)

ranker_bp = Blueprint("ranker", __name__, url_prefix="/ranker")


@ranker_bp.route("/", methods=["GET"])
@login_required
def index():
    jds = (
        JobDescription.query
        .filter_by(user_id=current_user.id)
        .order_by(JobDescription.created_at.desc())
        .all()
    )
    return render_template("ranker/index.html", page_title="Bulk Ranker", jds=jds)


@ranker_bp.route("/start", methods=["POST"])
@login_required
def start():
    jd_id = int(request.form.get("jd_id") or 0)
    w_match = float(request.form.get("w_match") or 0.6)
    w_ats = float(request.form.get("w_ats") or 0.4)

    if "resumes" not in request.files:
        flash("No files received.", "danger")
        return redirect(url_for("ranker.index"))

    files = request.files.getlist("resumes")
    if not files:
        flash("Please upload at least 1 resume.", "warning")
        return redirect(url_for("ranker.index"))

    # Create run
    run = create_bulk_run(current_user.id, jd_id, weights={"match": w_match, "ats": w_ats})

    # Save uploaded files to disk
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    allowed_exts = set(current_app.config["ALLOWED_EXTENSIONS"])

    original_names = [f.filename for f in files]
    saved = save_uploaded_files(files, upload_dir=upload_dir, allowed_exts=allowed_exts)

    if not saved:
        run.status = "failed"
        run.error = "No valid files saved. Only PDF/DOCX allowed."
        db.session.commit()
        flash("No valid files saved. Upload PDF/DOCX only.", "danger")
        return redirect(url_for("ranker.index"))

    # Parse and store temporary Resume rows
    resume_ids = parse_and_store_candidate_files(
        user_id=current_user.id,
        upload_dir=upload_dir,
        files_saved=saved,
        original_names=original_names,
    )

    run.total_files = len(resume_ids)
    run.processed_files = 0
    run.results = {**(run.results or {}), "temp_resume_ids": resume_ids}
    db.session.commit()

    # Start background worker
    start_bulk_processing(run_id=run.id, user_id=current_user.id, upload_dir=upload_dir)

    return redirect(url_for("ranker.progress", run_id=run.id))


@ranker_bp.route("/progress/<int:run_id>")
@login_required
def progress(run_id: int):
    run = BulkRankingRun.query.filter_by(id=run_id, user_id=current_user.id).first_or_404()
    return render_template("ranker/progress.html", page_title="Ranking Progress", run=run)


@ranker_bp.route("/api/progress/<int:run_id>")
@login_required
def api_progress(run_id: int):
    run = BulkRankingRun.query.filter_by(id=run_id, user_id=current_user.id).first_or_404()
    payload = {
        "id": run.id,
        "status": run.status,
        "error": run.error,
        "total_files": run.total_files,
        "processed_files": run.processed_files,
        "results_ready": bool(run.results and (run.results.get("rows") or [])) if isinstance(run.results, dict) else False,
    }
    return jsonify(payload)


@ranker_bp.route("/results/<int:run_id>")
@login_required
def results(run_id: int):
    run = BulkRankingRun.query.filter_by(id=run_id, user_id=current_user.id).first_or_404()
    rows = []
    weights = {"match": 0.6, "ats": 0.4}
    if isinstance(run.results, dict):
        rows = run.results.get("rows") or []
        weights = run.results.get("weights") or weights
    return render_template(
        "ranker/results.html",
        page_title="Ranker Results",
        run=run,
        rows=rows,
        weights=weights,
    )


@ranker_bp.route("/export/<int:run_id>.csv")
@login_required
def export_csv(run_id: int):
    run = BulkRankingRun.query.filter_by(id=run_id, user_id=current_user.id).first_or_404()
    if run.status != "done":
        flash("Run not completed yet.", "warning")
        return redirect(url_for("ranker.results", run_id=run_id))

    rows = (run.results or {}).get("rows") or []
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["rank", "resume_id", "file_name", "final_score", "match_score", "ats_score"])
    for i, r in enumerate(sorted(rows, key=lambda x: x.get("final_score", 0), reverse=True), start=1):
        writer.writerow([
            i,
            r.get("resume_id"),
            r.get("file_name"),
            r.get("final_score"),
            r.get("match_score"),
            r.get("ats_score"),
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=bulk_ranking_run_{run_id}.csv"},
    )