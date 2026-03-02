from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from app.models.resume import Resume
from app.services.ats_scoring_service import generate_ats_report

scoring_bp = Blueprint("scoring", __name__, url_prefix="/scoring")


@scoring_bp.route("/report/<int:resume_id>")
@login_required
def ats_report_page(resume_id: int):
    """
    Phase 3 UI page: renders the ATS Report page.
    Data is fetched via JS from /scoring/api/report/<resume_id>
    """
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    return render_template(
        "scoring/report.html",
        page_title="ATS Score Report",
        resume=resume,
    )


@scoring_bp.route("/api/report/<int:resume_id>", methods=["GET", "POST"])
@login_required
def ats_report_api(resume_id: int):
    """
    Phase 3 API: returns JSON ATS report.
    - GET: compute ATS report without JD
    - POST: compute ATS report using optional JD keywords
    Body: { "job_description": "..." }
    """
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()

    job_desc = ""
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        job_desc = (payload.get("job_description") or "").strip()

    parsed = resume.parsed or {}
    report = generate_ats_report(parsed=parsed, job_description=job_desc)
    return jsonify(report)