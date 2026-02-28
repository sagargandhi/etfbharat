Project Build

Run Node.js build script to generate `index.html` from `input.html` and copy ETF data:

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
- Copies all sector/theme JSON files from `src/etf/` to root `etf/` folder.
- Copies `etf-prices.json` to root.

The app dynamically loads ETF data from individual JSON files (one per sector/theme) instead of a single large file, improving performance and maintainability.

## Update ETF Prices Automatically

The Python script `update_etf_prices.py` queries NSE free APIs to fetch:
- **NAV** (closing price) from `/api/etf`
- **Outstanding Units** from `/api/quote-equity` 
- **AUM** = outstanding units × NAV (with ffmc fallback)

Run it after 4 PM IST on any trading day:

```powershell
cd src
python update_etf_prices.py
```

This will update `etf-prices.json` with the latest NAV and AUM for each ETF.

Note: The script now loads ETF metadata from individual sector JSON files in the `etf/` folder instead of a single `etf-data.json` file.
