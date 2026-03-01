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

# ── Load all ETF data from sector JSON files ──────────────────────────────────
def load_etf_data_from_config(config_file='etf-config.json', etf_folder='etf'):
    """Load all ETF data from individual sector/theme JSON files using config."""
    etf_data = []
    
    # Load configuration
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        etf_files = config.get('etfFiles', [])
    except Exception as e:
        print(f"Error loading config file {config_file}: {e}")
        return etf_data
    
    if not etf_files:
        print(f"No ETF files configured in {config_file}")
        return etf_data
    
    for filename in etf_files:
        filepath = os.path.join(etf_folder, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    etf_data.extend(data)
                    print(f"  Loaded {len(data)} ETFs from {filename}")
                else:
                    print(f"  Skipped {filename} (invalid format)")
        except Exception as e:
            print(f"  Error loading {filepath}: {e}")
    
    return etf_data

# ── Main ──────────────────────────────────────────────────────────────────────
prices_file = os.path.join(ROOT_DIR, 'etf-prices.json')
with open(prices_file, 'r', encoding='utf-8') as f:
    etf_prices = json.load(f)

print("Loading ETF data from etf/ folder using config...")
etf_data = load_etf_data_from_config(
    os.path.join(ROOT_DIR, 'etf-config.json'),
    os.path.join(ROOT_DIR, 'etf')
)
print(f"  Total: {len(etf_data)} ETFs loaded")

print("\nInitialising NSE session...")
init_nse_session()

print("Fetching NSE ETF list...")
nse_etfs = fetch_nse_etf_batch()
print(f"  Got {len(nse_etfs)} ETFs from NSE")

# Debug: show available fields from first ETF
if nse_etfs:
    first_etf = next(iter(nse_etfs.values()))
    print(f"  Available fields: {list(first_etf.keys())}")

# use free NSE quote API to fetch outstanding units for each symbol
print("Fetching outstanding quantities from NSE...")
nse_outstanding = fetch_nse_outstanding(nse_etfs.keys())
valid_out = sum(1 for v in nse_outstanding.values() if v is not None)
print(f"  Got outstanding for {valid_out} symbols")

updated_nav = updated_aum = 0

for etf in etf_data:
    ticker = etf.get('ticker')
    nse_symbol = etf.get('nseSymbol', ticker)
    if not ticker or not nse_symbol or ticker not in etf_prices:
        continue
    row = nse_etfs.get(nse_symbol)
    if not row:
        print(f"  {ticker}: NSE symbol '{nse_symbol}' not found in ETF list")
        continue
    nav = row.get('ltP')
    ffmc = row.get('ffmc')  # Free-float market cap in crores (fallback)

    nav_str = None
    nav_float = None
    if nav is not None:
        try:
            nav_float = float(nav)
            nav_str = f"₹{nav_float:,.2f}".rstrip('0').rstrip('.')
        except Exception:
            nav_str = None
    aum_str = None

    # first try to compute using outstanding units from NSE quote API
    out_units = nse_outstanding.get(nse_symbol)
    if out_units is not None and nav_float is not None:
        try:
            aum_val = out_units * nav_float
            # convert to crores for display
            aum_cr = aum_val / 1e7  # 1 crore = 10 million
            aum_str = f"₹{aum_cr:,.1f} Cr" if aum_cr < 1000 else f"₹{aum_cr:,.0f} Cr"
        except Exception as e:
            print(f"    [AUM calc error from outstanding for {ticker}] out={out_units} nav={nav_float} err={e}")
    # fallback to ffmc if outstanding unavailable
    if aum_str is None:
        try:
            if ffmc is not None:
                # Use free-float market cap directly (already in crores)
                aum_cr = float(str(ffmc).replace(',', ''))
                aum_str = f"₹{aum_cr:,.1f} Cr" if aum_cr < 1000 else f"₹{aum_cr:,.0f} Cr"
            else:
                print(f"    [No FFMC available for {ticker}]")
        except Exception as e:
            print(f"    [AUM calc error for {ticker}] ffmc={ffmc} err={e}")

    if nav_str:
        etf_prices[ticker]['nav'] = nav_str
        updated_nav += 1
    if aum_str:
        etf_prices[ticker]['aum'] = aum_str
        updated_aum += 1

    print(f"  {ticker} (NSE: {nse_symbol}): NAV={nav_str or '—'}  AUM={aum_str or '—'}")
    time.sleep(0.2)

with open(prices_file, 'w', encoding='utf-8') as f:
    json.dump(etf_prices, f, indent=2, ensure_ascii=False)

print(f"\nDone. NAV updated: {updated_nav} | AUM updated: {updated_aum}")
