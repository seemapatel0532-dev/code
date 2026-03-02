from __future__ import annotations

from datetime import datetime
from app.extensions import db


class BulkRankingRun(db.Model):
    __tablename__ = "bulk_ranking_runs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False, index=True)

    jd_id = db.Column(db.Integer, nullable=False, index=True)
    jd_title = db.Column(db.String(255), nullable=True)

    status = db.Column(db.String(30), nullable=False, default="queued")  # queued/running/done/failed
    error = db.Column(db.Text, nullable=True)

    total_files = db.Column(db.Integer, nullable=False, default=0)
    processed_files = db.Column(db.Integer, nullable=False, default=0)

    # results payload:
    # {
    #   "weights": {"match": 0.6, "ats": 0.4},
    #   "rows": [ {candidate...} ],
    #   "started_at": "...",
    #   "finished_at": "..."
    # }
    results = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)