import re
from typing import Dict, List, Tuple

STOPWORDS = set("""
a an the and or but if then else to of in on for with without at by from as is are was were be been being
this that these those it its i me my we our you your they their he she him her
""".split())

# Small but practical skills dictionary (expand anytime)
SKILL_KEYWORDS = {
    # Programming / Web
    "python", "java", "javascript", "typescript", "c++", "c", "go", "golang",
    "html", "css", "bootstrap", "react", "nextjs", "node", "express",
    "flask", "django", "fastapi",
    # Data
    "sql", "postgresql", "mysql", "sqlite", "mongodb", "redis",
    "pandas", "numpy", "matplotlib", "scikit-learn", "sklearn",
    "powerbi", "tableau", "excel",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "linux", "git",
    "ci/cd", "ci", "cd", "github actions", "jenkins",
    # Concepts
    "rest", "rest api", "apis", "microservices", "system design",
    "oauth", "jwt", "security", "testing", "unit testing", "pytest",
    "agile", "scrum",
}

ROLE_HINTS = {
    "data analyst": {"sql", "powerbi", "tableau", "excel", "dashboard", "reporting"},
    "data scientist": {"python", "scikit-learn", "ml", "machine learning", "statistics"},
    "backend developer": {"python", "java", "node", "flask", "django", "fastapi", "api", "rest"},
    "full stack developer": {"react", "node", "javascript", "html", "css", "api"},
    "devops engineer": {"docker", "kubernetes", "aws", "linux", "ci/cd"},
    "software engineer": {"git", "api", "testing", "design"},
}

EXPERIENCE_RE = re.compile(r"(\d{1,2})\s*(\+)?\s*(years?|yrs?)", re.IGNORECASE)


def _normalize(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9\+\#\.\-]{1,}", text.lower())


def _lines(text: str) -> List[str]:
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


def extract_experience(text: str) -> Dict:
    """
    Detects min/max years, based on patterns like:
      - 2 years
      - 3+ years
      - 5 yrs
    """
    years = []
    for m in EXPERIENCE_RE.finditer(text or ""):
        try:
            y = int(m.group(1))
            years.append(y)
        except:
            continue

    if not years:
        return {"min_years": None, "max_years": None, "raw_hits": []}

    return {
        "min_years": min(years),
        "max_years": max(years),
        "raw_hits": years[:12],
    }


def extract_skills(text: str) -> Dict:
    """
    Rule-based skill extraction:
    - scans for known skills in the raw text
    - marks 'critical' skills if they appear in lines containing required/must/mandatory
    """
    text_norm = (text or "").lower()
    found = set()

    # phrase matching (for multi-word skills)
    for s in SKILL_KEYWORDS:
        if " " in s:
            if s in text_norm:
                found.add(s)

    # token matching for single word skills
    toks = set(_tokens(text_norm))
    for s in SKILL_KEYWORDS:
        if " " not in s:
            if s in toks:
                found.add(s)

    # critical skills: required lines
    critical = set()
    required_markers = ("must", "required", "mandatory", "need", "strong", "essential")
    for ln in _lines(text_norm):
        if any(w in ln for w in required_markers):
            for s in list(found):
                if s in ln:
                    critical.add(s)

    # simple scoring: occurrences
    scores = {}
    for s in found:
        if " " in s:
            scores[s] = text_norm.count(s)
        else:
            scores[s] = len(re.findall(rf"\b{re.escape(s)}\b", text_norm))

    skills_sorted = sorted(found, key=lambda x: (-scores.get(x, 0), x))

    return {
        "skills": skills_sorted[:80],
        "skill_scores": {k: int(scores[k]) for k in skills_sorted[:80]},
        "critical_skills": sorted(list(critical))[:40],
    }


def identify_role(title: str, text: str, skills: List[str]) -> Dict:
    """
    Role detection:
    - prefer title keywords
    - else infer using skill overlap vs ROLE_HINTS
    """
    title_l = (title or "").lower()
    combined = (title_l + " " + (text or "").lower())

    # direct title match
    for role in ROLE_HINTS.keys():
        if role in title_l:
            return {"role": role.title(), "confidence": 0.92, "method": "title_match"}

    # infer by overlap
    skill_set = set(skills or [])
    best_role = None
    best_score = 0

    for role, hints in ROLE_HINTS.items():
        overlap = 0
        for h in hints:
            if " " in h:
                if h in combined:
                    overlap += 2
            else:
                if h in skill_set or re.search(rf"\b{re.escape(h)}\b", combined):
                    overlap += 1

        if overlap > best_score:
            best_score = overlap
            best_role = role

    if best_role and best_score >= 2:
        conf = min(0.90, 0.55 + best_score * 0.08)
        return {"role": best_role.title(), "confidence": round(conf, 2), "method": "skill_overlap"}

    return {"role": "General", "confidence": 0.40, "method": "fallback"}


def analyze_job_description(title: str, raw_text: str) -> Dict:
    raw_text = _normalize(raw_text)
    title = (title or "").strip() or "Untitled JD"

    sk = extract_skills(raw_text)
    exp = extract_experience(raw_text)
    role = identify_role(title=title, text=raw_text, skills=sk.get("skills", []))

    return {
        "title": title,
        "role": role,
        "experience": exp,
        "skills": sk,
        "stats": {
            "char_count": len(raw_text),
            "line_count": len(_lines(raw_text)),
            "word_count": len(_tokens(raw_text)),
        }
    }