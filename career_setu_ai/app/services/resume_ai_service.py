from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


_SPACED_LETTERS_RE = re.compile(r"^(?:[A-Za-z]\s+){2,}[A-Za-z]$")


def _collapse_spaced_letters(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    if _SPACED_LETTERS_RE.match(s):
        return s.replace(" ", "")
    return s


def _norm_lines(text: str) -> List[str]:
    lines = []
    for ln in (text or "").splitlines():
        ln2 = _collapse_spaced_letters(ln).strip()
        if ln2:
            lines.append(ln2)
    return lines


def _first_nonempty(lines: List[str]) -> str:
    for ln in lines:
        if ln.strip():
            return ln.strip()
    return ""


def _extract_name(lines: List[str]) -> str:
    candidates: List[Tuple[int, str]] = []
    for i, ln in enumerate(lines[:80]):
        l = ln.strip()
        if len(l) < 6 or len(l) > 40:
            continue
        if any(ch.isdigit() for ch in l):
            continue
        letters = sum(1 for ch in l if ch.isalpha())
        if letters < 6:
            continue
        upper_ratio = sum(1 for ch in l if ch.isalpha() and ch.isupper()) / max(1, letters)
        if upper_ratio >= 0.60:
            candidates.append((i, l.title() if l.isupper() else l))

    for i, ln in enumerate(lines[-30:]):
        l = ln.strip()
        if 6 <= len(l) <= 40 and not any(ch.isdigit() for ch in l):
            letters = sum(1 for ch in l if ch.isalpha())
            if letters >= 6:
                upper_ratio = sum(1 for ch in l if ch.isalpha() and ch.isupper()) / max(1, letters)
                if upper_ratio >= 0.60:
                    candidates.append((1000 + i, l.title() if l.isupper() else l))

    if not candidates:
        return ""
    candidates.sort(key=lambda x: x[0])
    for _, name in candidates:
        if name.strip().lower() not in {"skills", "education", "projects", "project", "profile", "contact", "languages", "links"}:
            return name.strip()
    return candidates[0][1].strip()


def _smart_split_skills(text: str) -> List[str]:
    raw = (text or "").replace("/", ",").replace(";", ",")
    raw = re.sub(r"\b(Programming|Web Development|Database Management|Tools|Languages)\s*:\s*", "", raw, flags=re.I)
    parts = [p.strip() for p in re.split(r"[,\n]", raw) if p.strip()]
    seen = set()
    out = []
    for p in parts:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out[:40]


def _projects_from_text(lines: List[str]) -> List[Dict[str, Any]]:
    projs: List[Dict[str, Any]] = []
    title_re = re.compile(r"^(?P<name>.+?)\s*\((?P<tech>[^)]+)\)\s*$")

    i = 0
    while i < len(lines):
        m = title_re.match(lines[i])
        if m:
            name = m.group("name").strip()
            tech = m.group("tech").strip()
            bullets: List[str] = []
            j = i + 1
            buf: List[str] = []
            while j < len(lines):
                if title_re.match(lines[j]):
                    break
                if lines[j].strip().lower() in {"skills", "education", "projects", "project", "profile", "contact", "languages", "links"}:
                    break
                buf.append(lines[j])
                j += 1

            desc = " ".join(buf).strip()
            if desc:
                sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", desc) if s.strip()]
                if not sents:
                    sents = [desc]
                for s in sents[:4]:
                    bullets.append(_bulletize(s))

            projs.append({"name": name, "tech": tech, "bullets": bullets})
            i = j
            continue
        i += 1

    return projs[:10]


def _simple_section_split(lines: List[str]) -> Dict[str, str]:
    mapping = {
        "PROFILE": "summary",
        "SUMMARY": "summary",
        "OBJECTIVE": "summary",
        "SKILLS": "skills",
        "TECHNICALSKILLS": "skills",
        "EDUCATION": "education",
        "PROJECT": "projects",
        "PROJECTS": "projects",
        "LANGUAGES": "other",
        "LINKS": "other",
        "CONTACT": "other",
    }

    current = "other"
    buckets: Dict[str, List[str]] = {"summary": [], "skills": [], "education": [], "projects": [], "other": []}

    for ln in lines:
        up = ln.strip().upper().replace(" ", "")
        if up in {"CONTACTPROFILE", "PROFILECONTACT"}:
            current = "summary"
            continue

        if up in mapping:
            current = mapping[up]
            continue

        up2 = up.rstrip(":")
        if up2 in mapping:
            current = mapping[up2]
            continue

        buckets[current].append(ln)

    return {k: "\n".join(v).strip() for k, v in buckets.items()}


def _education_from_text(lines: List[str]) -> List[Dict[str, str]]:
    edu: List[Dict[str, str]] = []

    deg_re = re.compile(
        r"\b(Bachelor of [A-Za-z ]+|Master of [A-Za-z ]+|B\.?\s*Tech|M\.?\s*Tech|BCA|MCA)\b",
        flags=re.I,
    )
    inst_re = re.compile(r"\b(University|College|Institute|Central university)\b", flags=re.I)

    for i, ln in enumerate(lines):
        if deg_re.search(ln) or inst_re.search(ln):
            degree = ""
            institution = ""
            year = ""
            window = lines[max(0, i - 1): min(len(lines), i + 3)]
            block = " ".join(window)
            mdeg = deg_re.search(block)
            if mdeg:
                degree = mdeg.group(0).strip()
            inst_lines = [w for w in window if inst_re.search(w)]
            if inst_lines:
                institution = max(inst_lines, key=len).strip()
            myear = re.search(r"\b(19\d{2}|20\d{2})\b", block)
            if myear:
                year = myear.group(0)

            if degree or institution or year:
                edu.append({"degree": degree, "institution": institution, "year": year})

    seen = set()
    out = []
    for e in edu:
        key = (e.get("degree", "").lower(), e.get("institution", "").lower())
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out[:6]


def _bulletize(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(".")
    if re.match(r"^(Built|Developed|Created|Designed|Implemented|Optimized|Integrated|Automated|Deployed)\b", s, flags=re.I):
        return s
    return f"Developed {s[0].lower() + s[1:] if len(s) > 1 else s}"


def profile_from_parsed(parsed: Dict[str, Any]) -> Dict[str, Any]:
    parsed = parsed or {}
    clean_text = (parsed.get("clean_text") or "").strip()
    entities = parsed.get("entities") or {}
    sections = parsed.get("sections") or {}

    lines = _norm_lines(clean_text)
    fallback_sections = _simple_section_split(lines)

    def _bad_split(sec: Dict[str, str]) -> bool:
        has_project_title = any(re.search(r"\([^)]{1,20}\)$", ln) for ln in lines)
        if has_project_title and not (sec.get("projects") or "").strip():
            return True
        if (sec.get("education") or "").strip() and any(
            "(" in ln and ")" in ln and "system" in ln.lower()
            for ln in _norm_lines(sec.get("education") or "")
        ):
            return True
        return False

    if _bad_split(sections):
        sections = fallback_sections

    name = _extract_name(lines)
    email = _first_nonempty(entities.get("emails") or [])
    phone = _first_nonempty(entities.get("phones") or [])

    links = ""
    lnks = []
    lnks.extend(entities.get("linkedin") or [])
    lnks.extend(entities.get("github") or [])
    lnks.extend(entities.get("urls") or [])
    lnks = [x for x in lnks if x]
    if lnks:
        links = " | ".join(lnks[:2])

    skills = _smart_split_skills(sections.get("skills") or "")
    projects = _projects_from_text(_norm_lines(sections.get("projects") or ""))
    if not projects:
        projects = _projects_from_text(lines)

    education = _education_from_text(_norm_lines(sections.get("education") or ""))
    if not education:
        education = _education_from_text(lines)

    summary_text = (sections.get("summary") or "").strip()
    if summary_text:
        summary_lines = _norm_lines(summary_text)
        summary = " ".join(summary_lines[:3]).strip()
    else:
        skill_hint = ", ".join(skills[:6])
        edu_hint = education[0].get("degree") if education else ""
        parts = [
            "Entry-level software developer focused on building reliable web and desktop applications.",
            f"Skilled in {skill_hint}." if skill_hint else "",
            f"Education: {edu_hint}." if edu_hint else "",
        ]
        summary = " ".join([p for p in parts if p]).strip()

    experience: List[Dict[str, Any]] = []

    return {
        "personal": {"name": name or "", "email": email or "", "phone": phone or "", "links": links or ""},
        "summary": summary or "",
        "skills": skills or [],
        "education": education or [],
        "experience": experience,
        "projects": projects or [],
    }