"""
Updates all guide HTML pages to use the same header/footer as index.html.
- Replaces .lp-nav / .lp-footer inline CSS with unified navbar/footer structure
- Uses styles.css classes (already linked in all guide pages)
"""

import re
import os
import glob

ROOT = r"c:\Git-Repo\static-proj\etfbharat"

# Guide HTML files to update (all *.html except index.html)
GUIDE_FILES = [
    "banking-etf.html",
    "debt-etf.html",
    "etf-taxation.html",
    "etf-vs-mutual-fund.html",
    "etf-vs-stocks.html",
    "ev-rail-etf.html",
    "expense-ratio.html",
    "gold-etf.html",
    "how-to-buy-etf-india.html",
    "international-etf.html",
    "nifty-50-etf.html",
    "nse-vs-bse.html",
    "sectoral-etf.html",
    "what-is-etf.html",
]

NEW_NAVBAR = """\
<div id="navbar">
  <div class="nav-inner">
    <div class="nav-logo-wrap">
      <a href="/" style="text-decoration:none;display:flex;align-items:center;gap:10px;">
        <div class="nav-logo-icon">📊</div>
        <div>
          <div class="nav-logo-title">ETF<span style="color:#FFB300">Bharat</span></div>
          <div class="nav-logo-sub">NSE · BSE · INDIA ETF INTELLIGENCE</div>
        </div>
      </a>
    </div>
    <a href="/" style="color:#7B93B8;font-size:12px;text-decoration:none;padding:6px 14px;border:1px solid #1A2840;border-radius:20px;white-space:nowrap;">← ETF Directory</a>
  </div>
</div>"""

NEW_FOOTER = """\
<footer>
  <div class="footer-logo">ETF<span style="color:#fff">Bharat</span></div>
  <p class="footer-p">India's comprehensive ETF education platform. Understand every ETF — index, holdings, weights and companies. Not SEBI registered. Educational use only.</p>
  <div class="footer-copy">© 2026 ETFBharat.com · Educational Platform · Not Investment Advice · Consult SEBI-registered advisors</div>
</footer>"""

# CSS lines to remove (regex patterns, one per line in the <style> block)
LP_CSS_PATTERNS = [
    r'\.lp-nav\{[^}]+\}',
    r'\.lp-nav-inner\{[^}]+\}',
    r'\.lp-logo\{[^}]+\}',
    r'\.lp-logo span\{[^}]+\}',
    r'\.lp-back\{[^}]+\}',
    r'\.lp-back:hover\{[^}]+\}',
    r'\.lp-footer\{[^}]+\}',
]

# Old nav block pattern (multi-line)
OLD_NAV_PATTERN = re.compile(
    r'<nav class="lp-nav"><div class="lp-nav-inner">.*?</div></nav>',
    re.DOTALL
)

# Old footer pattern
OLD_FOOTER_PATTERN = re.compile(
    r'<footer class="lp-footer">.*?</footer>',
    re.DOTALL
)

updated = []
errors = []

for filename in GUIDE_FILES:
    filepath = os.path.join(ROOT, filename)
    if not os.path.exists(filepath):
        errors.append(f"NOT FOUND: {filename}")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. Remove lp-* CSS lines from the <style> block
    for pattern in LP_CSS_PATTERNS:
        content = re.sub(pattern + r'\n?', '', content)

    # 2. Replace old nav block with new navbar
    nav_match = OLD_NAV_PATTERN.search(content)
    if nav_match:
        content = OLD_NAV_PATTERN.sub(NEW_NAVBAR, content)
    else:
        errors.append(f"NAV NOT FOUND in {filename}")

    # 3. Replace old footer with new footer
    footer_match = OLD_FOOTER_PATTERN.search(content)
    if footer_match:
        content = OLD_FOOTER_PATTERN.sub(NEW_FOOTER, content)
    else:
        errors.append(f"FOOTER NOT FOUND in {filename}")

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        updated.append(filename)
        print(f"✅ Updated: {filename}")
    else:
        print(f"⚠️  No changes: {filename}")

print(f"\nDone. {len(updated)}/{len(GUIDE_FILES)} files updated.")
if errors:
    print("Errors:")
    for e in errors:
        print(f"  ❌ {e}")
