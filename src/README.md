Project Build

Run Node.js build script to generate `index.html` from `input.html`:

```powershell
cd c:\Git-Repo\static-proj\etfbharat
npm run build
```

Or use the build.js script directly:

```powershell
node src/build.js
```

What it does:
- Copies `input.html` to `index.html` (with optional minification for production).

ETF data files (`etf/`, `etf-config.json`, `etf-prices.json`) live **only in the project root** and are used directly by `index.html` — no copying needed.

## Update ETF Prices Automatically

The Python script `update_etf_prices.py` queries NSE free APIs to fetch:
- **NAV** (closing price) from `/api/etf`
- **Outstanding Units** from `/api/quote-equity` 
- **AUM** = outstanding units × NAV (with ffmc fallback)

Run it after 4 PM IST on any trading day (from any directory):

```powershell
python src/update_etf_prices.py
```

This will update `etf-prices.json` in the project root with the latest NAV and AUM for each ETF.

Note: The script loads ETF metadata from individual sector JSON files in the root `etf/` folder via `etf-config.json`.
