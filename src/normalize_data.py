"""
Normalize ETF data:
  - etf-config.json  → keyed by NSE symbol, holdings = [{ticker, weight}]
  - etf-prices.json  → unchanged (already keyed by NSE symbol)
  - companies.json   → keyed by NSE ticker, with name/sector/color/description
"""

import json, os
from pathlib import Path

ROOT = Path(__file__).parent.parent
ETF_DIR = ROOT / "etf"

# ── helpers ────────────────────────────────────────────────────────────────────
# Mojibake map:
# e.g. ₹ (E2 82 B9) read as cp1252 → â‚¹ (U+00E2 U+201A U+00B9)
_MOJIBAKE = [
    ('\u00e2\u201a\u00b9', '\u20b9'),  # â‚¹ → ₹
    ('\u00e2\u20ac\u201d', '\u2014'),  # â€" → —  (em dash)
    ('\u00e2\u20ac\u2013', '\u2013'),  # â€" → –  (en dash)
    ('\u00e2\u20ac\u2019', '\u2019'),  # â€™ → '  (right single quote)
    ('\u00e2\u20ac\u2018', '\u2018'),  # â€˜ → '  (left single quote)
    ('\u00e2\u20ac\u201c', '\u201c'),  # â€œ → "  (left double quote)
    ('\u00e2\u20ac\u2026', '\u2026'),  # â€¦ → …  (ellipsis)
    ('\u00e2\u20ac\u02dc', '\u007e'),  # â€˜ edge case
    ('\u00c2\u00a0', '\u00a0'),        # Â  → NBSP
    ('\u00c3\u00a9', '\u00e9'),        # Ã© → é
    ('\u00c3\u00b3', '\u00f3'),        # Ã³ → ó
]

def fix_encoding(text: str) -> str:
    """Fix known mojibake sequences (UTF-8 bytes misread as cp1252)."""
    if not isinstance(text, str):
        return text
    for bad, good in _MOJIBAKE:
        if bad in text:
            text = text.replace(bad, good)
    return text

def fix_obj(obj):
    """Recursively fix encoding in a JSON object."""
    if isinstance(obj, str):
        return fix_encoding(obj)
    if isinstance(obj, list):
        return [fix_obj(v) for v in obj]
    if isinstance(obj, dict):
        return {k: fix_obj(v) for k, v in obj.items()}
    return obj

# ── read all ETF category files ────────────────────────────────────────────────
config_files = sorted(ETF_DIR.glob("*.json"))
print(f"Found {len(config_files)} ETF category files")

all_etfs = {}         # nseSymbol → ETF config entry
companies = {}        # company ticker → company record

for cf in config_files:
    etfs = fix_obj(json.loads(cf.read_text(encoding="utf-8")))
    for etf in etfs:
        sym = etf.get("nseSymbol") or etf.get("ticker")
        if not sym:
            print(f"  WARNING: ETF missing nseSymbol in {cf.name}: {etf.get('name')}")
            continue

        # Collect company descriptions & build slim holdings list
        slim_holdings = []
        for h in etf.get("holdings", []):
            ticker = h.get("ticker", "").strip()
            if not ticker:
                continue
            # Store company record (first-seen wins for description)
            if ticker not in companies:
                companies[ticker] = {
                    "name":        h.get("name", ""),
                    "sector":      h.get("sector", ""),
                    "color":       h.get("color", ""),
                    "description": h.get("description", ""),
                }
            slim_holdings.append({
                "ticker": ticker,
                "weight": h.get("weight", 0),
            })

        all_etfs[sym] = {
            "id":       etf.get("id", ""),
            "name":     etf.get("name", ""),
            "exchange": etf.get("exchange", "NSE"),
            "category": etf.get("category", ""),
            "color":    etf.get("color", ""),
            "index":    etf.get("index", {}),
            "holdings": slim_holdings,
            "sourceFile": cf.name,
        }

print(f"Total ETFs: {len(all_etfs)}")
print(f"Total unique companies: {len(companies)}")

# ── fix etf-prices.json encoding ───────────────────────────────────────────────
prices_path = ROOT / "etf-prices.json"
prices = fix_obj(json.loads(prices_path.read_text(encoding="utf-8")))
prices_path.write_text(
    json.dumps(prices, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"Fixed etf-prices.json ({len(prices)} entries)")

# ── write new etf-config.json ──────────────────────────────────────────────────
config_out = {
    "meta": {
        "description": "ETF configuration keyed by NSE symbol",
        "version": "2.0",
        "primaryKey": "nseSymbol",
        "lastUpdated": "2026-03-08",
        "totalEtfs": len(all_etfs),
        "totalCompanies": len(companies),
    },
    "etfs": all_etfs,
}
config_path = ROOT / "etf-config.json"
config_path.write_text(
    json.dumps(config_out, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"Written etf-config.json")

# ── write companies.json ───────────────────────────────────────────────────────
companies_out = {
    "meta": {
        "description": "All companies referenced in ETF holdings, keyed by NSE ticker",
        "version": "1.0",
        "primaryKey": "nseTicker",
        "lastUpdated": "2026-03-08",
        "totalCompanies": len(companies),
    },
    "companies": companies,
}
companies_path = ROOT / "companies.json"
companies_path.write_text(
    json.dumps(companies_out, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"Written companies.json")

# ── also fix encoding in all ETF category files ───────────────────────────────
for cf in config_files:
    raw = json.loads(cf.read_text(encoding="utf-8"))
    fixed = fix_obj(raw)
    cf.write_text(json.dumps(fixed, ensure_ascii=False, indent=4), encoding="utf-8")
print(f"Fixed encoding in {len(config_files)} ETF category files")

# ── summary ────────────────────────────────────────────────────────────────────
print("\n── Summary ──────────────────────────────────────────")
print(f"  etf-config.json : {len(all_etfs)} ETFs keyed by NSE symbol")
print(f"  etf-prices.json : {len(prices)} price records (encoding fixed)")
print(f"  companies.json  : {len(companies)} unique companies")
print(f"  etf/*.json      : encoding fixed in {len(config_files)} files")
