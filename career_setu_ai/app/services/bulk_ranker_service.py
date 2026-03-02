from __future__ import annotations

import os
import uuid
import threading
from datetime import datetime
from typing import Dict, Any, List, Tuple

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.bulk_ranking import BulkRankingRun
from app.models.resume import Resume
from app.models.job_description import JobDescription

from app.services.parsing_service import parse_resume
from app.services.ats_scoring_service import generate_ats_report
from app.services.match_service import match_resume_to_jd


# In-memory registry of active worker threads (simple background tasks)
_ACTIVE_WORKERS: Dict[int, threading.Thread] = {}


def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)


def _weighted_score(match_score: int, ats_score: int, weights: Dict[str, float]) -> int:
    wm = _safe_float(weights.get("match", 0.6), 0.6)
    wa = _safe_float(weights.get("ats", 0.4), 0.4)
    total = wm + wa
    if total <= 0:
        wm, wa, total = 0.6, 0.4, 1.0
    wm /= total
    wa /= total
    s = wm * match_score + wa * ats_score
    return int(round(max(0.0, min(100.0, s))))


def create_bulk_run(user_id: int, jd_id: int, weights: Dict[str, float]) -> BulkRankingRun:
    jd = JobDescription.query.filter_by(id=jd_id, user_id=user_id).first()
    if not jd:
        raise ValueError("Invalid JD selected.")

    run = BulkRankingRun(
        user_id=user_id,
        jd_id=jd_id,
        jd_title=jd.title,
        status="queued",
        total_files=0,
        processed_files=0,
        results={
            "weights": {
                "match": _safe_float(weights.get("match", 0.6), 0.6),
                "ats": _safe_float(weights.get("ats", 0.4), 0.4),
            },
            "rows": [],
            "started_at": None,
            "finished_at": None,
        },
    )
    db.session.add(run)
    db.session.commit()
    return run


def save_uploaded_files(files, upload_dir: str, allowed_exts: set[str]) -> List[Tuple[str, str, int]]:
    """
    Returns list of tuples: (save_path, ext, size_bytes)
    """
    os.makedirs(upload_dir, exist_ok=True)
    saved: List[Tuple[str, str, int]] = []

    for f in files:
        if not f or not f.filename:
            continue
        safe = secure_filename(f.filename)
        if "." not in safe:
            continue
        ext = safe.rsplit(".", 1)[1].lower()
        if ext not in allowed_exts:
            continue

        unique_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(upload_dir, unique_name)
        f.save(save_path)
        size = os.path.getsize(save_path)
        saved.append((save_path, ext, size))

    return saved


def start_bulk_processing(run_id: int, user_id: int, upload_dir: str):
    """
    Starts a background worker thread for this run.
    """

    def worker():
        try:
            run = BulkRankingRun.query.filter_by(id=run_id, user_id=user_id).first()
            if not run:
                return

            jd = JobDescription.query.filter_by(id=run.jd_id, user_id=user_id).first()
            if not jd:
                run.status = "failed"
                run.error = "Job Description not found."
                db.session.commit()
                return

            weights = (run.results or {}).get("weights") or {"match": 0.6, "ats": 0.4}

            run.status = "running"
            run.results = {**(run.results or {}), "started_at": datetime.utcnow().isoformat()}
            db.session.commit()

            # Find files that were saved for this run in upload_dir by name marker in Resume rows OR on disk
            # We store as Resume rows (temporary resumes owned by user) for auditing and ability to view later.
            candidates = (
                Resume.query
                .filter_by(user_id=user_id)
                .order_by(Resume.uploaded_at.desc())
                .limit(5000)
                .all()
            )

            # But for the run we track run.temp_resume_ids inside results (added by routes)
            temp_ids = ((run.results or {}).get("temp_resume_ids") or [])
            temp_set = set(int(x) for x in temp_ids if str(x).isdigit())

            run_rows: List[Dict[str, Any]] = []
            processed = 0
            total = run.total_files or len(temp_set)

            for r in candidates:
                if r.id not in temp_set:
                    continue

                # ATS report (Phase 3)
                ats = generate_ats_report(parsed=(r.parsed or {}), job_description=(jd.raw_text or ""))
                ats_score = int(ats.get("ats_score") or 0)

                # Match report (Phase 5)
                match = match_resume_to_jd(
                    parsed_resume=(r.parsed or {}),
                    analyzed_jd=(jd.analyzed or {}),
                    jd_raw_text=(jd.raw_text or ""),
                )
                match_score = int(match.get("match_score") or 0)

                final_score = _weighted_score(match_score, ats_score, weights)

                row = {
                    "resume_id": r.id,
                    "candidate_name": ((r.parsed or {}).get("entities") or {}).get("emails", [""])[0] or "Candidate",
                    "file_name": r.original_filename,
                    "match_score": match_score,
                    "ats_score": ats_score,
                    "final_score": final_score,
                    "matched_skills": (match.get("matched_skills") or [])[:20],
                    "missing_skills": (match.get("missing_skills") or [])[:20],
                }
                run_rows.append(row)

                processed += 1
                run.processed_files = processed
                run.total_files = total
                run.results = {**(run.results or {}), "rows": run_rows}
                db.session.commit()

            # Sort final ranking
            run_rows.sort(key=lambda x: (x.get("final_score", 0), x.get("match_score", 0)), reverse=True)

            run.status = "done"
            run.results = {**(run.results or {}), "rows": run_rows, "finished_at": datetime.utcnow().isoformat()}
            db.session.commit()

        except Exception as e:
            run = BulkRankingRun.query.filter_by(id=run_id, user_id=user_id).first()
            if run:
                run.status = "failed"
                run.error = str(e)
                db.session.commit()

    t = threading.Thread(target=worker, daemon=True)
    _ACTIVE_WORKERS[run_id] = t
    t.start()


def add_temp_resume_row(user_id: int, original_filename: str, stored_filename: str, ext: str, size: int, parsed: Dict[str, Any]) -> Resume:
    r = Resume(
        user_id=user_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_ext=ext,
        file_size=size,
        parsed=parsed,
    )
    db.session.add(r)
    db.session.commit()
    return r


def parse_and_store_candidate_files(
    user_id: int,
    upload_dir: str,
    files_saved: List[Tuple[str, str, int]],
    original_names: List[str],
) -> List[int]:
    """
    Parse uploaded files, create Resume rows. Returns list of Resume IDs created.
    """
    created_ids: List[int] = []

    for idx, (path, ext, size) in enumerate(files_saved):
        original = original_names[idx] if idx < len(original_names) else os.path.basename(path)
        stored_filename = os.path.basename(path)

        parsed = parse_resume(path, ext)
        r = add_temp_resume_row(user_id, original, stored_filename, ext, size, parsed)
        created_ids.append(r.id)

    return created_ids