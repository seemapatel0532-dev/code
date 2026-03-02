import os
import uuid

from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.resume import Resume
from app.services.parsing_service import parse_resume

resume_bp = Blueprint("resumes", __name__, url_prefix="/resumes")

def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]

@resume_bp.route("/")
@login_required
def list_resumes():
    items = (
        Resume.query
        .filter_by(user_id=current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    )
    return render_template("resumes/list.html", page_title="My Resumes", resumes=items)

@resume_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload_resume():
    if request.method == "POST":
        if "resume" not in request.files:
            flash("No file part in request.", "danger")
            return redirect(url_for("resumes.upload_resume"))

        f = request.files["resume"]
        if not f or f.filename == "":
            flash("Please select a file.", "warning")
            return redirect(url_for("resumes.upload_resume"))

        if not allowed_file(f.filename):
            flash("Only PDF and DOCX are allowed.", "danger")
            return redirect(url_for("resumes.upload_resume"))

        original = f.filename
        safe = secure_filename(original)
        ext = safe.rsplit(".", 1)[1].lower()

        unique_name = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        save_path = os.path.join(upload_dir, unique_name)

        # Save file
        f.save(save_path)

        # File size
        size = os.path.getsize(save_path)

        # Parse
        try:
            parsed = parse_resume(save_path, ext)
        except Exception as e:
            # clean up file if parsing fails
            try:
                os.remove(save_path)
            except Exception:
                pass
            flash(f"Parsing failed: {str(e)}", "danger")
            return redirect(url_for("resumes.upload_resume"))

        # Save DB row
        resume = Resume(
            user_id=current_user.id,
            original_filename=original,
            stored_filename=unique_name,
            file_ext=ext,
            file_size=size,
            parsed=parsed,
        )
        db.session.add(resume)
        db.session.commit()

        flash("Resume uploaded & parsed successfully ✅", "success")
        return redirect(url_for("resumes.view_resume", resume_id=resume.id))

    return render_template("resumes/upload.html", page_title="Upload Resume")

@resume_bp.route("/<int:resume_id>")
@login_required
def view_resume(resume_id: int):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    parsed = resume.parsed or {}
    return render_template("resumes/view.html", page_title="Resume Analysis", resume=resume, parsed=parsed)

@resume_bp.route("/file/<int:resume_id>")
@login_required
def download_resume_file(resume_id: int):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        resume.stored_filename,
        as_attachment=True,
        download_name=resume.original_filename,
    )