import requests
import re

# inspect main site for endpoints
r = requests.get('https://www.amfiindia.com/', headers={'User-Agent':'Mozilla/5.0'})
print('homepage', r.status_code, len(r.text))
urls = re.findall(r'"(/[^"\s]+)"', r.text)
for url in urls:
    if 'api' in url.lower() or 'ter' in url.lower():
        print('possible url', url)

# now fetch the TER page which replaced former TerReport
r2 = requests.get('https://www.amfiindia.com/ter-of-mf-schemes', headers={'User-Agent':'Mozilla/5.0'})
print('ter page', r2.status_code, len(r2.text))
# look for JSON or data endpoints referenced
for url in re.findall(r'"(https?://[^"]+)"', r2.text):
    if 'amfi' in url and ('ter' in url.lower() or 'api' in url.lower()):
        print('ter page link', url)

# also see if script tags include URLs
for match in re.findall(r'src="([^"]+)"', r2.text):
    if 'cdn' in match or 'amfiindia.com' in match:
        print('script src', match)
