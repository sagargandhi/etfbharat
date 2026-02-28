"""
update_etf_prices.py
--------------------
Updates etf-prices.json with end-of-day data from two sources:

  NAV + AUM  →  NSE equity API
               NAV  = priceInfo.lastPrice  (closing price)
               AUM  = securityInfo.issuedSize × lastPrice  (units × NAV)

  Expense    →  AMFI NAVAll.txt  (scheme expense ratio, updated monthly by AMFI)
               Matched by ISIN returned from NSE API

Run once after 4 PM IST on any trading day to get closing prices.
"""

import json, re, time
import requests

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

# ── AMFI expense ratio lookup ─────────────────────────────────────────────────
def fetch_amfi_expense_ratios():
    """
    Fetch AMFI NAVAll.txt and build an ISIN → expense ratio map.
    AMFI provides TER (Total Expense Ratio) for all mutual fund schemes.
    Format: SchemeCode;ISINDiv;ISINGrowth;SchemeName;NAV;Date
    Expense ratio comes from a separate AMFI endpoint per scheme.
    We use the simpler approach: scrape the ETF TER page.
    """
    url = 'https://www.amfiindia.com/modules/TerReport'
    isin_to_expense = {}
    try:
        r = requests.get(url, timeout=15,
                         headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code != 200:
            print(f"AMFI TER fetch failed: HTTP {r.status_code}")
            return isin_to_expense
        # Response is HTML table; parse rows with regex
        # Columns: AMC | Scheme Name | ISIN | TER (Regular) | TER (Direct) | Date
        rows = re.findall(
            r'<td[^>]*>(.*?)</td>', r.text, re.DOTALL | re.IGNORECASE)
        # Group into sets of 6
        for i in range(0, len(rows) - 5, 6):
            cells = [re.sub(r'<[^>]+>', '', rows[i+j]).strip() for j in range(6)]
            isin = cells[2].strip()
            ter  = cells[4].strip()  # Direct plan TER
            if isin and ter and re.match(r'[\d.]+', ter):
                isin_to_expense[isin] = ter + '%'
    except Exception as e:
        print(f"AMFI fetch error: {e}")
    return isin_to_expense

# ── NSE per-ticker fetch ───────────────────────────────────────────────────────
def fetch_nse_etf(ticker):
    """
    Returns (nav_str, aum_str, isin) from NSE closing data.
    NAV  = priceInfo.lastPrice
    AUM  = issuedSize (total units) × lastPrice ÷ 1 Cr  →  formatted as ₹X,XXX Cr
    ISIN is used to look up expense ratio from AMFI.
    """
    url = f'https://www.nseindia.com/api/quote-equity?symbol={ticker}'
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"  {ticker}: HTTP {resp.status_code}")
            return None, None, None
        data = resp.json()

        last_price   = data.get('priceInfo', {}).get('lastPrice')
        issued_size  = data.get('securityInfo', {}).get('issuedSize')  # total units
        isin         = data.get('info', {}).get('isin', '')

        if not last_price:
            return None, None, isin

        nav_str = f"₹{last_price:,.2f}".rstrip('0').rstrip('.')

        aum_str = None
        if issued_size and last_price:
            aum_cr = (issued_size * last_price) / 1e7  # paise → crore
            if aum_cr >= 1000:
                aum_str = f"₹{aum_cr:,.0f} Cr"
            else:
                aum_str = f"₹{aum_cr:,.1f} Cr"

        return nav_str, aum_str, isin

    except Exception as e:
        print(f"  {ticker}: error — {e}")
        return None, None, None

# ── Main ──────────────────────────────────────────────────────────────────────
with open('etf-prices.json', 'r', encoding='utf-8') as f:
    etf_prices = json.load(f)

print("Initialising NSE session...")
init_nse_session()

print("Fetching AMFI expense ratios...")
amfi_expense = fetch_amfi_expense_ratios()
print(f"  Got {len(amfi_expense)} AMFI TER entries")

updated_nav = updated_aum = updated_exp = 0

for ticker in etf_prices:
    print(f"  Fetching {ticker}...", end=' ')
    nav_str, aum_str, isin = fetch_nse_etf(ticker)

    if nav_str:
        etf_prices[ticker]['nav'] = nav_str
        updated_nav += 1

    if aum_str:
        etf_prices[ticker]['aum'] = aum_str
        updated_aum += 1

    exp_str = amfi_expense.get(isin) if isin else None
    if exp_str:
        etf_prices[ticker]['expense'] = exp_str
        updated_exp += 1

    print(f"NAV={nav_str or '—'}  AUM={aum_str or '—'}  Exp={exp_str or '—'}")
    time.sleep(0.5)

with open('etf-prices.json', 'w', encoding='utf-8') as f:
    json.dump(etf_prices, f, indent=2, ensure_ascii=False)

print(f"\nDone. NAV updated: {updated_nav} | AUM updated: {updated_aum} | Expense updated: {updated_exp}")
