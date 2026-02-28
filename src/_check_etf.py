import requests, time, json

NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nseindia.com/',
}
session = requests.Session()
session.headers.update(NSE_HEADERS)
session.get('https://www.nseindia.com', timeout=10)
time.sleep(1)

r = session.get('https://www.nseindia.com/api/etf', timeout=10)
d = r.json()
all_etfs = {row['symbol']: row for row in d['data']}

with open('src/etf-prices.json', encoding='utf-8') as f:
    prices = json.load(f)

# Print all 312 NSE ETF symbols so we can manually map
for sym in sorted(all_etfs.keys()):
    meta = all_etfs[sym].get('meta', {})
    isin = meta.get('isin', '')
    name = meta.get('companyName', '')
    print(f"{sym:<20} {isin}  {name}")
