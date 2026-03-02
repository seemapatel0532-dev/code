import re
from typing import Dict, Any, Tuple, List

import pdfplumber
from docx import Document

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"(\+?\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}"
)
URL_RE = re.compile(r"(https?://[^\s]+|www\.[^\s]+)", re.IGNORECASE)

SECTION_ALIASES = {
    "education": ["education", "academics", "academic background", "qualification", "qualifications"],
    "skills": ["skills", "technical skills", "core skills", "key skills", "tools", "technologies"],
    "experience": ["experience", "work experience", "employment", "professional experience", "internship", "internships"],
    "projects": ["projects", "personal projects", "academic projects", "project work"],
    "summary": ["summary", "profile", "objective", "about", "professional summary"],
    "certifications": ["certifications", "certificates", "licenses"],
}

# Some resumes use headings like: "C O N T A C T" or "P R O J E C T".
# We normalize such lines before running heading detection.
_SPACED_LETTERS_RE = re.compile(r"^(?:[A-Za-z]\s+){2,}[A-Za-z]$")


def _collapse_spaced_letters_line(line: str) -> str:
    """Collapse lines like 'C O N T A C T' -> 'CONTACT'."""
    if not line:
        return line
    s = line.strip()
    if _SPACED_LETTERS_RE.match(s):
        collapsed = s.replace(" ", "")
        # Some PDFs merge two sidebar headings into one line during extraction,
        # e.g. "C O N T A C T P R O F I L E" -> "CONTACTPROFILE".
        # In that case, prefer "PROFILE" so summary/objective is detected.
        if collapsed.upper() in {"CONTACTPROFILE", "PROFILECONTACT"}:
            return "PROFILE"
        return collapsed
    return line


def _normalize_heading_lines(text: str) -> str:
    if not text:
        return ""
    out_lines: List[str] = []
    for ln in text.splitlines():
        out_lines.append(_collapse_spaced_letters_line(ln))
    return "\n".join(out_lines)


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = _normalize_heading_lines(text)
    # normalize bullet symbols
    text = text.replace("•", "- ").replace("●", "- ").replace("◦", "- ")
    # collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_entities(text: str) -> Dict[str, Any]:
    emails = list(dict.fromkeys(EMAIL_RE.findall(text)))
    phones = list(dict.fromkeys([m.group(0) for m in PHONE_RE.finditer(text)]))
    urls = list(dict.fromkeys(URL_RE.findall(text)))

    # Try to find LinkedIn/GitHub specifically
    linkedin = [u for u in urls if "linkedin.com" in u.lower()]
    github = [u for u in urls if "github.com" in u.lower()]

    return {
        "emails": emails[:5],
        "phones": phones[:5],
        "urls": urls[:10],
        "linkedin": linkedin[:3],
        "github": github[:3],
    }


def _find_heading_positions(text: str) -> List[Tuple[int, str]]:
    """
    Return list of (index, section_key) positions where a heading is found.
    """
    positions: List[Tuple[int, str]] = []
    lowered = text.lower()

    # Build regex for each alias as "line that is just the heading"
    for key, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            # heading must appear on its own line (common in resumes)
            pattern = re.compile(rf"(?m)^\s*{re.escape(alias)}\s*:?\s*$", re.IGNORECASE)
            for m in pattern.finditer(lowered):
                positions.append((m.start(), key))

    positions.sort(key=lambda x: x[0])
    return positions


def _split_sections(text: str) -> Dict[str, str]:
    sections = {k: "" for k in ["summary", "skills", "experience", "education", "projects", "certifications", "other"]}

    positions = _find_heading_positions(text)
    if not positions:
        sections["other"] = text
        return sections

    for i, (start, key) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        chunk = text[start:end].strip()

        # Remove the heading line itself
        chunk = re.sub(r"(?m)^\s*[A-Za-z ].{0,40}\s*:?\s*$", "", chunk, count=1).strip()

        if sections.get(key):
            sections[key] += "\n\n" + chunk
        else:
            sections[key] = chunk

    # Anything before the first heading goes to summary
    first_start, _ = positions[0]
    pre = text[:first_start].strip()
    if pre:
        sections["summary"] = (pre + "\n\n" + sections["summary"]).strip() if sections["summary"] else pre

    return sections


def _quality_badge(clean_text: str, sections: Dict[str, str]) -> Dict[str, str]:
    length = len(clean_text)
    filled = sum(1 for k in ["skills", "experience", "education", "projects"] if sections.get(k, "").strip())

    if length >= 800 and filled >= 2:
        return {"label": "Good", "class": "bg-success-subtle text-success border border-success-subtle"}
    if length >= 300:
        return {"label": "Okay", "class": "bg-warning-subtle text-warning border border-warning-subtle"}
    return {"label": "Poor", "class": "bg-danger-subtle text-danger border border-danger-subtle"}


def extract_text_from_pdf(path: str) -> str:
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t:
                texts.append(t)
    return "\n".join(texts)


def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    parts = []
    for p in doc.paragraphs:
        if p.text and p.text.strip():
            parts.append(p.text)
    return "\n".join(parts)


def parse_resume(path: str, ext: str) -> Dict[str, Any]:
    """
    Returns structured resume intelligence:
    - clean_text
    - entities
    - sections
    - quality badge
    """
    ext = ext.lower().lstrip(".")
    if ext == "pdf":
        raw = extract_text_from_pdf(path)
    elif ext == "docx":
        raw = extract_text_from_docx(path)
    else:
        raise ValueError("Unsupported file type")

    clean = _clean_text(raw)
    entities = _extract_entities(clean)
    sections = _split_sections(clean)
    quality = _quality_badge(clean, sections)

    return {
        "clean_text": clean,
        "entities": entities,
        "sections": sections,
        "quality": quality,
        "stats": {
            "text_length": len(clean),
            "lines": clean.count("\n") + 1 if clean else 0,
        },
    }