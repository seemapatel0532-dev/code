from __future__ import annotations

import re
from typing import Any, Dict, List


# -----------------------------
# Lightweight “AI-like” writing helpers (no external API)
# -----------------------------

ACTION_VERBS = [
    "Built",
    "Developed",
    "Designed",
    "Implemented",
    "Optimized",
    "Automated",
    "Integrated",
    "Deployed",
    "Improved",
    "Analyzed",
]


def _safe_str(x: Any) -> str:
    return (x or "").strip()


def _extract_keywords(text: str) -> List[str]:
    """Very small keyword extractor (for ATS suggestions / skill gaps).

    NOTE: This is heuristic (no external LLM). It focuses on tech-like tokens.
    """

    text = _safe_str(text).lower()
    if not text:
        return []

    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+.#-]{1,30}", text)
    stop = {
        "and",
        "or",
        "the",
        "a",
        "an",
        "to",
        "of",
        "in",
        "for",
        "with",
        "on",
        "at",
        "by",
        "from",
        "as",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "this",
        "that",
        "you",
        "we",
        "our",
        "your",
        "their",
        "they",
        "it",
        "will",
        "can",
        "should",
        "must",
        "using",
        "use",
        "used",
        "work",
        "works",
        "working",
        "role",
        "responsibilities",
        "responsibility",
        "experience",
        "skills",
    }

    out: List[str] = []
    seen = set()
    for t in tokens:
        k = t.lower()
        if k in stop:
            continue
        if len(k) <= 2:
            continue
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out[:80]


def _pick_action_verb(bullet: str) -> str:
    bullet = _safe_str(bullet)
    if not bullet:
        return "Developed"
    first = bullet.split(" ", 1)[0].strip("-• ").capitalize()
    if first in ACTION_VERBS:
        return first
    return "Developed"


def star_rewrites(bullet: str, jd_text: str = "") -> List[str]:
    """Return 3 STAR-style rewrites (Situation/Task/Action/Result blended).

    These are templates + heuristics so you get consistent output without an API.
    """

    b = _safe_str(bullet)
    if not b:
        return []

    verb = _pick_action_verb(b)
    kws = _extract_keywords(jd_text)
    jd_hint = f" aligned with {kws[0]}" if kws else ""

    base = re.sub(r"^[-•]\s*", "", b).rstrip(".")
    metric = "(improved X by Y%)"
    metric2 = "(reduced time by Y%)"

    s1 = f"{verb} {base}{jd_hint}, owning requirements → implementation → validation {metric}."
    s2 = f"{verb} {base}{jd_hint} by building a clear pipeline, adding checks, and documenting outcomes {metric2}."
    s3 = f"{verb} {base}{jd_hint}; collaborated with stakeholders, resolved issues, and delivered measurable impact {metric}."

    return [re.sub(r"\s+", " ", x).strip() for x in [s1, s2, s3]]


def generate_summary(profile: Dict[str, Any], jd_text: str = "") -> str:
    personal = (profile or {}).get("personal", {}) or {}
    name = _safe_str(personal.get("name"))
    skills = (profile or {}).get("skills", []) or []
    projects = (profile or {}).get("projects", []) or []

    skill_hint = ", ".join([_safe_str(s) for s in skills if _safe_str(s)][:6])
    proj_hint = _safe_str(projects[0].get("name")) if projects else ""
    jd_kws = _extract_keywords(jd_text)
    jd_hint = ", ".join(jd_kws[:3]) if jd_kws else ""

    lines = [
        f"{name + ' — ' if name else ''}Software developer focused on building reliable, ATS-friendly applications and tools.",
    ]
    if skill_hint:
        lines.append(f"Strong in {skill_hint}.")
    if proj_hint:
        lines.append(f"Recent work includes {proj_hint} with measurable outcomes.")
    if jd_hint:
        lines.append(f"Targeting roles that require {jd_hint}.")

    return " ".join([x for x in lines if x]).strip()


def generate_cover_letter(profile: Dict[str, Any], jd_text: str, company: str = "", role: str = "") -> str:
    personal = (profile or {}).get("personal", {}) or {}
    name = _safe_str(personal.get("name")) or "Your Name"
    email = _safe_str(personal.get("email"))
    phone = _safe_str(personal.get("phone"))

    skills = (profile or {}).get("skills", []) or []
    skill_hint = ", ".join([_safe_str(s) for s in skills if _safe_str(s)][:8])

    projects = (profile or {}).get("projects", []) or []
    proj_lines = []
    for p in projects[:2]:
        pn = _safe_str(p.get("name"))
        tech = _safe_str(p.get("tech"))
        if pn:
            proj_lines.append(f"• {pn}{' (' + tech + ')' if tech else ''}")

    jd_kws = _extract_keywords(jd_text)
    jd_hint = ", ".join(jd_kws[:5])

    company = company or "your company"
    role = role or "this role"

    header = [name]
    if email or phone:
        header.append(" | ".join([x for x in [email, phone] if x]))

    body = f"""Dear Hiring Manager,

I’m writing to apply for {role} at {company}. I’m a developer who enjoys building clean, reliable systems and shipping features end-to-end.

My strongest skills include: {skill_hint or 'software development fundamentals, problem solving, and clean architecture'}. Based on the job description, I can contribute in areas like: {jd_hint or 'backend development, APIs, testing, and performance'}.

Highlights from my work:
{chr(10).join(proj_lines) if proj_lines else '• Built multiple projects showcasing strong fundamentals and practical implementation.'}

I’d love to share how I can help {company} deliver impact quickly. Thank you for your time and consideration.

Sincerely,
{name}
"""

    return "\n".join(header) + "\n\n" + body


def ats_fix_suggestions(profile: Dict[str, Any], jd_text: str) -> Dict[str, Any]:
    jd_kws = _extract_keywords(jd_text)

    parts: List[str] = []
    parts.append(_safe_str((profile or {}).get("summary")))
    parts.extend([_safe_str(s) for s in ((profile or {}).get("skills") or [])])
    for p in ((profile or {}).get("projects") or []):
        parts.append(_safe_str(p.get("name")))
        parts.append(_safe_str(p.get("tech")))
        parts.extend([_safe_str(b) for b in (p.get("bullets") or [])])
    for e in ((profile or {}).get("experience") or []):
        parts.append(_safe_str(e.get("role")))
        parts.append(_safe_str(e.get("company")))
        parts.extend([_safe_str(b) for b in (e.get("bullets") or [])])
    resume_text = " ".join([x for x in parts if x]).lower()

    missing: List[str] = []
    for kw in jd_kws[:40]:
        if kw.lower() not in resume_text:
            missing.append(kw)

    tips = []
    if missing:
        tips.append(
            {
                "title": "Add missing keywords (high impact)",
                "detail": "These appear in the JD but not in your resume. Add them naturally in Skills/Projects (only if true).",
                "items": missing[:12],
            }
        )
    tips.append(
        {
            "title": "Use strong action + outcome bullets",
            "detail": "Start bullets with a strong verb and add numbers (%, time saved, users, latency, accuracy).",
            "items": [
                "Built… (reduced X by Y%)",
                "Optimized… (improved X by Y%)",
                "Automated… (saved Y hours/week)",
            ],
        }
    )
    tips.append(
        {
            "title": "Keep structure ATS-safe",
            "detail": "Use standard headings (Summary, Skills, Experience, Projects, Education). Avoid complex layout tables in PDF.",
            "items": ["Single-column PDF", "Consistent headings", "Clickable email/links"],
        }
    )

    return {"missing_keywords": missing[:20], "tips": tips}


def skill_gap_roadmap(profile: Dict[str, Any], jd_text: str) -> Dict[str, Any]:
    jd_kws = _extract_keywords(jd_text)
    skills = [(_safe_str(s)).lower() for s in ((profile or {}).get("skills") or []) if _safe_str(s)]
    resume_skill_text = " ".join(skills)

    gaps: List[str] = []
    for kw in jd_kws:
        if kw.lower() not in resume_skill_text:
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.#-]{2,}$", kw):
                gaps.append(kw)
    gaps = gaps[:12]

    roadmap = []
    for i, g in enumerate(gaps[:8], start=1):
        roadmap.append(
            {
                "week": i,
                "skill": g,
                "plan": [
                    f"Learn fundamentals of {g} (docs + short notes)",
                    f"Build a mini-project using {g}",
                    "Add 1 resume bullet + 1 project line (truthful)",
                ],
            }
        )

    return {"gap_skills": gaps, "roadmap": roadmap}