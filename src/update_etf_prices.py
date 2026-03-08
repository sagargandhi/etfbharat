"""
update_etf_prices.py
--------------------
Updates etf-prices.json with NAV and AUM for every ETF.

  NAV  → NSE /api/etf  (ltP = closing price)
  AUM  → outstanding units × NAV
           outstanding units come from NSE /api/quote-equity (securityInfo.issuedSize)
           fallback: free-float market cap (ffmc) already in crores

Run once after 4 PM IST on any trading day to get closing prices.
"""

import json, os, time
import requests

# Project root is one level up from this script (src/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── NSE session setup ─────────────────────────────────────────────────────────
# NSE requires cookies from a browser visit before the API works.
# We establish a session by hitting the homepage first.
NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nseindia.com/',
}

session = requests.Session()
session.headers.update(NSE_HEADERS)

def init_nse_session():
    """Hit NSE homepage to get session cookies."""
    try:
        session.get('https://www.nseindia.com', timeout=10)
        time.sleep(1)
    except Exception as e:
        print(f"Warning: could not init NSE session: {e}")

# ── NSE per-ticker fetch ───────────────────────────────────────────────────────
def fetch_nse_etf_batch():
    """
    Returns a dict: nseSymbol → row from NSE /api/etf (ltP, qty, meta.isin, etc)
    """
    url = 'https://www.nseindia.com/api/etf'
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"NSE ETF list fetch failed: HTTP {resp.status_code}")
            return {}
        data = resp.json()
        return {row['symbol']: row for row in data.get('data', [])}
    except Exception as e:
        print(f"NSE ETF list fetch error: {e}")
        return {}


def fetch_nse_outstanding(symbols):
    """
    Look up outstanding quantity for each ETF symbol using the free
    NSE quote API.  The response JSON contains ``securityInfo.issuedSize``
    (the number of units outstanding) which we use to compute AUM.

    ``symbols`` should be an iterable of NSE tickers; the return value is a
    map symbol → issuedSize (float) or None on error.
    """
    out = {}
    for sym in symbols:
        url = f'https://www.nseindia.com/api/quote-equity?symbol={sym}'
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"    Outstanding fetch failed for {sym}: HTTP {resp.status_code}")
                out[sym] = None
                continue
            data = resp.json()
            sec = data.get('securityInfo', {})
            issued = sec.get('issuedSize') or sec.get('issuedQuantity')
            if issued is not None:
                # API sometimes returns strings with commas
                issued_val = float(str(issued).replace(',', ''))
            else:
                issued_val = None
            out[sym] = issued_val
        except Exception as e:
            print(f"    Outstanding lookup error for {sym}: {e}")
            out[sym] = None
        # be polite to NSE servers
        time.sleep(0.2)
    return out

# ── Load all ETF symbols from etf-config.json v2.0 ────────────────────────────
def load_etf_symbols(config_file: str) -> dict[str, dict]:
    """
    Load the normalized etf-config.json (v2.0, keyed by NSE symbol).
    Returns {nseSymbol: {name, category, ...}} for all 311 ETFs.
    Falls back gracefully if file is missing or malformed.
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        version = config.get('meta', {}).get('version', '1.0')
        if version >= '2.0' and 'etfs' in config:
            etfs = config['etfs']
            print(f"  etf-config.json v{version}: {len(etfs)} ETFs")
            return etfs
        # Legacy v1.0 — etfFiles list — shouldn't happen after normalize_data.py
        print("  WARNING: etf-config.json is old v1.0 format — run normalize_data.py first")
        return {}
    except Exception as e:
        print(f"Error loading {config_file}: {e}")
        return {}

# ── Formatting helpers ─────────────────────────────────────────────────────────
def fmt_nav(price_float: float) -> str:
    """Format NAV: ₹278.25, ₹1,234.5, ₹0.85"""
    if price_float >= 1000:
        return f"₹{price_float:,.2f}"
    return f"₹{price_float:.2f}"

def fmt_aum(aum_cr: float) -> str:
    """Format AUM in crores: ₹456.7 Cr or ₹56,762 Cr"""
    if aum_cr >= 1000:
        return f"₹{aum_cr:,.0f} Cr"
    return f"₹{aum_cr:,.1f} Cr"

# ── Main ──────────────────────────────────────────────────────────────────────
prices_file = os.path.join(ROOT_DIR, 'json', 'etf-prices.json')
with open(prices_file, 'r', encoding='utf-8') as f:
    etf_prices = json.load(f)
print(f"Loaded etf-prices.json: {len(etf_prices)} existing records")

print("\nLoading ETF symbols from etf-config.json v2.0 ...")
etf_config = load_etf_symbols(os.path.join(ROOT_DIR, 'json', 'etf-config.json'))
if not etf_config:
    print("No ETFs loaded — aborting.")
    raise SystemExit(1)

print("\nInitialising NSE session...")
init_nse_session()

print("Fetching NSE ETF list...")
nse_etfs = fetch_nse_etf_batch()
print(f"  Got {len(nse_etfs)} ETFs from NSE API")
if nse_etfs:
    print(f"  Available fields: {list(next(iter(nse_etfs.values())).keys())}")

# Fetch outstanding units only for symbols found in NSE data (saves time)
symbols_to_query = list(nse_etfs.keys())
print(f"\nFetching outstanding units for {len(symbols_to_query)} symbols ...")
nse_outstanding = fetch_nse_outstanding(symbols_to_query)
valid_out = sum(1 for v in nse_outstanding.values() if v is not None)
print(f"  Got outstanding for {valid_out}/{len(symbols_to_query)} symbols")

updated_nav = updated_aum = added_new = 0

for nse_symbol, etf_meta in etf_config.items():
    row = nse_etfs.get(nse_symbol)
    if not row:
        # ETF exists in our config but not in NSE live list (de-listed or thin trading)
        continue

    raw_nav  = row.get('ltP')
    ffmc     = row.get('ffmc')   # free-float mkt cap in crores (fallback for AUM)

    # ── NAV ──────────────────────────────────────────────────────────────────
    nav_str   = None
    nav_float = None
    if raw_nav is not None:
        try:
            nav_float = float(str(raw_nav).replace(',', ''))
            nav_str   = fmt_nav(nav_float)
        except Exception:
            pass

    # ── AUM ──────────────────────────────────────────────────────────────────
    aum_str  = None
    out_units = nse_outstanding.get(nse_symbol)
    if out_units is not None and nav_float is not None:
        try:
            aum_cr  = (out_units * nav_float) / 1e7   # units × NAV → crores
            aum_str = fmt_aum(aum_cr)
        except Exception as e:
            print(f"  [AUM calc error {nse_symbol}] units={out_units} nav={nav_float}: {e}")
    if aum_str is None and ffmc is not None:
        try:
            aum_cr  = float(str(ffmc).replace(',', ''))
            aum_str = fmt_aum(aum_cr)
        except Exception as e:
            print(f"  [FFMC parse error {nse_symbol}] ffmc={ffmc}: {e}")

    # ── Expense ratio (kept from existing; NSE doesn't provide this) ──────────
    existing   = etf_prices.get(nse_symbol, {})
    expense    = existing.get('expense', '—')

    # ── Upsert into etf_prices ────────────────────────────────────────────────
    if nse_symbol not in etf_prices:
        etf_prices[nse_symbol] = {}
        added_new += 1

    if nav_str:
        etf_prices[nse_symbol]['nav']     = nav_str
        updated_nav += 1
    if aum_str:
        etf_prices[nse_symbol]['aum']     = aum_str
        updated_aum += 1
    etf_prices[nse_symbol]['expense'] = expense

    print(f"  {nse_symbol}: NAV={nav_str or '—'}  AUM={aum_str or '—'}  Exp={expense}")
    time.sleep(0.2)

with open(prices_file, 'w', encoding='utf-8') as f:
    json.dump(etf_prices, f, indent=2, ensure_ascii=False)

print(f"\nDone.  NAV updated: {updated_nav}  |  AUM updated: {updated_aum}  |  New entries: {added_new}")
print(f"etf-prices.json now has {len(etf_prices)} records")
