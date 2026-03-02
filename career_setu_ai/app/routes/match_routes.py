from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import login_required, current_user

from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.services.match_service import match_resume_to_jd


match_bp = Blueprint("match", __name__, url_prefix="/match")


@match_bp.route("/", methods=["GET", "POST"])
@login_required
def select():
    """Select Resume + JD to generate Match Report."""
    resumes = (
        Resume.query
        .filter_by(user_id=current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    )

    jds = (
        JobDescription.query
        .filter_by(user_id=current_user.id)
        .order_by(JobDescription.created_at.desc())
        .all()
    )

    if request.method == "POST":
        resume_id = int(request.form.get("resume_id") or 0)
        jd_id = int(request.form.get("jd_id") or 0)

        if not resume_id or not jd_id:
            flash("Please select both a Resume and a Job Description.", "warning")
            return redirect(url_for("match.select"))

        return redirect(url_for("match.report", resume_id=resume_id, jd_id=jd_id))

    return render_template(
        "match/select.html",
        page_title="Match Engine",
        resumes=resumes,
        jds=jds,
    )


@match_bp.route("/report/<int:resume_id>/<int:jd_id>")
@login_required
def report(resume_id: int, jd_id: int):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    jd = JobDescription.query.filter_by(id=jd_id, user_id=current_user.id).first_or_404()

    result = match_resume_to_jd(
        parsed_resume=resume.parsed or {},
        analyzed_jd=jd.analyzed or {},
        jd_raw_text=jd.raw_text or "",
    )

    return render_template(
        "match/report.html",
        page_title="Match Report",
        resume=resume,
        jd=jd,
        result=result,
    )


@match_bp.route("/api/<int:resume_id>/<int:jd_id>")
@login_required
def api(resume_id: int, jd_id: int):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    jd = JobDescription.query.filter_by(id=jd_id, user_id=current_user.id).first_or_404()

    result = match_resume_to_jd(
        parsed_resume=resume.parsed or {},
        analyzed_jd=jd.analyzed or {},
        jd_raw_text=jd.raw_text or "",
    )

    return jsonify(result)