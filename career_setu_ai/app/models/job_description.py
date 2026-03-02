from datetime import datetime
from app.extensions import db


class JobDescription(db.Model):
    __tablename__ = "job_descriptions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    title = db.Column(db.String(180), nullable=False, default="Untitled JD")
    company = db.Column(db.String(140), nullable=True)
    location = db.Column(db.String(140), nullable=True)

    raw_text = db.Column(db.Text, nullable=False)
    analyzed = db.Column(db.JSON, nullable=True)  # structured JD JSON (skills/role/experience/etc)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)