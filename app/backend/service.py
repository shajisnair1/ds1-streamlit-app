from .loaders import load_or_build_indexes
from .search_engine import StandardSearchEngine


def get_filter_options():
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


def get_bha_connections():
    return [
        "NC23", "NC26", "NC31", "NC35", "NC38", "NC40", "NC44", "NC46", "NC50", "NC56",
        "6 5/8 REG", "7 5/8 REG", "5 1/2 FH", "6 5/8 FH"
    ]


def get_search_engine():
    indexes = load_or_build_indexes()

    if not indexes.get("vol3") and not indexes.get("vol4"):
        from .fallback_pdf_parser import build_fallback_indexes

        indexes = build_fallback_indexes()

    return StandardSearchEngine(indexes)
