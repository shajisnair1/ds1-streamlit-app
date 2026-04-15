from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = ROOT_DIR / "app"
DATA_DIR = APP_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
NORMALIZED_DIR = DATA_DIR / "normalized"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)

VOL3_JSON = ROOT_DIR / "volume3_content.json"
VOL4_JSON = ROOT_DIR / "volume4_content.json"

VOL3_PDF = ROOT_DIR / "DS1_Vol3_5th.pdf"
VOL4_PDF = ROOT_DIR / "DS1_Vol4_5th.pdf"

MD_ROOT = ROOT_DIR / "md_sources"
VOL3_MD_DIR = MD_ROOT / "vol3"
VOL4_MD_DIR = MD_ROOT / "vol4"
VOL3_MD_PAGES = VOL3_MD_DIR / "pages"
VOL4_MD_PAGES = VOL4_MD_DIR / "pages"

NORMALIZED_VOL3 = NORMALIZED_DIR / "vol3_sections.json"
NORMALIZED_VOL4 = NORMALIZED_DIR / "vol4_sections.json"