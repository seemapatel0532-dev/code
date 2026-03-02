from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user

from app.extensions import db
from app.models.resume_profile import ResumeProfile, ResumeProfileVersion
from app.models.resume import Resume
from app.services.resume_builder_service import build_docx, build_pdf
from app.services.resume_ai_service import profile_from_parsed

builder_bp = Blueprint("builder", __name__, url_prefix="/builder")


def _default_profile():
    return {
        "personal": {"name": "", "email": "", "phone": "", "links": ""},
        "summary": "",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
    }


@builder_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # one profile per user (simple)
    profile = ResumeProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = ResumeProfile(user_id=current_user.id, title="My Resume Profile", profile_json=_default_profile())
        db.session.add(profile)
        db.session.commit()

    if request.method == "POST":
        # Personal
        personal = {
            "name": (request.form.get("name") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "phone": (request.form.get("phone") or "").strip(),
            "links": (request.form.get("links") or "").strip(),
        }
        summary = (request.form.get("summary") or "").strip()

        # Skills (comma separated)
        skills_raw = (request.form.get("skills") or "").strip()
        skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

        # Education (repeatable)
        edu = []
        edu_degree = request.form.getlist("edu_degree")
        edu_inst = request.form.getlist("edu_inst")
        edu_year = request.form.getlist("edu_year")
        for i in range(max(len(edu_degree), len(edu_inst), len(edu_year))):
            d = (edu_degree[i] if i < len(edu_degree) else "").strip()
            ins = (edu_inst[i] if i < len(edu_inst) else "").strip()
            y = (edu_year[i] if i < len(edu_year) else "").strip()
            if d or ins or y:
                edu.append({"degree": d, "institution": ins, "year": y})

        # Experience
        exp = []
        exp_role = request.form.getlist("exp_role")
        exp_company = request.form.getlist("exp_company")
        exp_duration = request.form.getlist("exp_duration")
        exp_bullets = request.form.getlist("exp_bullets")  # newline separated per item
        for i in range(max(len(exp_role), len(exp_company), len(exp_duration), len(exp_bullets))):
            r = (exp_role[i] if i < len(exp_role) else "").strip()
            c = (exp_company[i] if i < len(exp_company) else "").strip()
            du = (exp_duration[i] if i < len(exp_duration) else "").strip()
            braw = (exp_bullets[i] if i < len(exp_bullets) else "").strip()
            bullets = [x.strip() for x in braw.splitlines() if x.strip()]
            if r or c or du or bullets:
                exp.append({"role": r, "company": c, "duration": du, "bullets": bullets})

        # Projects
        projects = []
        p_name = request.form.getlist("proj_name")
        p_tech = request.form.getlist("proj_tech")
        p_bullets = request.form.getlist("proj_bullets")
        for i in range(max(len(p_name), len(p_tech), len(p_bullets))):
            n = (p_name[i] if i < len(p_name) else "").strip()
            t = (p_tech[i] if i < len(p_tech) else "").strip()
            braw = (p_bullets[i] if i < len(p_bullets) else "").strip()
            bullets = [x.strip() for x in braw.splitlines() if x.strip()]
            if n or t or bullets:
                projects.append({"name": n, "tech": t, "bullets": bullets})

        profile.profile_json = {
            "personal": personal,
            "summary": summary,
            "skills": skills,
            "education": edu,
            "experience": exp,
            "projects": projects,
        }
        db.session.commit()

        ver = ResumeProfileVersion(
            profile_id=profile.id,
            user_id=current_user.id,
            label="Saved",
            snapshot_json=profile.profile_json,
        )
        db.session.add(ver)
        db.session.commit()

        flash("Profile saved + version snapshot created ✅", "success")
        return redirect(url_for("builder.index"))

    versions = (
        ResumeProfileVersion.query
        .filter_by(profile_id=profile.id, user_id=current_user.id)
        .order_by(ResumeProfileVersion.created_at.desc())
        .limit(20)
        .all()
    )

    return render_template(
        "builder/index.html",
        page_title="Resume Builder",
        profile=profile,
        versions=versions,
    )


@builder_bp.route("/import/<int:resume_id>")
@login_required
def import_from_resume(resume_id: int):
    """Create/overwrite the user's builder profile using an uploaded resume's parsed content."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    parsed = resume.parsed or {}

    new_profile = profile_from_parsed(parsed)

    profile = ResumeProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = ResumeProfile(user_id=current_user.id, title="My Resume Profile", profile_json=new_profile)
        db.session.add(profile)
        db.session.commit()
    else:
        profile.profile_json = new_profile
        db.session.commit()

    ver = ResumeProfileVersion(
        profile_id=profile.id,
        user_id=current_user.id,
        label=f"Imported from {resume.original_filename}",
        snapshot_json=profile.profile_json,
    )
    db.session.add(ver)
    db.session.commit()

    flash("Imported your uploaded resume into Builder ✅ Now edit + export.", "success")
    return redirect(url_for("builder.index"))


@builder_bp.route("/view")
@login_required
def view():
    """Interactive HTML resume view (shareable + printable)."""
    profile = ResumeProfile.query.filter_by(user_id=current_user.id).first_or_404()
    embed = (request.args.get("embed") or "").strip() == "1"
    tpl = "builder/view_embed.html" if embed else "builder/view.html"
    return render_template(tpl, page_title="Interactive Resume", profile=profile)


@builder_bp.route("/export/docx")
@login_required
def export_docx():
    profile = ResumeProfile.query.filter_by(user_id=current_user.id).first_or_404()
    blob = build_docx(profile.profile_json or {})
    return Response(
        blob,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=CareerSetu_Resume.docx"},
    )


@builder_bp.route("/export/pdf")
@login_required
def export_pdf():
    profile = ResumeProfile.query.filter_by(user_id=current_user.id).first_or_404()
    blob = build_pdf(profile.profile_json or {})
    return Response(
        blob,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=CareerSetu_Resume.pdf"},
    )