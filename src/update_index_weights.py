"""
update_index_weights.py
-----------------------
Fetches the latest constituent weights for NSE equity indices and
updates the corresponding indices/*.json files.

After updating index files, you should run normalize_data.py to
rebuild etf-config.json and companies.json:

    python src/update_index_weights.py
    python src/normalize_data.py

Run this once after market hours on any trading day to keep weights fresh.

How weights are computed
------------------------
NSE's /api/equity-stockIndices returns each constituent with a `ffmc`
field (free-float market capitalisation in crores).
Weight = ffmc / sum(all ffmc in index) × 100

For indices not covered by NSE API (e.g. international, debt), a
"fallback_only" flag is set and the existing weights are kept as-is.
"""

import json, re, time, subprocess, sys
from pathlib import Path
from datetime import date

import requests

ROOT      = Path(__file__).parent.parent
INDEX_DIR = ROOT / "indices"

# ── NSE session setup ─────────────────────────────────────────────────────────
NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         "https://www.nseindia.com/",
}

session = requests.Session()
session.headers.update(NSE_HEADERS)


def init_nse_session():
    try:
        session.get("https://www.nseindia.com", timeout=12)
        time.sleep(1.5)
        print("NSE session initialised")
    except Exception as e:
        print(f"Warning: could not init NSE session: {e}")


# ── index slug → NSE API query param ─────────────────────────────────────────
# Key  : slug used in indices/*.json filename
# Value: the `index` query param accepted by NSE /api/equity-stockIndices
#        Set to None to skip NSE fetch and keep existing weights.
NSE_INDEX_MAP: dict[str, str | None] = {
    # ── Large Cap ──────────────────────────────────────────────────────────
    "nifty-50":                                     "NIFTY 50",
    "nifty-50-index":                               "NIFTY 50",
    "nifty-50-tri":                                 "NIFTY 50",
    "nifty-50-index-tri":                           "NIFTY 50",
    "sensex":                                       "NIFTY NEXT 50",   # approximate
    "bse-sensex":                                   None,              # BSE — no NSE API
    "nifty-next-50":                                "NIFTY NEXT 50",
    "nifty-next-50-index":                          "NIFTY NEXT 50",
    "nifty-next-50-tri":                            "NIFTY NEXT 50",
    "nifty-100":                                    "NIFTY 100",
    "nifty-100-total-return-index":                 "NIFTY 100",
    "nifty-100-tri":                                "NIFTY 100",
    # ── Mid & Small Cap ───────────────────────────────────────────────────
    "nifty-midcap-150":                             "NIFTY MIDCAP 150",
    "nifty-midcap-150-index":                       "NIFTY MIDCAP 150",
    "nifty-midcap-150-index-tri":                   "NIFTY MIDCAP 150",
    "nifty-midcap-150-tri":                         "NIFTY MIDCAP 150",
    "nifty-midcap-100":                             "NIFTY MIDCAP 100",
    "nifty-smallcap-250":                           "NIFTY SMALLCAP 250",
    "nifty-smallcap-250-index":                     "NIFTY SMALLCAP 250",
    # ── Sectoral ──────────────────────────────────────────────────────────
    "nifty-bank":                                   "NIFTY BANK",
    "nifty-private-bank-index":                     "NIFTY PRIVATE BANK",
    "nifty-psu-bank":                               "NIFTY PSU BANK",
    "nifty-psu-bank-index":                         "NIFTY PSU BANK",
    "nifty-it-index":                               "NIFTY IT",
    "nifty-auto-index":                             "NIFTY AUTO",
    "nifty-healthcare-index":                       "NIFTY HEALTHCARE INDEX",
    "nifty-pharma-index":                           "NIFTY PHARMA",
    "nifty-financial-services-index":               "NIFTY FINANCIAL SERVICES",
    "nifty-fmcg-index":                             "NIFTY FMCG",
    "nifty-metal-index":                            "NIFTY METAL",
    "nifty-energy-index":                           "NIFTY ENERGY",
    "nifty-realty-index":                           "NIFTY REALTY",
    "nifty-infrastructure-index":                   "NIFTY INFRASTRUCTURE",
    # ── Thematic ──────────────────────────────────────────────────────────
    "nifty-india-defence-index":                    "NIFTY INDIA DEFENCE",
    "nifty-india-defence-index-tri":                "NIFTY INDIA DEFENCE",
    "nifty-india-railways-index":                   "NIFTY INDIA RAILWAYS",
    "nifty-ev-and-new-age-automotive-index":        "NIFTY EV & NEW AGE AUTOMOTIVE",
    "nifty-ev-and-new-age-automotive-total-return-index":
                                                    "NIFTY EV & NEW AGE AUTOMOTIVE",
    "nifty-india-consumption-index":                "NIFTY INDIA CONSUMPTION",
    "nifty-india-manufacturing-total-return-index": "NIFTY INDIA MANUFACTURING",
    "nifty-mnc-index":                              "NIFTY MNC",
    "nifty-cpse-index":                             "NIFTY CPSE",
    "nifty-200-momentum-30-index":                  "NIFTY200 MOMENTUM 30",
    "nifty-alpha-50-index":                         "NIFTY ALPHA 50",
    "nifty50-value-20":                             "NIFTY50 VALUE 20",
    "nifty-50-equal-weight-index":                  "NIFTY50 EQUAL WEIGHT",
    "nifty-100-low-volatility-30-index":            "NIFTY100 LOW VOLATILITY 30",
    "nifty100-esg-sector-leaders":                  "NIFTY100 ESG SECTOR LEADERS",
    "bharat-22-index":                              "NIFTY BHARAT 22",
    # ── Commodity / Debt / International → keep existing weights ──────────
    "gold":                          None,
    "domestic-gold-price":           None,
    "domestic-price-of-gold":        None,
    "domestic-price-of-physical-gold": None,
    "commodity-gold":                None,
    "commodity-silver":              None,
    "domestic-silver-price":         None,
    "domestic-price-of-silver":      None,
    "domestic-price-of-physical-silver": None,
    "physical-price-of-silver":      None,
    "nifty-1d-rate-index":           None,
    "nifty-5-yr-benchmark-g-sec-index": None,
    "nifty-10-yr-benchmark-g-sec-index": None,
    "nasdaq-100-index":              None,
    "hang-seng-index":               None,
    "hang-seng-tech-index":          None,
    "msci-india-index":              None,
}


# ── fetch index constituents from NSE ─────────────────────────────────────────

def fetch_nse_index(nse_query: str) -> list[dict]:
    """
    Returns list of dicts: {symbol, weight (%), ...} from NSE.
    Weight is derived from free-float market cap (ffmc).
    Returns [] on error.
    """
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={nse_query}"
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"    NSE error {resp.status_code} for '{nse_query}'")
            return []
        data = resp.json().get("data", [])
        # First row is the index summary itself — skip if symbol is the index name
        constituents = [r for r in data if r.get("symbol") and r["symbol"] != nse_query]
        if not constituents:
            return []
        # Compute weights from ffmc
        total_ffmc = sum(float(r.get("ffmc") or 0) for r in constituents)
        if total_ffmc <= 0:
            return []
        result = []
        for r in constituents:
            ffmc = float(r.get("ffmc") or 0)
            result.append({
                "symbol": r["symbol"].strip(),
                "weight": round(ffmc / total_ffmc * 100, 4),
            })
        # Sort descending by weight
        result.sort(key=lambda x: -x["weight"])
        return result
    except Exception as e:
        print(f"    fetch error for '{nse_query}': {e}")
        return []


# ── apply updated weights to an index file ────────────────────────────────────

def apply_weights(idx_data: dict, nse_rows: list[dict]) -> tuple[dict, int, int]:
    """
    Merge fresh NSE weights into the existing index file data.
    Only updates `weight`; preserves name, sector, color, description.
    Returns (updated_data, updated_count, missing_count).
    """
    # Build lookup: NSE symbol → new weight
    weight_map = {r["symbol"]: r["weight"] for r in nse_rows}

    updated   = 0
    missing   = 0
    holdings  = idx_data.get("holdings", [])
    for h in holdings:
        ticker = h.get("ticker", "").strip()
        if ticker in weight_map:
            h["weight"] = weight_map[ticker]
            updated += 1
        else:
            missing += 1

    idx_data["updatedAt"] = str(date.today())
    return idx_data, updated, missing


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    if not INDEX_DIR.exists():
        print("ERROR: indices/ directory not found. Run src/extract_indices.py first.")
        sys.exit(1)

    # Determine which slugs to process
    target_slugs = set(sys.argv[1:])          # e.g. python update_index_weights.py nifty-50 nifty-bank
    all_index_files = sorted(INDEX_DIR.glob("*.json"))

    if target_slugs:
        files_to_process = [f for f in all_index_files if f.stem in target_slugs]
        print(f"Processing {len(files_to_process)} requested index file(s)")
    else:
        files_to_process = all_index_files
        print(f"Processing all {len(files_to_process)} index file(s)")

    init_nse_session()

    updated_files  = 0
    skipped_no_map = 0
    skipped_none   = 0
    errors         = 0

    for idx_f in files_to_process:
        slug = idx_f.stem
        nse_query = NSE_INDEX_MAP.get(slug, "NOT_IN_MAP")

        if nse_query == "NOT_IN_MAP":
            # Not in map at all — mark source as manual and skip silently
            skipped_no_map += 1
            continue

        if nse_query is None:
            # Explicitly mapped to None → keep existing weights
            skipped_none += 1
            continue

        print(f"  [{slug}] ← NSE '{nse_query}' … ", end="", flush=True)
        nse_rows = fetch_nse_index(nse_query)
        if not nse_rows:
            print("NO DATA — keeping existing weights")
            errors += 1
            time.sleep(0.5)
            continue

        idx_data = json.loads(idx_f.read_text(encoding="utf-8"))
        idx_data, upd, miss = apply_weights(idx_data, nse_rows)
        idx_data["source"] = "nse"
        idx_f.write_text(json.dumps(idx_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"OK  ({upd} updated, {miss} not matched)")
        updated_files += 1
        time.sleep(0.3)  # polite to NSE

    print()
    print(f"── Results ──────────────────────────────────────────")
    print(f"  Updated      : {updated_files} index files")
    print(f"  Skipped (None): {skipped_none}  (commodity/debt/international — manual only)")
    print(f"  Skipped (map) : {skipped_no_map}  (not in NSE_INDEX_MAP — add entry if needed)")
    print(f"  Errors        : {errors}")
    print()
    print("Next step: run  python src/normalize_data.py  to rebuild etf-config.json")


if __name__ == "__main__":
    main()
