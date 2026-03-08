"""
extract_indices.py  ── run ONCE to bootstrap the indices/ directory
-------------------------------------------------------------------
1. Reads all etf/*.json files.
2. For each unique index.name, creates indices/{slug}.json containing
   the canonical holdings (picked from whichever ETF has the most
   holdings for that index, so we keep the richest data).
3. Rewrites each etf/*.json file replacing the `holdings` array with
   an `indexKey` string that points to the correct index file.

After this script runs you should commit both the new indices/ files
and the updated etf/*.json files.  normalize_data.py can then resolve
indexKey → holdings automatically.

Safe to re-run: existing index files are only overwritten if the new
source has MORE holdings (--force flag skips that guard).
"""

import json, re, sys
from pathlib import Path
from datetime import date

ROOT      = Path(__file__).parent.parent
ETF_DIR   = ROOT / "etf"
INDEX_DIR = ROOT / "indices"
FORCE     = "--force" in sys.argv      # overwrite even if existing has more holdings

TODAY = str(date.today())


# ── helpers ────────────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ── pass 1: collect the best holdings per index ────────────────────────────────

# best_index[slug] = {"indexName", "slug", "source", "updatedAt", "holdings"}
best_index: dict[str, dict] = {}
# slug_for_name[raw_index_name] = slug
slug_for_name: dict[str, str] = {}

print("Pass 1 — scanning ETF files …")
for cf in sorted(ETF_DIR.glob("*.json")):
    etfs = json.loads(cf.read_text(encoding="utf-8"))
    for etf in etfs:
        idx_name = etf.get("index", {}).get("name", "").strip()
        if not idx_name:
            print(f"  WARNING: {etf.get('nseSymbol','?')} has no index.name — skipping")
            continue

        slug = slugify(idx_name)
        slug_for_name[idx_name] = slug

        holdings = etf.get("holdings", [])
        existing = best_index.get(slug)
        if existing is None or len(holdings) > len(existing["holdings"]):
            best_index[slug] = {
                "indexName": idx_name,
                "slug":      slug,
                # "nse" means update_index_weights.py can auto-refresh;
                # "manual" means weights are maintained by hand.
                "source":    "manual",
                "updatedAt": TODAY,
                "holdings":  holdings,
            }

print(f"  → {len(best_index)} unique indices found\n")


# ── pass 2: write index files ──────────────────────────────────────────────────

INDEX_DIR.mkdir(exist_ok=True)
written = 0
skipped = 0

print("Pass 2 — writing indices/*.json …")
for slug, data in sorted(best_index.items()):
    path = INDEX_DIR / f"{slug}.json"
    if path.exists() and not FORCE:
        existing_len = len(json.loads(path.read_text(encoding="utf-8")).get("holdings", []))
        if existing_len >= len(data["holdings"]):
            skipped += 1
            continue
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  {slug}.json  ({len(data['holdings'])} holdings)")
    written += 1

print(f"  → wrote {written}, skipped {skipped} (already up-to-date)\n")


# ── pass 3: rewrite etf/*.json — replace holdings with indexKey ────────────────

print("Pass 3 — rewriting etf/*.json …")
for cf in sorted(ETF_DIR.glob("*.json")):
    etfs   = json.loads(cf.read_text(encoding="utf-8"))
    changed = False
    for etf in etfs:
        idx_name = etf.get("index", {}).get("name", "").strip()
        if not idx_name:
            continue
        slug = slug_for_name.get(idx_name)
        if slug and "holdings" in etf:
            etf["indexKey"] = slug           # add reference
            del etf["holdings"]              # remove inline data
            changed = True

    if changed:
        cf.write_text(json.dumps(etfs, ensure_ascii=False, indent=4), encoding="utf-8")
        print(f"  updated  {cf.name}")
    else:
        print(f"  skipped  {cf.name}  (no changes needed)")

print("\nDone.  Remember to run normalize_data.py next to rebuild etf-config.json.")
