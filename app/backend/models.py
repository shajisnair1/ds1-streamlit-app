from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

VolumeType = Literal["vol3", "vol4", "all"]
ResultType = Literal["text", "table", "reference", "not_found"]
SearchMode = Literal[
    "free_text",
    "drill_pipe_dimensional",
    "hwdp_dimensional",
    "drill_collar_dimensional",
    "bha_acceptance",
    "bha_general",
]

class SectionChunk(BaseModel):
    volume: str
    page_number: int
    clause: Optional[str] = None
    heading: Optional[str] = None
    text: str = ""
    keywords: List[str] = Field(default_factory=list)
    has_table: bool = False
    table_data: Optional[List[Dict[str, Any]]] = None
    raw_table: Optional[List[List[str]]] = None
    source_type: Optional[str] = None

class SearchRequest(BaseModel):
    volume: VolumeType = "all"
    search_mode: SearchMode = "free_text"
    query: Optional[str] = None
    
    target_clause: Optional[str] = None  # NEW: Added target clause override

    component_type: Optional[str] = None
    size: Optional[str] = None
    weight_ppf: Optional[str] = None
    connection_type: Optional[str] = None
    grade: Optional[str] = None

    reduced_tsr: bool = False
    twdp: bool = False

    center_pad_od: Optional[str] = None
    slip_recess_depth: Optional[str] = None
    elevator_recess_depth: Optional[str] = None

    used_bha_acceptance_only: bool = False
    top_k: int = 5

class SearchResult(BaseModel):
    result_type: ResultType
    volume: Optional[str] = None
    page_number: Optional[int] = None
    clause: Optional[str] = None
    heading: Optional[str] = None

    text: Optional[str] = None
    table: Optional[List[Dict[str, Any]]] = None
    markdown_table: Optional[str] = None

    confidence: Optional[float] = None
    notes: Optional[str] = None
    source_type: Optional[str] = None
    page_ref: Optional[str] = None

class SearchResponse(BaseModel):
    success: bool
    query_interpreted: str
    results: List[SearchResult] = Field(default_factory=list)
    message: Optional[str] = None