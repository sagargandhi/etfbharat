"""
Check and fix mojibake encoding in all JSON and HTML files.
Covers emoji corruption (ðŸ… etc.) plus common symbol patterns.
Self-deletes after running.
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent.parent

# ── Full mojibake map ─────────────────────────────────────────────────────────
# Pattern: UTF-8 bytes misread as cp1252/latin-1
FIXES = [
    # Rupee ₹ (E2 82 B9)
    ('\u00e2\u201a\u00b9', '\u20b9'),
    # Em dash — (E2 80 94)
    ('\u00e2\u20ac\u201d', '\u2014'),
    # En dash – (E2 80 93)
    ('\u00e2\u20ac\u2013', '\u2013'),
    # Right single quote ' (E2 80 99)
    ('\u00e2\u20ac\u2019', '\u2019'),
    # Left single quote ' (E2 80 98)
    ('\u00e2\u20ac\u2018', '\u2018'),
    # Left double quote " (E2 80 9C)
    ('\u00e2\u20ac\u201c', '\u201c'),
    # Right double quote " (E2 80 9D)
    ('\u00e2\u20ac\u009d', '\u201d'),
    # Ellipsis … (E2 80 A6)
    ('\u00e2\u20ac\u2026', '\u2026'),
    # Bullet • (E2 80 A2)
    ('\u00e2\u20ac\u00a2', '\u2022'),
    # Middle dot · (C2 B7)
    ('\u00c2\u00b7', '\u00b7'),
    # NBSP (C2 A0)
    ('\u00c2\u00a0', '\u00a0'),
    # é (C3 A9)
    ('\u00c3\u00a9', '\u00e9'),
    # ó (C3 B3)
    ('\u00c3\u00b3', '\u00f3'),
    # ▾ dropdown arrow (E2 96 BE)
    ('\u00e2\u2013\u00be', '\u25be'),
    # → right arrow (E2 86 92)
    ('\u00e2\u2020\u2019', '\u2192'),
    # ☰ hamburger (E2 98 B0)
    ('\u00e2\u02dc\u00b0', '\u2630'),
    # ⚡ lightning (E2 9A A1)
    ('\u00e2\u009a\u00a1', '\u26a1'),
    # ✓ check (E2 9C 93)
    ('\u00e2\u009c\u2019', '\u2713'),
    # × multiply (C3 97)
    ('\u00c3\u2014', '\u00d7'),

    # ── 4-byte emoji: F0 XX XX XX read as cp1252 gives ð Ÿ X X ─────────────
    # The pattern is: U+00F0 (ð) + U+0178 (Ÿ) + two more cp1252 chars

    # 📊 U+1F4CA  F0 9F 93 8A → ðŸ"Š  (ð=F0, Ÿ=9F, "=93, Š=8A)
    ('\u00f0\u0178\u201c\u0160', '\U0001f4ca'),
    # 📈 U+1F4C8  F0 9F 93 88 → ðŸ"ˆ  (ð=F0, Ÿ=9F, "=93, ˆ=88)
    ('\u00f0\u0178\u201c\u02c6', '\U0001f4c8'),
    # 📉 U+1F4C9  F0 9F 93 89 → ðŸ"‰  (ð=F0, Ÿ=9F, "=93, ‰=89)
    ('\u00f0\u0178\u201c\u2030', '\U0001f4c9'),
    # 📋 U+1F4CB  F0 9F 93 8B → ðŸ"‹  (ð=F0, Ÿ=9F, "=93, ‹=8B)
    ('\u00f0\u0178\u201c\u2039', '\U0001f4cb'),
    # 🏠 U+1F3E0  F0 9F 8F A0 → ðŸ    (ð=F0, Ÿ=9F, =8F→undefined, =A0→NBSP)
    ('\u00f0\u0178\u008f\u00a0', '\U0001f3e0'),
    # 🏗️ U+1F3D7  F0 9F 8F 97 → ðŸ—  (ð=F0, Ÿ=9F, =8F, —=97)
    ('\u00f0\u0178\u008f\u2014', '\U0001f3d7'),
    # 🥇 U+1F947  F0 9F A5 87 → ðŸ¥‡
    ('\u00f0\u0178\u00a5\u2021', '\U0001f947'),
    # 🪙 U+1FA99  F0 9F AA 99 → ðŸªš  (approximation)
    ('\u00f0\u0178\u00aa\u2122', '\U0001fa99'),
    # 🏦 U+1F3E6  F0 9F 8F A6 → ðŸ¦
    ('\u00f0\u0178\u008f\u00a6', '\U0001f3e6'),
    # 💻 U+1F4BB  F0 9F 92 BB → ðŸ'»
    ('\u00f0\u0178\u2019\u00bb', '\U0001f4bb'),
    # 💰 U+1F4B0  F0 9F 92 B0 → ðŸ'°
    ('\u00f0\u0178\u2019\u00b0', '\U0001f4b0'),
    # 🔄 U+1F504  F0 9F 94 84 → ðŸ"„
    ('\u00f0\u0178\u201d\u201e', '\U0001f504'),
    # 🔍 U+1F50D  F0 9F 94 8D → ðŸ"
    ('\u00f0\u0178\u201d\u2039', '\U0001f50d'),
    # 🛡️ U+1F6E1  F0 9F 9B A1 → ðŸ›¡  (shield)
    ('\u00f0\u0178\u009b\u00a1', '\U0001f6e1'),
    # 📝 U+1F4DD  F0 9F 93 9D → ðŸ"
    ('\u00f0\u0178\u201c\u009d', '\U0001f4dd'),
    # 🏛️ U+1F3DB  F0 9F 8F 9B → ðŸ›
    ('\u00f0\u0178\u008f\u009b', '\U0001f3db'),
    # 🇮🇳 flag - complex, skip
    # ☑️ ✅ etc - skip complex emoji
]

def fix_text(text: str) -> str:
    for bad, good in FIXES:
        if bad in text:
            text = text.replace(bad, good)
    return text

def process_files(pattern_list):
    fixed = 0
    clean = 0
    for pattern in pattern_list:
        for f in sorted(ROOT.glob(pattern)):
            try:
                orig = f.read_text(encoding='utf-8')
            except Exception as e:
                print(f'  ERROR reading {f.name}: {e}')
                continue
            updated = fix_text(orig)
            if updated != orig:
                f.write_text(updated, encoding='utf-8')
                print(f'  FIXED  {f.relative_to(ROOT)}')
                fixed += 1
            else:
                clean += 1
    return fixed, clean

print('=== Checking & fixing encoding across all file types ===')
print()

f1, c1 = process_files(['*.html'])
print(f'HTML:    {f1} fixed, {c1} clean')

f2, c2 = process_files(['etf/*.json', 'indices/*.json', 'json/*.json'])
print(f'JSON:    {f2} fixed, {c2} clean')

print()
print('Done.')

# self-delete
Path(__file__).unlink()
