from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------
# Normalization helpers
# -----------------------------

_ALIAS = {
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "nodejs": "node",
    "node.js": "node",
    "js": "javascript",
    "ts": "typescript",
    "postgres": "postgresql",
    "postgre": "postgresql",
    "restful": "rest",
    "restful api": "rest api",
}


def _norm_skill(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("_", " ").replace("/", " ").replace("-", "-")
    s = " ".join(s.split())
    return _ALIAS.get(s, s)


def _as_skill_set(skills: List[str] | None) -> Set[str]:
    out = set()
    for x in (skills or []):
        nx = _norm_skill(x)
        if nx:
            out.add(nx)
    return out


# -----------------------------
# Skill categories (UI filters)
# -----------------------------

CATEGORY_RULES: Dict[str, Set[str]] = {
    "Programming": {
        "python", "java", "javascript", "typescript", "c", "c++", "go", "golang",
        "html", "css", "bootstrap",
    },
    "Frameworks": {"flask", "django", "fastapi", "react", "nextjs", "node", "express"},
    "Data": {
        "sql", "postgresql", "mysql", "sqlite", "mongodb", "redis",
        "pandas", "numpy", "matplotlib", "scikit-learn",
        "tableau", "powerbi", "excel",
    },
    "Cloud & DevOps": {
        "aws", "azure", "gcp", "docker", "kubernetes", "linux", "git",
        "jenkins", "github actions", "ci", "cd", "ci/cd",
    },
    "APIs & Security": {"rest", "rest api", "apis", "oauth", "jwt", "security", "testing", "unit testing", "pytest"},
    "Process": {"agile", "scrum", "system design", "microservices"},
}


def categorize_skill(skill: str) -> str:
    s = _norm_skill(skill)
    for cat, rules in CATEGORY_RULES.items():
        if s in rules:
            return cat
    return "Other"


# -----------------------------
# Scoring components
# -----------------------------

def _skill_overlap_score(
    resume_skills: Set[str],
    jd_skills: Set[str],
    jd_critical: Set[str],
) -> Tuple[int, Dict[str, Any]]:
    if not jd_skills:
        return 0, {"overlap": 0, "target": 0, "critical_target": 0, "critical_overlap": 0}

    overlap = resume_skills.intersection(jd_skills)
    critical_overlap = resume_skills.intersection(jd_critical)

    # Weighted: critical skills matter more
    base = len(overlap) / max(1, len(jd_skills))
    crit = len(critical_overlap) / max(1, len(jd_critical)) if jd_critical else base

    score = int(round((base * 0.65 + crit * 0.35) * 100))

    meta = {
        "overlap": len(overlap),
        "target": len(jd_skills),
        "critical_target": len(jd_critical),
        "critical_overlap": len(critical_overlap),
    }
    return max(0, min(100, score)), meta


def _semantic_similarity_score(resume_text: str, jd_text: str) -> int:
    r = (resume_text or "").strip()
    j = (jd_text or "").strip()

    if not r or not j:
        return 0

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_features=5000,
    )

    X = vectorizer.fit_transform([r, j])
    sim = float(cosine_similarity(X[0:1], X[1:2])[0][0])

    return int(round(max(0.0, min(1.0, sim)) * 100))


def _role_fit_score(jd_role: str, resume_skills: Set[str], role_hints: Dict[str, Set[str]]) -> Tuple[int, Dict[str, Any]]:
    role_key = (jd_role or "general").strip().lower()
    hints = role_hints.get(role_key, set())

    if not hints:
        score = 60 if len(resume_skills) >= 6 else 45
        return score, {"role": jd_role, "hint_target": 0, "hint_overlap": 0}

    overlap = 0
    for h in hints:
        nh = _norm_skill(h)
        if nh in resume_skills:
            overlap += 1

    score = int(round((overlap / max(1, len(hints))) * 100))
    return max(0, min(100, score)), {"role": jd_role, "hint_target": len(hints), "hint_overlap": overlap}


# -----------------------------
# Public API
# -----------------------------

ROLE_HINTS_SIMPLE: Dict[str, Set[str]] = {
    "data analyst": {"sql", "powerbi", "tableau", "excel"},
    "data scientist": {"python", "scikit-learn", "statistics"},
    "backend developer": {"python", "java", "flask", "django", "fastapi", "rest"},
    "full stack developer": {"react", "node", "javascript", "html", "css", "rest"},
    "devops engineer": {"docker", "kubernetes", "aws", "linux", "ci/cd"},
    "software engineer": {"git", "testing", "api", "system design"},
    "general": set(),
}


def extract_resume_skills(parsed_resume: Dict[str, Any], jd_skill_universe: List[str] | None = None) -> List[str]:
    """
    Your resume parser stores sections + clean_text but not a dedicated skill list.
    So we do a practical extraction:
    - build candidates from JD skills + a small universal list
    - match them against resume text
    """
    sections = (parsed_resume or {}).get("sections") or {}
    text = "\n".join([
        (sections.get("skills") or ""),
        (sections.get("experience") or ""),
        (sections.get("projects") or ""),
        (parsed_resume or {}).get("clean_text") or "",
    ]).lower()

    candidates = set(_norm_skill(s) for s in (jd_skill_universe or []))
    candidates |= {
        "python", "java", "javascript", "typescript", "html", "css", "bootstrap",
        "sql", "postgresql", "mysql", "mongodb", "git", "linux",
        "flask", "django", "fastapi", "react", "node", "express",
        "docker", "kubernetes", "aws", "azure", "gcp",
        "pandas", "numpy", "matplotlib", "scikit-learn",
        "rest", "rest api", "apis", "pytest", "testing",
    }

    found = set()

    # Phrase match first
    for s in candidates:
        if " " in s and s in text:
            found.add(s)

    # Token-ish match for single words
    tokens = set([t.strip(".,:;()[]{}<>\"'`).") for t in text.replace("\n", " ").split()])
    for s in candidates:
        if " " not in s and s in tokens:
            found.add(s)

    return sorted(found)


def generate_recommendations(missing: List[str], critical_missing: List[str], jd_role: str) -> List[Dict[str, str]]:
    recs: List[Dict[str, str]] = []

    if critical_missing:
        top = critical_missing[:8]
        recs.append({
            "title": "Add critical skills first",
            "detail": "These are marked as required/mandatory in the JD. Add them to Skills + show proof in projects/experience.",
            "copy": "Missing critical skills: " + ", ".join(top),
        })

    if missing:
        top = missing[:10]
        recs.append({
            "title": "Close the skill gaps",
            "detail": "Add missing tools/keywords to your resume (only if you truly know them) and reflect them in bullets.",
            "copy": "Missing skills: " + ", ".join(top),
        })

    recs.append({
        "title": "Improve semantic match",
        "detail": "Rewrite bullets using the JD language: action verb + tool + result. ATS + semantic match both improve.",
        "copy": "Bullet template: Built/Developed X using Y, improving Z by N% (or saving N hours/week).",
    })

    if (jd_role or "").strip() and jd_role.lower() != "general":
        recs.append({
            "title": f"Role-fit focus: {jd_role}",
            "detail": "Add 1–2 projects that directly match the role. Recruiters want proof, not only keywords.",
            "copy": "Project template: Problem → Approach → Tools → Metrics → Outcome.",
        })

    return recs[:6]


def match_resume_to_jd(parsed_resume: Dict[str, Any], analyzed_jd: Dict[str, Any], jd_raw_text: str) -> Dict[str, Any]:
    analyzed_jd = analyzed_jd or {}

    jd_skills_list = ((analyzed_jd.get("skills") or {}).get("skills") or [])
    jd_critical_list = ((analyzed_jd.get("skills") or {}).get("critical_skills") or [])
    jd_role = (((analyzed_jd.get("role") or {}).get("role")) or "General")

    jd_skills = _as_skill_set(jd_skills_list)
    jd_critical = _as_skill_set(jd_critical_list)

    resume_skills_list = extract_resume_skills(parsed_resume, jd_skill_universe=jd_skills_list)
    resume_skills = _as_skill_set(resume_skills_list)

    skill_score, skill_meta = _skill_overlap_score(resume_skills, jd_skills, jd_critical)

    resume_text = (parsed_resume or {}).get("clean_text") or ""
    semantic_score = _semantic_similarity_score(resume_text, jd_raw_text or "")

    role_fit_score, role_meta = _role_fit_score(jd_role, resume_skills, ROLE_HINTS_SIMPLE)

    match_score = int(round(skill_score * 0.45 + semantic_score * 0.35 + role_fit_score * 0.20))
    match_score = max(0, min(100, match_score))

    matched = sorted(list(resume_skills.intersection(jd_skills)))
    missing = sorted(list(jd_skills.difference(resume_skills)))
    critical_missing = sorted(list(jd_critical.difference(resume_skills)))

    def to_badges(items: List[str]) -> List[Dict[str, str]]:
        return [{"name": x, "category": categorize_skill(x)} for x in items]

    recommendations = generate_recommendations(missing=missing, critical_missing=critical_missing, jd_role=jd_role)

    return {
        "match_score": match_score,
        "breakdown": {
            "skill_overlap": {"score": skill_score, **skill_meta},
            "semantic_similarity": {"score": semantic_score},
            "role_fit": {"score": role_fit_score, **role_meta},
        },
        "matched_skills": to_badges(matched),
        "missing_skills": to_badges(missing),
        "critical_missing": to_badges(critical_missing),
        "recommendations": recommendations,
        "meta": {
            "resume_skill_count": len(resume_skills),
            "jd_skill_count": len(jd_skills),
            "jd_role": jd_role,
        },
    }