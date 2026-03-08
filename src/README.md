# ETFBharat — Developer Guide

## Build index.html

```powershell
cd c:\Git-Repo\static-proj\etfbharat
node src/build.js            # production (minified)
node src/build.js --dev      # dev (readable)
```

Copies `src/input.html` → `index.html`.

---

## Data Architecture

Holdings weights are stored **once per index**, not once per ETF.

```
indices/
  nifty-50.json           ← canonical weights for Nifty 50
  nifty-bank.json         ← canonical weights for Nifty Bank
  domestic-gold-price.json
  …  (236 index files total)

etf/
  large-cap.json          ← ETF metadata + indexKey (no inline holdings)
  sectoral---banking.json
  …

json/
  etf-config.json         ← built by normalize_data.py (do not hand-edit)
  etf-prices.json         ← built by update_etf_prices.py (do not hand-edit)
  companies.json          ← built by normalize_data.py (do not hand-edit)
```

Each `etf/*.json` entry references an index file via `indexKey`:

```json
{
  "nseSymbol": "NIFTYBEES",
  "indexKey": "nifty-50",
  "index": { "name": "Nifty 50", ... }
}
```

All 13 ETFs that track Nifty 50 share a single `indices/nifty-50.json`.
Update that file and all ETFs pick up new weights on the next
`normalize_data.py` run.

---

## Scheduled Update Workflow

### Step 1 — Refresh index constituent weights (NSE)

```powershell
python src/update_index_weights.py
# or update specific indices only:
python src/update_index_weights.py nifty-50 nifty-bank nifty-it-index
```

- Reads `NSE_INDEX_MAP` in the script (slug → NSE query string).
- Fetches free-float market cap from NSE `/api/equity-stockIndices`.
- Calculates `weight = ffmc / sum(ffmc) * 100`.
- Commodity / debt / international indices are skipped (mapped to `None`).

### Step 2 — Rebuild etf-config.json

```powershell
python src/normalize_data.py
```

- Loads all `indices/*.json` files.
- Resolves `indexKey` → holdings for each ETF.
- Writes `etf-config.json` and `companies.json`.
- Fixes encoding in all `etf/*.json` and `indices/*.json`.

### Step 3 — Refresh ETF prices / AUM

```powershell
python src/update_etf_prices.py
```

Updates `etf-prices.json` with NAV and AUM. Run after 4 PM IST on any trading day.

---

## One-Time Migration (already done)

`src/extract_indices.py` was the one-time script that:
1. Extracted holdings from each `etf/*.json` → created `indices/{slug}.json`.
2. Replaced inline `holdings` arrays in `etf/*.json` with `indexKey` strings.

Do **not** re-run it unless intentionally resetting (use `--force` flag).

---

## Adding a New Index to Auto-Update

1. Open `src/update_index_weights.py`.
2. Add an entry to `NSE_INDEX_MAP`:
   ```python
   "my-new-index-slug": "NIFTY SOME INDEX",
   ```
3. Test: `python src/update_index_weights.py my-new-index-slug`
