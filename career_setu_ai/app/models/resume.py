from datetime import datetime
from app.extensions import db

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_ext = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, nullable=False, default=0)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Parsed intelligence stored as JSON
    parsed = db.Column(db.JSON, nullable=True)