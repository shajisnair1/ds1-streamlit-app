from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import SearchRequest, SearchResponse
from .loaders import load_or_build_indexes
from .fallback_pdf_parser import build_fallback_indexes
from .search_engine import StandardSearchEngine

app = FastAPI(title="DS-1 Standard Data Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

indexes = load_or_build_indexes()

if not indexes.get("vol3") and not indexes.get("vol4"):
    indexes = build_fallback_indexes()

engine = StandardSearchEngine(indexes)


@app.get("/")
def root():
    return {"message": "DS-1 Standard Data Extractor API running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "vol3_sections": len(indexes.get("vol3", [])),
        "vol4_sections": len(indexes.get("vol4", [])),
    }


@app.get("/sample-sections/{volume}")
def sample_sections(volume: str):
    chunks = indexes.get(volume, [])
    return {
        "count": len(chunks),
        "sample": [c.model_dump() for c in chunks[:3]]
    }


@app.get("/filter-options")
def filter_options():
    connection_types = [
        "NC23", "NC26", "NC31", "NC35", "NC38", "NC40", "NC44", "NC46", "NC50", "NC56",
        "6 5/8 REG", "7 5/8 REG", "5 1/2 FH", "6 5/8 FH",
        "HT",
        "XT",
        "XT-M",
        "GPDS",
        "TurboTorque",
        "TurboTorque-M",
        "uXT",
        "uGPD",
        "VX",
        "EIS",
        "TM",
        "Delta",
        "X-Force",
        "NK DSTJ",
        "HLIDS",
        "HLMTC",
        "HLST",
        "HLIST",
        "Hydril Wedge Thread",
        "DPM-DS",
        "DPM-MT",
        "DPM-ST",
        "DPM-HighTorque",
        "CET"
    ]

    hwdp_connection_types = [
        "NC23", "NC26", "NC31", "NC35", "NC38", "NC40", "NC44", "NC46", "NC50", "NC56",
        "6 5/8 REG", "7 5/8 REG", "5 1/2 FH", "6 5/8 FH",
        "HT",
        "XT",
        "XT-M",
        "GPDS",
        "uXT",
        "uGPD",
        "Delta",
        "EIS",
        "VX"
    ]

    hwdp_center_pad_map = {
        '2 7/8"': ["3 5/16"],
        '3 1/2"': ["3 1/4", "4"],
        '4"': ["4", "4 1/2"],
        '4 1/2"': ["4 1/2", "5"],
        '5"': ["5", "5 1/2"],
        '5 1/2"': ["6"],
        '5 7/8"': ["6"],
        '6 5/8"': ["6 3/8", "7 1/8"],
        '8"': ["7 1/8"]
    }

    return {
        "component_types": [
            "drill pipe",
            "hwdp",
            "drill collars",
            "bha"
        ],
        "sizes": [
            '2 3/8"', '2 7/8"', '3 1/2"', '4"', '4 1/2"', '5"', '5 1/2"', '5 7/8"',
            '6 5/8"', '6 3/4"', '8"', '9 1/2"', '9 3/4"'
        ],
        "hwdp_sizes": list(hwdp_center_pad_map.keys()),
        "weights_ppf": [
            "13.3", "15.5", "16.6", "19.5", "21.9", "25.6", "27.7"
        ],
        "connection_types": connection_types,
        "hwdp_connection_types": hwdp_connection_types,
        "grades": [
            "E75", "X95", "G105", "S135"
        ],
        "bha_connections": [
            "NC23", "NC26", "NC31", "NC35", "NC38", "NC40", "NC44", "NC46", "NC50", "NC56",
            "6 5/8 REG", "7 5/8 REG", "5 1/2 FH", "6 5/8 FH"
        ],
        "hwdp_center_pad_map": hwdp_center_pad_map
    }


@app.get("/bha-connections")
def bha_connections():
    return {
        "connections": [
            "NC23", "NC26", "NC31", "NC35", "NC38", "NC40", "NC44", "NC46", "NC50", "NC56",
            "6 5/8 REG", "7 5/8 REG", "5 1/2 FH", "6 5/8 FH"
        ]
    }


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    return engine.search(req)