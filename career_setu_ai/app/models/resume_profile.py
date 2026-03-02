from __future__ import annotations

from datetime import datetime
from app.extensions import db


class ResumeProfile(db.Model):
    __tablename__ = "resume_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)

    title = db.Column(db.String(255), nullable=False, default="My Resume Profile")

    # current working data
    profile_json = db.Column(db.JSON, nullable=False, default=dict)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResumeProfileVersion(db.Model):
    __tablename__ = "resume_profile_versions"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)

    label = db.Column(db.String(255), nullable=True)
    snapshot_json = db.Column(db.JSON, nullable=False, default=dict)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)