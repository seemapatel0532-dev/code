from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models.job_description import JobDescription
from app.services.jd_analysis_service import analyze_job_description

# ✅ Phase 4 JD module under /jds
jds_bp = Blueprint("jds", __name__, url_prefix="/jds")


@jds_bp.route("/")
@login_required
def jd_library():
    q = (request.args.get("q") or "").strip().lower()

    jds = JobDescription.query.filter_by(user_id=current_user.id).order_by(JobDescription.created_at.desc()).all()

    if q:
        # simple in-memory filter (fast enough for small/medium)
        def match(jd: JobDescription) -> bool:
            t = (jd.title or "").lower()
            r = ((jd.analyzed or {}).get("role", {}).get("role") or "").lower()
            skills = " ".join(((jd.analyzed or {}).get("skills", {}).get("skills") or []))
            return (q in t) or (q in r) or (q in skills.lower())

        jds = [x for x in jds if match(x)]

    return render_template("jds/list.html", page_title="JD Library", jds=jds, q=q)


@jds_bp.route("/new", methods=["GET", "POST"])
@login_required
def jd_new():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        company = (request.form.get("company") or "").strip() or None
        location = (request.form.get("location") or "").strip() or None
        raw_text = (request.form.get("raw_text") or "").strip()

        if not raw_text:
            flash("Job Description text is required.", "warning")
            return redirect(url_for("jds.jd_new"))

        analyzed = analyze_job_description(title=title, raw_text=raw_text)

        jd = JobDescription(
            user_id=current_user.id,
            title=analyzed.get("title") or "Untitled JD",
            company=company,
            location=location,
            raw_text=raw_text,
            analyzed=analyzed,
        )
        db.session.add(jd)
        db.session.commit()

        flash("JD saved and analyzed ✅", "success")
        return redirect(url_for("jds.jd_detail", jd_id=jd.id))

    return render_template("jds/new.html", page_title="Add Job Description")


@jds_bp.route("/<int:jd_id>")
@login_required
def jd_detail(jd_id: int):
    jd = JobDescription.query.filter_by(id=jd_id, user_id=current_user.id).first_or_404()
    analyzed = jd.analyzed or {}
    return render_template(
        "jds/detail.html",
        page_title="JD Detail",
        jd=jd,
        analyzed=analyzed,
    )


@jds_bp.route("/<int:jd_id>/delete", methods=["POST"])
@login_required
def jd_delete(jd_id: int):
    jd = JobDescription.query.filter_by(id=jd_id, user_id=current_user.id).first_or_404()
    db.session.delete(jd)
    db.session.commit()
    flash("JD deleted.", "success")
    return redirect(url_for("jds.jd_library"))