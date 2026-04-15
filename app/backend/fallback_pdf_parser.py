import re
from pathlib import Path
from typing import List, Dict, Any

import pdfplumber

from .models import SectionChunk
from .config import VOL3_PDF, VOL4_PDF
from .loaders import clean_text, extract_clause_from_text, extract_heading_from_text, build_keywords, normalize_table


def parse_pdf_to_sections(volume: str, pdf_path: Path) -> List[SectionChunk]:
    sections: List[SectionChunk] = []
    if not pdf_path.exists():
        return sections

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = clean_text(page.extract_text() or "")
            heading = extract_heading_from_text(text)
            clause = extract_clause_from_text(text)

            tables = page.extract_tables() or []
            table_data = None
            raw_table = None
            for t in tables:
                norm = normalize_table(t)
                if norm:
                    table_data = norm
                    raw_table = t
                    break

            sections.append(
                SectionChunk(
                    volume=volume,
                    page_number=page_num,
                    clause=clause,
                    heading=heading,
                    text=text,
                    keywords=build_keywords(text, heading),
                    has_table=table_data is not None,
                    table_data=table_data,
                    raw_table=raw_table,
                    source_type="pdf_fallback"
                )
            )
    return sections


def build_fallback_indexes():
    return {
        "vol3": parse_pdf_to_sections("vol3", VOL3_PDF),
        "vol4": parse_pdf_to_sections("vol4", VOL4_PDF),
    }