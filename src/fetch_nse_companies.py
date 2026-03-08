"""
Fetch all NSE-listed companies and merge into companies.json.

Sources used (all public, no auth required):
  1. https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv
     → Complete list of NSE-listed equities (symbol, name, ISIN, series, listing date)
  2. Multiple Nifty index CSVs  → sector / industry classification for index stocks
  3. NSE equity meta API (optional, best-effort per symbol) → detailed sector/industry

Merge strategy:
  - Existing entries in companies.json are PRESERVED as-is (they have rich descriptions).
  - New symbols get: name, sector, color, isin, series, listingDate, description="".
"""

import json, csv, time, logging, io, sys
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    sys.exit("Install requests: pip install requests")

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT   = Path(__file__).parent.parent
OUT    = ROOT / "json" / "companies.json"

# ── Sector → hex color map ────────────────────────────────────────────────────
SECTOR_COLORS: dict[str, str] = {
    "Financial Services":         "#2196F3",
    "Banks":                      "#1565C0",
    "Insurance":                  "#0D47A1",
    "Information Technology":     "#00BCD4",
    "Oil Gas & Consumable Fuels": "#FF6F00",
    "Energy":                     "#FF8F00",
    "Fast Moving Consumer Goods": "#4CAF50",
    "Consumer Durables":          "#66BB6A",
    "Healthcare":                 "#E91E63",
    "Pharmaceuticals":            "#AD1457",
    "Automobile":                 "#9C27B0",
    "Auto Components":            "#7B1FA2",
    "Capital Goods":              "#FF5722",
    "Construction":               "#BF360C",
    "Metals & Mining":            "#607D8B",
    "Realty":                     "#795548",
    "Telecom":                    "#F50057",
    "Media":                      "#FF4081",
    "Power":                      "#FFC107",
    "Chemicals":                  "#8BC34A",
    "Textiles":                   "#CDDC39",
    "Cement":                     "#9E9E9E",
    "Diversified":                "#00ACC1",
    "Services":                   "#26C6DA",
    "Commodity":                  "#FFB300",
    "Agricultural":               "#558B2F",
    "Defence":                    "#3E2723",
    "Infrastructure":             "#F57F17",
    "Logistics":                  "#0288D1",
    "Retail":                     "#6A1B9A",
}

def sector_color(sector: str) -> str:
    for key, color in SECTOR_COLORS.items():
        if key.lower() in sector.lower() or sector.lower() in key.lower():
            return color
    return "#9E9E9E"  # fallback grey

# ── HTTP helpers ───────────────────────────────────────────────────────────────
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/",
})

def _warm_cookie() -> None:
    """Hit the NSE homepage once to get session cookies (needed for API calls)."""
    try:
        SESSION.get("https://www.nseindia.com", timeout=15)
        time.sleep(1)
    except Exception as e:
        log.warning(f"Cookie warm-up failed: {e}")

def _get_csv(url: str) -> list[dict]:
    """Fetch a CSV URL and return list of dicts."""
    r = SESSION.get(url, timeout=30)
    r.raise_for_status()
    reader = csv.DictReader(io.StringIO(r.text))
    return [row for row in reader]

def _get_json(url: str) -> Any:
    r = SESSION.get(url, timeout=20)
    r.raise_for_status()
    return r.json()

# ── Step 1: Warm cookie ────────────────────────────────────────────────────────
log.info("Warming NSE session cookie …")
_warm_cookie()

# ── Step 2: Full equity list ──────────────────────────────────────────────────
log.info("Fetching complete NSE equity list …")
EQUITY_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
try:
    equity_rows = _get_csv(EQUITY_URL)
    log.info(f"  Got {len(equity_rows)} equity rows")
except Exception as e:
    log.error(f"Failed to fetch equity list: {e}")
    equity_rows = []

# Build symbol → {name, isin, series, listingDate}
equity_map: dict[str, dict] = {}
for row in equity_rows:
    sym = row.get(" SYMBOL", row.get("SYMBOL", "")).strip()
    if not sym:
        continue
    equity_map[sym] = {
        "name":        row.get("NAME OF COMPANY", "").strip().title(),
        "isin":        row.get(" ISIN NUMBER", row.get("ISIN NUMBER", "")).strip(),
        "series":      row.get(" SERIES", row.get("SERIES", "")).strip(),
        "listingDate": row.get(" DATE OF LISTING", row.get("DATE OF LISTING", "")).strip(),
    }
log.info(f"Parsed {len(equity_map)} unique NSE symbols from equity list")

# ── Step 3: Sector data from Nifty index CSVs ────────────────────────────────
SECTOR_CSVS = [
    "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv",
    "https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv",
    "https://nsearchives.nseindia.com/content/indices/ind_niftymidcap150list.csv",
    "https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
    "https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap50list.csv",
    "https://nsearchives.nseindia.com/content/indices/ind_niftymicrocap250list.csv",
]

sector_map: dict[str, str] = {}  # symbol → sector/industry string
name_map: dict[str, str] = {}    # symbol → properly-cased company name

for url in SECTOR_CSVS:
    try:
        rows = _get_csv(url)
        for row in rows:
            sym = row.get("Symbol", "").strip()
            industry = (
                row.get("Industry", "")
                or row.get("Sector", "")
                or row.get("INDUSTRY", "")
            ).strip()
            cname = (
                row.get("Company Name", "")
                or row.get("NAME OF COMPANY", "")
            ).strip()
            if sym:
                if industry and sym not in sector_map:
                    sector_map[sym] = industry
                if cname and sym not in name_map:
                    name_map[sym] = cname
        log.info(f"  {url.split('/')[-1]}: sector data for {len(sector_map)} symbols")
    except Exception as e:
        log.warning(f"  Could not fetch {url.split('/')[-1]}: {e}")

# ── Step 4: Load existing companies.json ──────────────────────────────────────
log.info("Loading existing companies.json …")
data = json.loads(OUT.read_text("utf-8"))
existing: dict[str, dict] = data["companies"]
log.info(f"  {len(existing)} companies already present")

# ── Step 5: Merge ─────────────────────────────────────────────────────────────
added = 0
updated = 0

for sym, eq in equity_map.items():
    if sym in existing:
        # Patch ISIN/listingDate onto existing entries if missing
        changed = False
        for field in ("isin", "listingDate", "series"):
            if eq.get(field) and field not in existing[sym]:
                existing[sym][field] = eq[field]
                changed = True
        if changed:
            updated += 1
        continue

    # New company
    sector   = sector_map.get(sym, "")
    raw_name = name_map.get(sym) or eq["name"]

    existing[sym] = {
        "name":        raw_name,
        "sector":      sector,
        "color":       sector_color(sector),
        "isin":        eq["isin"],
        "series":      eq["series"],
        "listingDate": eq["listingDate"],
        "description": "",
    }
    added += 1

log.info(f"Added {added} new companies, patched {updated} existing entries")

# ── Step 6: Sort alphabetically by key & update meta ─────────────────────────
data["companies"] = dict(sorted(existing.items()))
data["meta"]["totalCompanies"] = len(data["companies"])
data["meta"]["lastUpdated"] = "2026-03-08"

OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
log.info(f"Written companies.json → {len(data['companies'])} total companies  ({OUT.stat().st_size//1024} KB)")
