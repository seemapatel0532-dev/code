import re
from typing import Any, Dict, List, Tuple

BULLET_RE = re.compile(r"^\s*(?:[-*•‣▪▫▶➤→]|(\d+[\.\)]))\s+")
URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)

SECTION_TARGETS = {
    "experience": {"weight": 22, "min_chars": 250},
    "skills": {"weight": 18, "min_chars": 120},
    "education": {"weight": 15, "min_chars": 120},
    "projects": {"weight": 10, "min_chars": 120},
    "summary": {"weight": 5, "min_chars": 60},
    "certifications": {"weight": 5, "min_chars": 40},
    "achievements": {"weight": 5, "min_chars": 60},
}

BASELINE_KEYWORDS = {
    "experience", "project", "projects", "education", "skills", "summary",
    "responsible", "managed", "built", "designed", "developed", "implemented",
    "optimized", "improved", "analyzed", "collaborated", "led", "owned",
    "tested", "deployed", "maintained", "automated", "delivered",
    "stakeholders", "requirements", "documentation", "api", "apis",
    "database", "sql", "python", "java", "javascript", "html", "css",
    "flask", "django", "react", "node", "git", "linux", "cloud",
    "aws", "azure", "gcp", "docker", "kubernetes", "ci", "cd",
    "metrics", "kpi", "performance", "scalable", "security",
    "communication", "leadership", "problem", "solution",
}

STOPWORDS = set("""
a an the and or but if then else to of in on for with without at by from as is are was were be been being
this that these those it its i me my we our you your they their he she him her
""".split())


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _safe_text(parsed: Dict[str, Any]) -> str:
    return ((parsed or {}).get("clean_text") or "").strip()


def _sections(parsed: Dict[str, Any]) -> Dict[str, str]:
    secs = (parsed or {}).get("sections") or {}
    out = {}
    for k, v in secs.items():
        if isinstance(v, str):
            out[k.lower().strip()] = v.strip()
    return out


def _words(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9\+\#\.\-]{1,}", text.lower())


def _sentences(text: str) -> List[str]:
    s = re.split(r"[.!?\n]+", text)
    return [x.strip() for x in s if x.strip()]


def _score_section_completeness(sections: Dict[str, str]) -> Tuple[int, List[Dict[str, Any]]]:
    tips = []
    total_weight = sum(v["weight"] for v in SECTION_TARGETS.values())
    got = 0

    for key, cfg in SECTION_TARGETS.items():
        content = sections.get(key, "")
        if len(content) >= cfg["min_chars"]:
            got += cfg["weight"]
        else:
            if len(content) > 0:
                frac = _clamp(len(content) / cfg["min_chars"], 0.0, 1.0)
                got += int(round(cfg["weight"] * 0.55 * frac))
                tips.append({
                    "id": f"sec_{key}",
                    "severity": "medium",
                    "title": f"Expand your {key.title()} section",
                    "explanation": f"Your {key} section exists but looks short. ATS prefers clearer and more complete sections.",
                    "fix": f"Add 2–4 more bullet points to {key.title()} with tools + results.",
                    "copy_text": f"{key.title()}:\n• Improved X by Y% using Z.\n• Built/Owned feature A using tools B.\n• Measured results using metrics C."
                })
            else:
                tips.append({
                    "id": f"missing_{key}",
                    "severity": "high" if key in ("experience", "skills", "education") else "low",
                    "title": f"Add a {key.title()} section",
                    "explanation": f"ATS scoring improves when key sections are present with clear headings.",
                    "fix": f"Create heading '{key.title()}' and add ATS-friendly bullets.",
                    "copy_text": f"{key.title()}:\n• (Add 3–6 bullets)\n• Action verb + tools + measurable outcome"
                })

    score = int(round(100 * (got / total_weight)))
    return int(_clamp(score, 0, 100)), tips


def _score_formatting_safety(text: str) -> Tuple[int, List[Dict[str, Any]]]:
    tips = []
    score = 100

    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    if lines:
        long_lines = [ln for ln in lines if len(ln) >= 120]
        if len(long_lines) / max(1, len(lines)) > 0.15:
            score -= 18
            tips.append({
                "id": "fmt_long_lines",
                "severity": "medium",
                "title": "Avoid multi-column layouts",
                "explanation": "Multi-column resumes can scramble reading order in ATS parsing.",
                "fix": "Use a single-column layout and keep lines shorter.",
                "copy_text": "Layout tip: Use one column. Keep headings simple. Avoid text boxes and multi-column tables."
            })

    url_count = len(URL_RE.findall(text))
    if url_count >= 6:
        score -= 8
        tips.append({
            "id": "fmt_many_links",
            "severity": "low",
            "title": "Too many links",
            "explanation": "Many links add noise and reduce clarity for parsers.",
            "fix": "Keep 2–4 key links (LinkedIn, GitHub, Portfolio).",
            "copy_text": "Links: LinkedIn | GitHub | Portfolio"
        })

    return int(_clamp(score, 0, 100)), tips


def _flesch_reading_ease(text: str) -> float:
    words = re.findall(r"[A-Za-z]+", text)
    if not words:
        return 0.0
    sentences = _sentences(text)
    if not sentences:
        return 0.0

    def syllables(w: str) -> int:
        w = re.sub(r"[^a-z]", "", w.lower())
        if not w:
            return 0
        groups = re.findall(r"[aeiouy]+", w)
        s = len(groups)
        if w.endswith("e") and s > 1:
            s -= 1
        return max(1, s)

    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(syllables(w) for w in words)

    return 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)


def _score_readability(text: str) -> Tuple[int, List[Dict[str, Any]]]:
    tips = []
    fre = _flesch_reading_ease(text)
    score = int(_clamp((fre + 10) * 0.85, 0, 100))

    if score < 55:
        tips.append({
            "id": "readability",
            "severity": "medium",
            "title": "Improve readability",
            "explanation": "ATS and recruiters prefer short, clear bullet points.",
            "fix": "Shorten long sentences. Keep bullets around 8–20 words.",
            "copy_text": "Bullet format: Action verb + what you did + tools + measurable result."
        })

    return score, tips


def _score_keyword_coverage(text: str, job_description: str = "") -> Tuple[int, List[Dict[str, Any]], Dict[str, Any]]:
    tips = []

    token_set = set(_words(text))
    baseline = set(BASELINE_KEYWORDS)

    used_jd = False
    if job_description.strip():
        used_jd = True
        jd_tokens = [w for w in _words(job_description) if w not in STOPWORDS and len(w) >= 3]
        baseline = baseline.union(set(jd_tokens[:80]))

    hits = sorted(list(baseline.intersection(token_set)))
    coverage = len(hits) / max(1, len(baseline))
    score = int(_clamp(coverage * 140, 0, 100))

    if score < 60:
        tips.append({
            "id": "keywords_low",
            "severity": "high",
            "title": "Low keyword coverage",
            "explanation": "Your resume may be missing common ATS keywords and tools/skills terms.",
            "fix": "Add a Skills section and rewrite bullets using role keywords.",
            "copy_text": "Skills:\n• Python, SQL, Git, Linux\n• Flask/Django, REST APIs\n• Data analysis, automation"
        })

    meta = {
        "keyword_hits": hits[:60],
        "keyword_hits_count": len(hits),
        "keyword_target_count": len(baseline),
        "used_job_description": used_jd,
    }
    return score, tips, meta


def _score_bullet_structure(text: str) -> Tuple[int, List[Dict[str, Any]], Dict[str, Any]]:
    tips = []
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    bullet_lines = [ln for ln in lines if BULLET_RE.search(ln)]

    if not lines:
        return 0, [{
            "id": "empty",
            "severity": "high",
            "title": "Empty resume text",
            "explanation": "No readable text was extracted.",
            "fix": "Upload a text-based PDF/DOCX (not scanned images).",
            "copy_text": "Tip: Export resume as text-based PDF from Word/Google Docs."
        }], {"bullet_count": 0}

    bullet_ratio = len(bullet_lines) / len(lines)
    score = 100

    if bullet_ratio < 0.10:
        score -= 28
        tips.append({
            "id": "bullets_low",
            "severity": "high",
            "title": "Add more bullet points",
            "explanation": "Bullet points improve ATS scanning and clarity.",
            "fix": "Convert paragraphs into bullets (3–6 bullets per role).",
            "copy_text": "• Built X using Y\n• Improved metric by Z%\n• Automated process saving N hours/week"
        })
    elif bullet_ratio < 0.18:
        score -= 12
        tips.append({
            "id": "bullets_medium",
            "severity": "medium",
            "title": "Use bullets consistently",
            "explanation": "You have some bullets but should be more consistent in Experience/Projects.",
            "fix": "Use bullets for responsibilities and measurable outcomes.",
            "copy_text": "Experience:\n• Action verb + task + tools + impact"
        })

    bullet_word_counts = []
    for ln in bullet_lines:
        cleaned = BULLET_RE.sub("", ln).strip()
        wc = len(re.findall(r"[A-Za-z0-9]+", cleaned))
        bullet_word_counts.append(wc)

    if bullet_lines:
        too_short = sum(1 for wc in bullet_word_counts if wc <= 4)
        too_long = sum(1 for wc in bullet_word_counts if wc >= 28)

        if too_short / len(bullet_lines) > 0.25:
            score -= 10
            tips.append({
                "id": "bullets_too_short",
                "severity": "medium",
                "title": "Bullets are too short",
                "explanation": "Very short bullets miss tools/results, reducing ATS matches.",
                "fix": "Make bullets 8–20 words and include tools + outcome.",
                "copy_text": "• Built a Flask API to automate reporting, reducing manual work by 30%."
            })

        if too_long / len(bullet_lines) > 0.20:
            score -= 10
            tips.append({
                "id": "bullets_too_long",
                "severity": "medium",
                "title": "Bullets are too long",
                "explanation": "Long bullets reduce readability and hide keywords.",
                "fix": "Split long bullets into 2 bullets or remove extra clauses.",
                "copy_text": "• Designed X using Y.\n• Improved Z by N% using A/B testing."
            })

    meta = {
        "line_count": len(lines),
        "bullet_count": len(bullet_lines),
        "bullet_ratio": round(bullet_ratio, 3),
        "avg_bullet_words": round(sum(bullet_word_counts) / max(1, len(bullet_word_counts)), 2) if bullet_word_counts else 0,
    }
    return int(_clamp(score, 0, 100)), tips, meta


def generate_ats_report(parsed: Dict[str, Any], job_description: str = "") -> Dict[str, Any]:
    text = _safe_text(parsed)
    sections = _sections(parsed)

    sec_score, sec_tips = _score_section_completeness(sections)
    fmt_score, fmt_tips = _score_formatting_safety(text)
    read_score, read_tips = _score_readability(text)
    kw_score, kw_tips, kw_meta = _score_keyword_coverage(text, job_description=job_description)
    bullet_score, bullet_tips, bullet_meta = _score_bullet_structure(text)

    weights = {
        "section_completeness": 0.25,
        "formatting_safety": 0.20,
        "readability": 0.15,
        "keyword_coverage": 0.25,
        "bullet_structure": 0.15,
    }

    overall = (
        sec_score * weights["section_completeness"]
        + fmt_score * weights["formatting_safety"]
        + read_score * weights["readability"]
        + kw_score * weights["keyword_coverage"]
        + bullet_score * weights["bullet_structure"]
    )
    ats_score = int(round(_clamp(overall, 0, 100)))

    if ats_score >= 85:
        grade = "Excellent"
    elif ats_score >= 70:
        grade = "Good"
    elif ats_score >= 55:
        grade = "Average"
    else:
        grade = "Needs Work"

    all_tips = []
    seen = set()
    for arr in (sec_tips, fmt_tips, read_tips, kw_tips, bullet_tips):
        for t in arr:
            if t["id"] not in seen:
                seen.add(t["id"])
                all_tips.append(t)

    sev_rank = {"high": 0, "medium": 1, "low": 2}
    all_tips.sort(key=lambda x: (sev_rank.get(x.get("severity", "low"), 9), x.get("title", "")))

    breakdown = {
        "section_completeness": {
            "score": sec_score,
            "label": "Section Completeness",
            "explanation": "Checks whether key sections exist and have enough content."
        },
        "formatting_safety": {
            "score": fmt_score,
            "label": "Formatting Safety",
            "explanation": "Detects ATS-risky formatting (multi-column patterns, too many links, etc.)."
        },
        "readability": {
            "score": read_score,
            "label": "Readability Quality",
            "explanation": "Measures how easy your resume text is to scan using short, clear bullets."
        },
        "keyword_coverage": {
            "score": kw_score,
            "label": "Keyword Coverage",
            "explanation": "Matches common ATS keywords (and optional JD keywords) against your resume text."
        },
        "bullet_structure": {
            "score": bullet_score,
            "label": "Bullet Structure",
            "explanation": "Checks bullet usage, consistency, and bullet length quality."
        },
    }

    return {
        "ats_score": ats_score,
        "grade": grade,
        "breakdown": breakdown,
        "improvement_tips": all_tips[:14],
        "meta": {
            "text_length": len(text),
            "sections_found": sorted([k for k, v in sections.items() if v]),
            "keyword_meta": kw_meta,
            "bullet_meta": bullet_meta,
            "used_job_description": bool(job_description.strip()),
        },
    }