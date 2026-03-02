from __future__ import annotations

from typing import Any, Dict, List, Tuple

from flask import Blueprint, Response, jsonify, render_template, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.resume_profile import ResumeProfile, ResumeProfileVersion
from app.services.ai_writing_service import (
    ats_fix_suggestions,
    generate_cover_letter,
    generate_summary,
    skill_gap_roadmap,
    star_rewrites,
)
from app.services.cover_letter_export_service import build_cover_letter_docx, build_cover_letter_pdf


assistant_bp = Blueprint("assistant", __name__, url_prefix="/assistant")


def _default_profile() -> Dict[str, Any]:
    return {
        "personal": {"name": "", "email": "", "phone": "", "links": ""},
        "summary": "",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
    }


def _get_profile() -> ResumeProfile:
    prof = ResumeProfile.query.filter_by(user_id=current_user.id).first()
    if not prof:
        prof = ResumeProfile(user_id=current_user.id, title="My Resume Profile", profile_json=_default_profile())
        db.session.add(prof)
        db.session.commit()
    return prof


def _collect_bullets(profile_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return bullet list with stable ids for UI selection."""
    out: List[Dict[str, Any]] = []

    exp = (profile_json or {}).get("experience") or []
    for i, e in enumerate(exp):
        role = (e or {}).get("role") or "Experience"
        bullets = (e or {}).get("bullets") or []
        for j, b in enumerate(bullets):
            if not (b or "").strip():
                continue
            out.append(
                {
                    "id": f"exp:{i}:{j}",
                    "label": f"{role} • Bullet {j+1}",
                    "text": b,
                }
            )

    proj = (profile_json or {}).get("projects") or []
    for i, p in enumerate(proj):
        name = (p or {}).get("name") or "Project"
        bullets = (p or {}).get("bullets") or []
        for j, b in enumerate(bullets):
            if not (b or "").strip():
                continue
            out.append(
                {
                    "id": f"proj:{i}:{j}",
                    "label": f"{name} • Bullet {j+1}",
                    "text": b,
                }
            )
    return out


def _apply_bullet(profile_json: Dict[str, Any], bullet_id: str, new_text: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Apply rewritten bullet into profile_json. Returns (ok, msg, updated_json)."""
    new_text = (new_text or "").strip()
    if not new_text:
        return False, "New bullet text is empty.", profile_json

    parts = (bullet_id or "").split(":")
    if len(parts) != 3:
        return False, "Invalid bullet id.", profile_json

    kind, i_s, j_s = parts
    try:
        i = int(i_s)
        j = int(j_s)
    except Exception:
        return False, "Invalid bullet position.", profile_json

    pj = dict(profile_json or {})

    if kind == "exp":
        exp = list(pj.get("experience") or [])
        if i < 0 or i >= len(exp):
            return False, "Experience index out of range.", profile_json
        entry = dict(exp[i] or {})
        bullets = list(entry.get("bullets") or [])
        if j < 0 or j >= len(bullets):
            return False, "Bullet index out of range.", profile_json
        bullets[j] = new_text
        entry["bullets"] = bullets
        exp[i] = entry
        pj["experience"] = exp
        return True, "Applied to Experience bullet ✅", pj

    if kind == "proj":
        proj = list(pj.get("projects") or [])
        if i < 0 or i >= len(proj):
            return False, "Project index out of range.", profile_json
        entry = dict(proj[i] or {})
        bullets = list(entry.get("bullets") or [])
        if j < 0 or j >= len(bullets):
            return False, "Bullet index out of range.", profile_json
        bullets[j] = new_text
        entry["bullets"] = bullets
        proj[i] = entry
        pj["projects"] = proj
        return True, "Applied to Project bullet ✅", pj

    return False, "Unknown bullet type.", profile_json


@assistant_bp.route("/optimizer")
@login_required
def optimizer_page():
    prof = _get_profile()
    bullets = _collect_bullets(prof.profile_json or {})
    return render_template(
        "assistant/optimizer.html",
        page_title="Optimizer",
        profile=prof,
        bullets=bullets,
    )


@assistant_bp.route("/cover-letter")
@login_required
def cover_letter_page():
    prof = _get_profile()
    return render_template(
        "assistant/cover_letter.html",
        page_title="Cover Letter",
        profile=prof,
    )


# -----------------------------
# API endpoints (JSON)
# -----------------------------
@assistant_bp.route("/api/rewrite", methods=["POST"])
@login_required
def api_rewrite():
    data = request.get_json(force=True) or {}
    bullet = (data.get("bullet") or "").strip()
    jd_text = (data.get("jd_text") or "").strip()
    suggestions = star_rewrites(bullet, jd_text)
    return jsonify({"ok": True, "suggestions": suggestions})


@assistant_bp.route("/api/summary", methods=["POST"])
@login_required
def api_summary():
    data = request.get_json(force=True) or {}
    jd_text = (data.get("jd_text") or "").strip()
    prof = _get_profile()
    summary = generate_summary(prof.profile_json or {}, jd_text)
    return jsonify({"ok": True, "summary": summary})


@assistant_bp.route("/api/ats", methods=["POST"])
@login_required
def api_ats():
    data = request.get_json(force=True) or {}
    jd_text = (data.get("jd_text") or "").strip()
    prof = _get_profile()
    out = ats_fix_suggestions(prof.profile_json or {}, jd_text)
    return jsonify({"ok": True, **out})


@assistant_bp.route("/api/roadmap", methods=["POST"])
@login_required
def api_roadmap():
    data = request.get_json(force=True) or {}
    jd_text = (data.get("jd_text") or "").strip()
    prof = _get_profile()
    out = skill_gap_roadmap(prof.profile_json or {}, jd_text)
    return jsonify({"ok": True, **out})


@assistant_bp.route("/api/apply", methods=["POST"])
@login_required
def api_apply():
    data = request.get_json(force=True) or {}
    bullet_id = (data.get("bullet_id") or "").strip()
    new_text = (data.get("new_text") or "").strip()

    prof = _get_profile()
    ok, msg, updated = _apply_bullet(prof.profile_json or {}, bullet_id, new_text)
    if not ok:
        return jsonify({"ok": False, "message": msg}), 400

    prof.profile_json = updated
    db.session.commit()

    ver = ResumeProfileVersion(
        profile_id=prof.id,
        user_id=current_user.id,
        label=f"Optimizer applied {bullet_id}",
        snapshot_json=prof.profile_json,
    )
    db.session.add(ver)
    db.session.commit()

    return jsonify({"ok": True, "message": msg, "profile": prof.profile_json})


@assistant_bp.route("/api/cover-letter", methods=["POST"])
@login_required
def api_cover_letter():
    data = request.get_json(force=True) or {}
    jd_text = (data.get("jd_text") or "").strip()
    company = (data.get("company") or "").strip()
    role = (data.get("role") or "").strip()

    prof = _get_profile()
    letter = generate_cover_letter(prof.profile_json or {}, jd_text, company=company, role=role)
    return jsonify({"ok": True, "letter": letter})


# -----------------------------
# Cover letter downloads
# -----------------------------
@assistant_bp.route("/cover-letter/download/docx", methods=["POST"])
@login_required
def cover_letter_download_docx():
    company = (request.form.get("company") or "").strip()
    role = (request.form.get("role") or "").strip()
    jd_text = (request.form.get("jd_text") or "").strip()
    letter = (request.form.get("letter") or "").strip()

    prof = _get_profile()
    if not letter:
        letter = generate_cover_letter(prof.profile_json or {}, jd_text, company=company, role=role)

    blob = build_cover_letter_docx(prof.profile_json or {}, letter)
    return Response(
        blob,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=CareerSetu_CoverLetter.docx"},
    )


@assistant_bp.route("/cover-letter/download/pdf", methods=["POST"])
@login_required
def cover_letter_download_pdf():
    company = (request.form.get("company") or "").strip()
    role = (request.form.get("role") or "").strip()
    jd_text = (request.form.get("jd_text") or "").strip()
    letter = (request.form.get("letter") or "").strip()

    prof = _get_profile()
    if not letter:
        letter = generate_cover_letter(prof.profile_json or {}, jd_text, company=company, role=role)

    blob = build_cover_letter_pdf(prof.profile_json or {}, letter)
    return Response(
        blob,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=CareerSetu_CoverLetter.pdf"},
    )