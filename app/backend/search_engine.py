from typing import Dict, List, Optional
from fractions import Fraction
import re
import pandas as pd
from rapidfuzz import fuzz

from .models import SearchRequest, SearchResponse, SearchResult, SectionChunk
from .config import VOL3_PDF, VOL4_PDF

# Compacted dictionaries to save output space
DRILL_PIPE_CONNECTION_ALIASES = {
    "nc23":"api", "nc26":"api", "nc31":"api", "nc35":"api", "nc38":"api", "nc40":"api", "nc44":"api", "nc46":"api", "nc50":"api", "nc56":"api",
    "6 5/8 reg":"api", "7 5/8 reg":"api", "5 1/2 fh":"api", "6 5/8 fh":"api",
    "ht":"ht", "hi torque":"ht", "grant prideco hi torque":"ht",
    "xt":"xt", "extreme":"xt", "xtreme":"xt", "grant prideco extreme":"xt", "grant prideco xtreme":"xt",
    "xt-m":"xtm", "xt m":"xtm", "extreme-m":"xtm", "extreme m":"xtm", "grant prideco extreme torque-m":"xtm",
    "gpds":"gpds", "double shoulder":"gpds", "grant prideco double shoulder":"gpds",
    "turbotorque":"turbotorque", "turbo torque":"turbotorque", "grant prideco turbotorque":"turbotorque",
    "turbotorque-m":"turbotorquem", "turbo torque-m":"turbotorquem", "turbo torque m":"turbotorquem", "grant prideco turbotorque-m":"turbotorquem",
    "uxt":"uxt", "u-xt":"uxt", "ugpd":"ugpd", "ugpds":"ugpd", "u g p d":"ugpd", "grant prideco ugpd":"ugpd", "grant prideco ugpds":"ugpd",
    "vx":"vx", "vam express":"vx", "express":"vx", "grant prideco express":"vx",
    "eis":"eis", "tm":"tm", "tm2":"tm", "delta":"delta", "x-force":"xforce", "x force":"xforce", "xforce":"xforce",
    "nkdstj":"nkdstj", "nk dstj":"nkdstj", "hlids":"hlids", "hlmt":"hlmt", "hlmtc":"hlmt", "hlst":"hlst", "hlist":"hlist",
    "hydril wedge thread":"hydril_wedge_thread", "wedge thread":"hydril_wedge_thread",
    "dpm-ds":"dpm_ds", "dpm ds":"dpm_ds", "dpm-mt":"dpm_mt", "dpm mt":"dpm_mt", "dpm-st":"dpm_st", "dpm st":"dpm_st",
    "dpm-hightorque":"dpm_hightorque", "dpm high torque":"dpm_hightorque", "cet":"cet", "command tubular cet":"cet",
}

NORMAL_DP_CONNECTION_TO_CLAUSE = {
    "api":"3.7.1", "ht":"3.7.2", "xt":"3.7.3", "xtm":"3.7.4", "gpds":"3.7.5", "turbotorque":"3.7.6", "turbotorquem":"3.7.7",
    "uxt":"3.7.8", "ugpd":"3.7.9", "vx":"3.7.10", "eis":"3.7.11", "tm":"3.7.12", "delta":"3.7.13", "xforce":"3.7.14",
    "nkdstj":"3.7.15", "hlids":"3.7.16", "hlmt":"3.7.17", "hlst":"3.7.18", "hlist":"3.7.19", "hydril_wedge_thread":"3.7.20",
    "dpm_ds":"3.7.21", "dpm_mt":"3.7.22", "dpm_st":"3.7.23", "dpm_hightorque":"3.7.24", "cet":"3.7.25",
}

TWDP_CONNECTION_TO_CLAUSE = {"api":"3.8.1", "ht":"3.8.2", "xt":"3.8.3", "turbotorque":"3.8.4", "turbotorquem":"3.8.5", "uxt":"3.8.6", "delta":"3.8.7"}
HWDP_CONNECTION_TO_CLAUSE = {"api":"3.10.1", "ht":"3.10.2", "xt":"3.10.3", "xtm":"3.10.4", "gpds":"3.10.5", "uxt":"3.10.6", "ugpd":"3.10.7", "delta":"3.10.8", "eis":"3.10.9", "vx":"3.10.10"}


def page_ref(volume: str, page_number: int) -> str:
    return f"{str(VOL3_PDF if volume == 'vol3' else VOL4_PDF)}#page={page_number}"


def markdown_from_table(table: List[dict]) -> Optional[str]:
    try:
        return pd.DataFrame(table).to_markdown(index=False) if table else None
    except Exception:
        return None


def normalize_text(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def simplify_token(s: Optional[str]) -> str:
    return re.sub(r'[^a-z0-9]+', '', normalize_text(s))


def matches_exact_dimension(dim: str, text: str) -> bool:
    if not dim or not text: return False
    clean_dim = dim.replace('"', '').strip()
    pattern = r'(?<!\d)' + re.escape(clean_dim) + r'(?!\.?\d|/)'
    return bool(re.search(pattern, text))


def parse_fractional_inches(value: Optional[str]) -> Optional[Fraction]:
    if not value: return None
    parts = value.strip().replace('"', "").split()
    try:
        if len(parts) == 1:
            return Fraction(parts[0]) if "/" in parts[0] else Fraction(int(parts[0]), 1)
        if len(parts) == 2:
            return Fraction(int(parts[0]), 1) + Fraction(parts[1])
    except Exception:
        pass
    return None


def format_fractional_inches(value: Fraction) -> str:
    whole = value.numerator // value.denominator
    frac = value - whole
    if frac == 0: return str(whole)
    frac_str = f"{frac.numerator}/{frac.denominator}"
    return frac_str if whole == 0 else f"{whole} {frac_str}"


def minus_quarter_inch(value: Optional[str]) -> Optional[str]:
    parsed = parse_fractional_inches(value)
    return format_fractional_inches(parsed - Fraction(1, 4)) if parsed and (parsed - Fraction(1, 4)) > 0 else None


def match_clause(candidate: Optional[str], target: str) -> bool:
    if not candidate or not target: return False
    c, t = candidate.strip(), target.strip()
    return c == t or c.startswith(t + ".")


class StandardSearchEngine:
    def __init__(self, indexes: Dict[str, List[SectionChunk]]):
        self.indexes = indexes

    def get_chunks(self, volume: str) -> List[SectionChunk]:
        if volume == "all":
            return self.indexes.get("vol3", []) + self.indexes.get("vol4", [])
        return self.indexes.get(volume, [])

    def text_of(self, chunk: SectionChunk) -> str:
        return f"{chunk.heading or ''}\n{chunk.text}\n{' '.join(chunk.keywords)}".lower()

    def interpreted_query(self, req: SearchRequest) -> str:
        parts = [req.search_mode]
        for v in [req.target_clause, req.component_type, req.size, req.weight_ppf, req.connection_type, req.grade, req.center_pad_od, req.query]:
            if v: parts.append(str(v))

        if req.search_mode == "hwdp_dimensional" and req.center_pad_od:
            if min_od := minus_quarter_inch(req.center_pad_od):
                parts.append(f"min_center_upset_od={min_od}")

        if getattr(req, "reduced_tsr", False): parts.append("reduced_tsr")
        if getattr(req, "twdp", False): parts.append("twdp")
        if req.used_bha_acceptance_only: parts.append("used_bha_acceptance_only")

        return " | ".join(parts)

    def front_matter_penalty(self, chunk: SectionChunk) -> float:
        text = self.text_of(chunk)
        penalty = -50 if chunk.page_number <= 20 else 0
        if any(x in text for x in ["reviewers and contributors", "authors", "copyright", "table of contents", "contents", "sponsor companies"]):
            penalty -= 25
        return penalty

    def normalize_connection_key(self, connection_type: Optional[str]) -> Optional[str]:
        if not connection_type: return None
        raw = normalize_text(connection_type)
        compact = simplify_token(connection_type)

        if raw in DRILL_PIPE_CONNECTION_ALIASES: return DRILL_PIPE_CONNECTION_ALIASES[raw]
        if compact in DRILL_PIPE_CONNECTION_ALIASES: return DRILL_PIPE_CONNECTION_ALIASES[compact]
        for k, v in DRILL_PIPE_CONNECTION_ALIASES.items():
            if simplify_token(k) == compact: return v
        if compact.startswith("nc") and compact[2:].isdigit(): return "api"
        return None

    def filter_match(self, chunk: SectionChunk, req: SearchRequest) -> bool:
        text = self.text_of(chunk)
        if req.search_mode in ["drill_pipe_dimensional", "hwdp_dimensional", "bha_acceptance"] and chunk.page_number < 20:
            return False
        if chunk.volume == "vol4" and req.search_mode in ["drill_pipe_dimensional", "hwdp_dimensional"]:
            return False

        if req.component_type:
            c = req.component_type.lower()
            if c == "drill pipe" and not any(x in text for x in ["drill pipe", "nwdp", "tool joint", "reduced tsr", "twdp"]): return False
            elif c == "hwdp" and not any(x in text for x in ["hwdp", "heavy weight drill pipe", "center pad", "center upset"]): return False
            elif c == "bha" and not any(x in text for x in ["bha", "stabilizer", "stabiliser", "specialty tools", "connection", "acceptance criteria"]): return False

        return True

    def mode_component_match(self, chunk: SectionChunk, req: SearchRequest) -> float:
        text = self.text_of(chunk)
        score = 0
        is_proprietary = req.connection_type and self.normalize_connection_key(req.connection_type) not in [None, "api"]

        if req.search_mode == "drill_pipe_dimensional":
            if getattr(req, "twdp", False):
                if chunk.volume == "vol3" and 152 <= chunk.page_number <= 188: score += 100
                if match_clause(chunk.clause, "3.8"): score += 100
                if any(x in text for x in ["twdp", "thick-walled", "thick walled"]): score += 50
            elif getattr(req, "reduced_tsr", False):
                if chunk.volume == "vol3" and 223 <= chunk.page_number <= 224: score += 100
                if match_clause(chunk.clause, "3.7.26"): score += 120
                if "reduced tsr" in text or "premium class" in text: score += 60
            else:
                if chunk.volume == "vol3" and 151 <= chunk.page_number <= 219: score += 80
                if match_clause(chunk.clause, "3.6.1"): score += 120
                if chunk.clause and (chunk.clause.startswith("3.6") or chunk.clause.startswith("3.7")): score += 60
                if not is_proprietary:
                    if match_clause(chunk.clause, "3.7.1"): score += 100
                    if "api" in text or "non-proprietary" in text: score += 40

        elif req.search_mode == "hwdp_dimensional":
            if chunk.volume == "vol3" and 248 <= chunk.page_number <= 253: score += 100
            if match_clause(chunk.clause, "3.10"): score += 120
            if "hwdp" in text or "heavy weight drill pipe" in text: score += 60
            if req.center_pad_od and req.center_pad_od.lower() in text: score += 40

        elif req.search_mode == "bha_acceptance":
            if chunk.volume == "vol3" and 234 <= chunk.page_number <= 247: score += 100
            if match_clause(chunk.clause, "3.9"): score += 100
            if chunk.volume == "vol4":
                score += 60 if any(x in text for x in ["motor", "jar", "mwd", "specialty"]) else -20

        return score

    def score(self, chunk: SectionChunk, req: SearchRequest) -> float:
        text = self.text_of(chunk)
        iq = self.interpreted_query(req).lower()
        q = (req.query or "").lower().strip()
        score = (fuzz.partial_ratio(iq, text) * 0.35) + (fuzz.token_set_ratio(iq, text) * 0.20) + self.mode_component_match(chunk, req)

        if getattr(req, "target_clause", None) and match_clause(chunk.clause, req.target_clause): score += 200

        if req.size:
            score += 25 if matches_exact_dimension(req.size, text) or req.size.lower() in text else 0

        if req.weight_ppf:
            w = normalize_text(req.weight_ppf)
            if w in text or (w + "0") in text or w.replace(".0", "") in text: score += 25

        if req.connection_type:
            ct_clean = simplify_token(req.connection_type)
            if ct_clean and ct_clean in simplify_token(text):
                score += 150 if req.search_mode == "bha_acceptance" else 40

        # FIX: Better scoring for custom proprietary grades (like V150, Z140)
        if req.grade:
            g = normalize_text(req.grade)
            if len(g) == 1:
                # Standard API Grade (E, X, G, S)
                if f" {g} " in f" {text} ": score += 20
            else:
                # Proprietary Grade (V150, CY104, etc.)
                if g in text or g.replace("-", "") in text: score += 20

        if req.center_pad_od and normalize_text(req.center_pad_od) in text: score += 35

        if req.search_mode == "free_text" and q:
            if chunk.clause and (q in chunk.clause.lower() or chunk.clause.lower() in q): score += 50
            if chunk.heading and q in chunk.heading.lower(): score += 40
            if any(kw in q for kw in ["table", "dimension", "data", "summary"]) and chunk.has_table: score += 40
            if any(kw in q for kw in ["procedure", "inspection", "criteria", "method", "setup"]):
                if "procedure" in text or "inspection" in text or "method" in text:
                    score += 30 + (10 if not chunk.has_table else 0)
            if q in text: score += 25

        if chunk.heading: score += 4
        if chunk.clause: score += 3
        score += self.front_matter_penalty(chunk)
        if len((chunk.text or "").strip()) < 80: score -= 8
        return score

    def choose_result_type(self, chunk: SectionChunk, req: SearchRequest) -> str:
        if req.search_mode in ["drill_pipe_dimensional", "hwdp_dimensional", "drill_collar_dimensional"]:
            return "table" if chunk.has_table else "reference"
        if req.search_mode == "bha_acceptance":
            return "table" if chunk.has_table else "text"
        if req.search_mode in ["bha_general", "free_text"]:
            q_lower = (req.query or "").lower()
            return "table" if chunk.has_table and (any(x in q_lower for x in ["table", "data", "dimensional", "dimensions"]) or len(chunk.text) < 300) else "text"
        return "reference"

    def row_matches_request(self, row: Dict[str, str], req: SearchRequest, is_connection_table: bool = False) -> bool:
        row_text = " | ".join(str(v) for v in row.values()).lower()
        checks = []

        if is_connection_table:
            if req.connection_type:
                conn_clean = simplify_token(req.connection_type)
                if conn_clean: checks.append(conn_clean in simplify_token(row_text))
        else:
            if req.size:
                checks.append(matches_exact_dimension(req.size, row_text) or req.size.lower() in row_text)
            if req.weight_ppf:
                w = normalize_text(req.weight_ppf)
                checks.append(w in row_text or w.replace(".0", "") in row_text)
            
            # FIX: Perfect routing for custom proprietary grades (e.g. V150 vs Standard S)
            if req.grade:
                g = normalize_text(req.grade)
                if len(g) == 1:
                    checks.append(f" {g} " in f" {row_text} " or f"| {g} |" in f" {row_text} ")
                else:
                    checks.append(g in row_text.replace("-", "").replace(" ", ""))

            if req.connection_type:
                conn_clean = simplify_token(req.connection_type)
                checks.append(conn_clean in simplify_token(row_text) if conn_clean else True)

        if req.center_pad_od:
            checks.append(normalize_text(req.center_pad_od) in row_text)

        required_checks = [c for c in checks]
        if not required_checks: return True

        passed = sum(1 for c in required_checks if c)
        
        threshold = len(required_checks) if is_connection_table else max(1, len(required_checks) - 1)
        return passed >= threshold

    def filter_table_rows(self, table_data: Optional[List[Dict[str, str]]], req: SearchRequest, is_connection_table: bool = False) -> Optional[List[Dict[str, str]]]:
        if not table_data: return None
        matched = [row for row in table_data if self.row_matches_request(row, req, is_connection_table)]
        return matched if matched else table_data

    def find_clause_chunks(self, clause: str, volume: str = "vol3", require_table: bool = True) -> List[SectionChunk]:
        chunks = self.indexes.get(volume, [])
        valid_chunks = [c for c in chunks if c.page_number >= 20 and (not require_table or c.has_table)]
        
        exact = [c for c in valid_chunks if match_clause(c.clause, clause)]
        if exact:
            exact.sort(key=lambda c: c.page_number)
            return exact

        fuzzy = [c for c in valid_chunks if clause in self.text_of(c)]
        if fuzzy:
            fuzzy.sort(key=lambda c: c.page_number)
            return fuzzy

        return []

    def build_clause_result(self, chunk: SectionChunk, req: SearchRequest, score: float = 100.0, is_conn_table: bool = False) -> SearchResult:
        filtered_table = self.filter_table_rows(chunk.table_data, req, is_conn_table) if chunk.table_data else None

        if filtered_table:
            return SearchResult(
                result_type="table", volume=chunk.volume, page_number=chunk.page_number, clause=chunk.clause, heading=chunk.heading,
                table=filtered_table, markdown_table=markdown_from_table(filtered_table), confidence=round(score, 2),
                notes="Clause-routed table result.", source_type=chunk.source_type, page_ref=page_ref(chunk.volume, chunk.page_number),
            )

        if chunk.has_table and chunk.table_data:
            return SearchResult(
                result_type="table", volume=chunk.volume, page_number=chunk.page_number, clause=chunk.clause, heading=chunk.heading,
                table=chunk.table_data, markdown_table=markdown_from_table(chunk.table_data), confidence=round(score, 2),
                notes="Clause-routed table. No exact row match found.", source_type=chunk.source_type, page_ref=page_ref(chunk.volume, chunk.page_number),
            )

        return SearchResult(
            result_type="reference", volume=chunk.volume, page_number=chunk.page_number, clause=chunk.clause, heading=chunk.heading,
            confidence=round(score, 2), notes="Clause-routed reference.", source_type=chunk.source_type, page_ref=page_ref(chunk.volume, chunk.page_number),
        )

    def build_clause_results_for_chunks(self, chunks: List[SectionChunk], req: SearchRequest, score: float, is_conn_table: bool = False) -> List[SearchResult]:
        if not chunks: return []
        
        matched_results = []
        for chunk in chunks:
            if chunk.table_data:
                matched_rows = [row for row in chunk.table_data if self.row_matches_request(row, req, is_conn_table)]
                if matched_rows:
                    matched_results.append(SearchResult(
                        result_type="table", volume=chunk.volume, page_number=chunk.page_number, clause=chunk.clause, heading=chunk.heading,
                        table=matched_rows, markdown_table=markdown_from_table(matched_rows), confidence=round(score, 2),
                        notes="Direct multi-page row match.", source_type=chunk.source_type, page_ref=page_ref(chunk.volume, chunk.page_number),
                    ))
        
        if matched_results: return matched_results
        return [self.build_clause_result(chunk, req, score, is_conn_table) for chunk in chunks]

    def build_result(self, chunk: SectionChunk, req: SearchRequest, score: float) -> SearchResult:
        rtype = self.choose_result_type(chunk, req)
        is_conn_table = chunk.clause and ("3.7." in chunk.clause or "3.8." in chunk.clause)

        if rtype == "table" and chunk.table_data:
            filtered_table = self.filter_table_rows(chunk.table_data, req, is_conn_table)
            return SearchResult(
                result_type="table", volume=chunk.volume, page_number=chunk.page_number, clause=chunk.clause, heading=chunk.heading,
                table=filtered_table, markdown_table=markdown_from_table(filtered_table), confidence=round(score, 2),
                notes="Extracted table.", source_type=chunk.source_type, page_ref=page_ref(chunk.volume, chunk.page_number),
            )

        if rtype == "text":
            return SearchResult(
                result_type="text", volume=chunk.volume, page_number=chunk.page_number, clause=chunk.clause, heading=chunk.heading,
                text=(chunk.text or "")[:5000], confidence=round(score, 2), notes="Extracted text.",
                source_type=chunk.source_type, page_ref=page_ref(chunk.volume, chunk.page_number),
            )

        return SearchResult(
            result_type="reference", volume=chunk.volume, page_number=chunk.page_number, clause=chunk.clause, heading=chunk.heading,
            confidence=round(score, 2), notes="Reference returned.", source_type=chunk.source_type, page_ref=page_ref(chunk.volume, chunk.page_number),
        )

    def validate_request(self, req: SearchRequest) -> Optional[str]:
        if req.search_mode == "drill_pipe_dimensional":
            missing = [x for x, val in [("Size", req.size), ("Connection Type", req.connection_type)] if not val]
            if missing: return f"Need {', '.join(missing)} for Drill Pipe search."
            if getattr(req, "reduced_tsr", False) and getattr(req, "twdp", False): return "Select Reduced TSR or TWDP, not both."
        elif req.search_mode == "hwdp_dimensional":
            missing = [x for x, val in [("Size", req.size), ("Connection Type", req.connection_type), ("Center Pad OD", req.center_pad_od)] if not val]
            if missing: return f"Need {', '.join(missing)} for HWDP search."
        return None

    def drill_pipe_clause_results(self, req: SearchRequest) -> Optional[List[SearchResult]]:
        if req.search_mode != "drill_pipe_dimensional": return None

        if getattr(req, "reduced_tsr", False):
            chunks = self.find_clause_chunks("3.7.26", volume="vol3", require_table=True)
            return self.build_clause_results_for_chunks(chunks, req, score=250.0, is_conn_table=True) or None

        conn_key = self.normalize_connection_key(req.connection_type)
        if getattr(req, "twdp", False):
            tube_clause, conn_clause = "3.6.2", TWDP_CONNECTION_TO_CLAUSE.get(conn_key or "api", "3.8.1")
        else:
            tube_clause, conn_clause = "3.6.1", NORMAL_DP_CONNECTION_TO_CLAUSE.get(conn_key or "api", "3.7.1")

        results = []
        tube_chunks = self.find_clause_chunks(tube_clause, volume="vol3", require_table=True)
        results.extend(self.build_clause_results_for_chunks(tube_chunks, req, score=240.0, is_conn_table=False))

        conn_chunks = self.find_clause_chunks(conn_clause, volume="vol3", require_table=True)
        results.extend(self.build_clause_results_for_chunks(conn_chunks, req, score=235.0, is_conn_table=True))

        return results if results else None

    def hwdp_clause_results(self, req: SearchRequest) -> Optional[List[SearchResult]]:
        if req.search_mode != "hwdp_dimensional": return None
        conn_key = self.normalize_connection_key(req.connection_type)
        conn_clause = HWDP_CONNECTION_TO_CLAUSE.get(conn_key or "api", "3.10.1")
        chunks = self.find_clause_chunks(conn_clause, volume="vol3", require_table=True)
        return self.build_clause_results_for_chunks(chunks, req, score=245.0, is_conn_table=True) or None

    def search(self, req: SearchRequest) -> SearchResponse:
        query_interpreted = self.interpreted_query(req)
        if err := self.validate_request(req):
            return SearchResponse(success=True, query_interpreted=query_interpreted, results=[], message=err)

        if dp_results := self.drill_pipe_clause_results(req):
            return SearchResponse(success=True, query_interpreted=query_interpreted, results=dp_results)

        if hwdp_results := self.hwdp_clause_results(req):
            return SearchResponse(success=True, query_interpreted=query_interpreted, results=hwdp_results)

        chunks = self.get_chunks(req.volume)
        if not chunks: return SearchResponse(success=False, query_interpreted=query_interpreted, results=[], message="No indexed content found.")

        candidates = [c for c in chunks if self.filter_match(c, req)] or (chunks if req.query else [])
        if not candidates: return SearchResponse(success=True, query_interpreted=query_interpreted, results=[], message="Not found in Vol. 3/4.")

        scored = sorted([(c, self.score(c, req)) for c in candidates], key=lambda x: x[1], reverse=True)
        top = [(c, s) for c, s in scored[:req.top_k] if s >= 18]

        if not top: return SearchResponse(success=True, query_interpreted=query_interpreted, results=[], message="Not found. Try a more specific query.")

        return SearchResponse(success=True, query_interpreted=query_interpreted, results=[self.build_result(c, req, s) for c, s in top])