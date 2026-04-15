import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import (
    VOL3_JSON, VOL4_JSON,
    VOL3_MD_PAGES, VOL4_MD_PAGES,
    NORMALIZED_VOL3, NORMALIZED_VOL4
)
from .models import SectionChunk


CLAUSE_REGEX = re.compile(r'\b(\d+(?:\.\d+)+)\b')
PAGE_FILE_REGEX = re.compile(r'page[-_ ]?(\d+)', re.IGNORECASE)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = text.replace("\ufeff", "")
    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_clause_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    m = CLAUSE_REGEX.search(text)
    return m.group(1) if m else None


def extract_heading_from_text(text: str) -> Optional[str]:
    if not text:
        return None

    lines = [ln.strip().strip("#").strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:12]:
        if len(ln) <= 180 and not re.fullmatch(r'\d+(?:\.\d+)+', ln):
            return ln
    return None


def build_keywords(text: str, heading: Optional[str] = None) -> List[str]:
    base = f"{heading or ''}\n{text or ''}".lower()
    patterns = [
        "drill pipe",
        "heavy weight drill pipe",
        "hwdp",
        "drill collar",
        "drill collars",
        "wash pipe",
        "bha",
        "stabilizer",
        "stabiliser",
        "ring gauge",
        "acceptance criteria",
        "used bha",
        "dimensional",
        "inspection",
        "connection",
        "g105",
        "s135",
        "x95",
        "e75",
        "nc23",
        "nc26",
        "nc31",
        "nc35",
        "nc38",
        "nc40",
        "nc44",
        "nc46",
        "nc50",
        "nc56",
        "reg",
        "fh",
        "nkdstj",
        "nk dstj",
        "hi torque",
        "ht",
        "xt",
        "extreme",
        "gpds",
        "double shoulder",
        "vx",
        "express",
        "uxt",
        "ugpd",
        "eis",
        "tm",
        "delta",
        "x-force",
        "cet",
    ]
    kws = set()
    for p in patterns:
        if p in base:
            kws.add(p)

    for m in re.finditer(r'\bNC\d+\b', text or "", flags=re.IGNORECASE):
        kws.add(m.group(0).upper())

    for m in re.finditer(r'\b\d+(?:\s+\d+/\d+)?\s*(?:"|in|inch)\b', text or "", flags=re.IGNORECASE):
        kws.add(m.group(0))

    return sorted(kws)


def parse_markdown_table(md_text: str) -> Optional[List[Dict[str, Any]]]:
    lines = [ln.rstrip() for ln in md_text.splitlines()]
    table_blocks = []
    current = []

    for ln in lines:
        if "|" in ln:
            current.append(ln)
        else:
            if len(current) >= 2:
                table_blocks.append(current)
            current = []

    if len(current) >= 2:
        table_blocks.append(current)

    if not table_blocks:
        return None

    for block in table_blocks:
        if len(block) < 2:
            continue

        header_line = block[0]
        sep_line = block[1]

        if "|" not in header_line or "|" not in sep_line:
            continue

        if not re.search(r'[-:| ]{3,}', sep_line):
            continue

        headers = [c.strip() for c in header_line.strip("|").split("|")]
        headers = [h if h else f"col_{i+1}" for i, h in enumerate(headers)]

        rows = []
        for ln in block[2:]:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) < len(headers):
                cells += [""] * (len(headers) - len(cells))
            elif len(cells) > len(headers):
                cells = cells[:len(headers)]
            if any(cells):
                rows.append({headers[i]: cells[i] for i in range(len(headers))})

        if rows:
            return rows

    return None


def split_into_sections(volume: str, page_number: int, text: str, source_type: str) -> List[SectionChunk]:
    text = clean_text(text)
    if not text:
        return []

    matches = list(CLAUSE_REGEX.finditer(text))
    md_table = parse_markdown_table(text)
    sections: List[SectionChunk] = []

    if len(matches) <= 1:
        heading = extract_heading_from_text(text)
        clause = extract_clause_from_text(text)
        sections.append(
            SectionChunk(
                volume=volume,
                page_number=page_number,
                clause=clause,
                heading=heading,
                text=text,
                keywords=build_keywords(text, heading),
                has_table=md_table is not None,
                table_data=md_table,
                raw_table=None,
                source_type=source_type
            )
        )
        return sections

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk_text = text[start:end].strip()
        clause = match.group(1)
        heading = extract_heading_from_text(chunk_text)

        sections.append(
            SectionChunk(
                volume=volume,
                page_number=page_number,
                clause=clause,
                heading=heading,
                text=chunk_text,
                keywords=build_keywords(chunk_text, heading),
                has_table=(md_table is not None and i == 0),
                table_data=md_table if i == 0 else None,
                raw_table=None,
                source_type=source_type
            )
        )

    if not sections:
        heading = extract_heading_from_text(text)
        clause = extract_clause_from_text(text)
        sections.append(
            SectionChunk(
                volume=volume,
                page_number=page_number,
                clause=clause,
                heading=heading,
                text=text,
                keywords=build_keywords(text, heading),
                has_table=md_table is not None,
                table_data=md_table,
                raw_table=None,
                source_type=source_type
            )
        )

    return sections


def extract_page_number_from_filename(path: Path) -> Optional[int]:
    m = PAGE_FILE_REGEX.search(path.name)
    if m:
        return int(m.group(1))
    return None


def read_text_file(path: Path) -> str:
    for enc in ["utf-8", "utf-8-sig", "latin-1"]:
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    return ""


def find_best_text_file_in_page_dir(page_dir: Path) -> Optional[Path]:
    if not page_dir.exists() or not page_dir.is_dir():
        return None

    for name in ["markdown.md", "header.md"]:
        candidate = page_dir / name
        if candidate.exists() and candidate.is_file():
            return candidate

    candidates = [p for p in page_dir.rglob("*") if p.is_file()]
    if not candidates:
        return None

    preferred_exts = [".md", ".markdown", ".txt", ""]
    for ext in preferred_exts:
        matches = [p for p in candidates if p.suffix.lower() == ext.lower()]
        if matches:
            matches = sorted(matches, key=lambda p: p.stat().st_size, reverse=True)
            return matches[0]

    candidates = sorted(candidates, key=lambda p: p.stat().st_size, reverse=True)
    return candidates[0]


def load_markdown_pages(volume: str, pages_dir: Path) -> List[SectionChunk]:
    if not pages_dir.exists():
        return []

    sections: List[SectionChunk] = []

    page_entries = [p for p in pages_dir.iterdir()]
    page_entries = sorted(page_entries, key=lambda p: extract_page_number_from_filename(p) or 999999)

    for entry in page_entries:
        page_num = extract_page_number_from_filename(entry)
        if page_num is None:
            continue

        text = ""

        if entry.is_file():
            text = read_text_file(entry)

        elif entry.is_dir():
            header_file = entry / "header.md"
            markdown_file = entry / "markdown.md"

            header_text = read_text_file(header_file) if header_file.exists() else ""
            markdown_text = read_text_file(markdown_file) if markdown_file.exists() else ""

            if markdown_text.strip():
                text = f"{header_text}\n\n{markdown_text}".strip()
            else:
                best_file = find_best_text_file_in_page_dir(entry)
                if best_file:
                    text = read_text_file(best_file)

        if not text.strip():
            continue

        sections.extend(split_into_sections(volume, page_num, text, source_type="markdown_page"))

    return sections


def load_json_file(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_table(table: Any) -> Optional[List[Dict[str, Any]]]:
    if not table:
        return None

    if isinstance(table, list) and table and isinstance(table[0], dict):
        return table

    if isinstance(table, list) and table and isinstance(table[0], list):
        rows = [[("" if c is None else str(c)).strip() for c in row] for row in table]
        rows = [r for r in rows if any(r)]
        if len(rows) < 2:
            return None

        headers = rows[0]
        headers = [h if h else f"col_{i+1}" for i, h in enumerate(headers)]
        out = []
        for row in rows[1:]:
            if len(row) < len(headers):
                row = row + [""] * (len(headers) - len(row))
            elif len(row) > len(headers):
                row = row[:len(headers)]
            out.append({headers[i]: row[i] for i in range(len(headers))})
        return out

    return None


def parse_page_entry(volume: str, page_entry: Dict[str, Any]) -> List[SectionChunk]:
    page_number = (
        page_entry.get("page_number")
        or page_entry.get("page")
        or page_entry.get("page_num")
        or page_entry.get("number")
        or 0
    )

    text = (
        page_entry.get("text")
        or page_entry.get("content")
        or page_entry.get("page_text")
        or ""
    )

    tables = page_entry.get("tables") or page_entry.get("table_data") or []
    table_data = normalize_table(tables[0]) if tables else None

    text = clean_text(text)
    if not text:
        return []

    sections = split_into_sections(volume, int(page_number), text, source_type="json")

    if table_data and sections:
        sections[0].has_table = True
        sections[0].table_data = table_data

    return sections


def load_json_sections(volume: str, path: Path) -> List[SectionChunk]:
    if not path.exists():
        return []

    data = load_json_file(path)
    page_entries = []

    if isinstance(data, list):
        page_entries = data
    elif isinstance(data, dict):
        if isinstance(data.get("pages"), list):
            page_entries = data["pages"]
        elif isinstance(data.get("content"), list):
            page_entries = data["content"]
        else:
            page_entries = [v for v in data.values() if isinstance(v, dict)]

    sections: List[SectionChunk] = []
    for entry in page_entries:
        if isinstance(entry, dict):
            sections.extend(parse_page_entry(volume, entry))

    return sections


def save_normalized(sections: List[SectionChunk], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([s.model_dump() for s in sections], f, ensure_ascii=False, indent=2)


def load_normalized(path: Path) -> List[SectionChunk]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [SectionChunk(**x) for x in data]


def load_or_build_indexes() -> Dict[str, List[SectionChunk]]:
    if NORMALIZED_VOL3.exists() and NORMALIZED_VOL4.exists():
        return {
            "vol3": load_normalized(NORMALIZED_VOL3),
            "vol4": load_normalized(NORMALIZED_VOL4),
        }

    vol3_sections = load_markdown_pages("vol3", VOL3_MD_PAGES)
    vol4_sections = load_markdown_pages("vol4", VOL4_MD_PAGES)

    if not vol3_sections:
        vol3_sections = load_json_sections("vol3", VOL3_JSON)

    if not vol4_sections:
        vol4_sections = load_json_sections("vol4", VOL4_JSON)

    save_normalized(vol3_sections, NORMALIZED_VOL3)
    save_normalized(vol4_sections, NORMALIZED_VOL4)

    return {
        "vol3": vol3_sections,
        "vol4": vol4_sections,
    }