Project build

Run the PowerShell build script to generate `index.html` from `input.html` and `etf-data.json`:

```powershell
cd c:\Git-Repo\static-proj\etfbharat
.\build.ps1
```

What it does:
- Reads `input.html` and replaces `<!-- INJECT_ETF_DATA -->` with a `<script>const ETF_DATA = ...;</script>` block built from `etf-data.json`.
- Writes the resulting `index.html`.

Next steps (optional):
- Move inline `app` JS into `app.js` and include it from `input.html`.
- Add a minifier (PowerShell or Node) to compress `index.html`.

## Update ETF Data Automatically

1. Install dependencies (requires Node.js):

```sh
npm install
```

2. Edit `ETF_URLS.example.js` to map each ETF ticker to its NSE/BSE URL.

3. Copy to `ETF_URLS.js`:

```sh
cp ETF_URLS.example.js ETF_URLS.js
```

4. Run the update script:

```sh
node update-etf-data.js
```

This will fetch latest NAV, AUM, and expense ratio for each ETF and update `etf-data.json` in place. It will also warn if company weights do not sum to 100%.

You must fill in the correct URLs and selectors for your ETFs in the script.
