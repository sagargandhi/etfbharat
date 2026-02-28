const fs   = require('fs');
const path = require('path');

const dev          = process.argv.includes('--dev');
const minifyOnly   = process.argv.includes('--minify-only');
const srcDir       = __dirname;
const root         = path.join(srcDir, '..');
const inputPath    = path.join(srcDir, 'input.html');
const dataPath     = path.join(srcDir, 'etf-data.json');
const pricesPath   = path.join(srcDir, 'etf-prices.json');
const outputPath   = path.join(root, 'index.html');

// ── Minify helper ─────────────────────────────────────────────────────────────
function minify(html) {
  return html
    .replace(/<!--[\s\S]*?-->/g, '')   // strip HTML comments
    .replace(/[ \t]+/g, ' ')           // collapse horizontal whitespace
    .replace(/\n\s*/g, '\n')           // trim leading whitespace on each line
    .replace(/\n{2,}/g, '\n')          // collapse blank lines
    .trim();
}

// ── Minify-only mode: minify existing index.html in place ────────────────────
if (minifyOnly) {
  if (!fs.existsSync(outputPath)) {
    console.error('index.html not found — run build first');
    process.exit(1);
  }
  const before = fs.readFileSync(outputPath, 'utf8');
  const after  = minify(before);
  fs.writeFileSync(outputPath, after, 'utf8');
  const saved = ((before.length - after.length) / before.length * 100).toFixed(1);
  console.log(`Minified index.html — ${saved}% reduction (${before.length} → ${after.length} bytes)`);
  process.exit(0);
}

// ── Validate inputs ───────────────────────────────────────────────────────────
[inputPath, dataPath, pricesPath].forEach(p => {
  if (!fs.existsSync(p)) {
    console.error(`Missing required file: ${path.basename(p)}`);
    process.exit(1);
  }
});

// ── Load & merge data ─────────────────────────────────────────────────────────
const etfs   = JSON.parse(fs.readFileSync(dataPath,   'utf8'));
const prices = JSON.parse(fs.readFileSync(pricesPath, 'utf8'));

const merged = etfs.map(etf => {
  const p = prices[etf.ticker];
  if (p) return { ...etf, aum: p.aum, expense: p.expense, nav: p.nav };
  return etf;
});

// ── Inject data into template ─────────────────────────────────────────────────
const input = fs.readFileSync(inputPath, 'utf8');

if (!/<!--\s*INJECT_ETF_DATA\s*-->/.test(input)) {
  console.error('Placeholder <!-- INJECT_ETF_DATA --> not found in input.html');
  process.exit(1);
}

const script = `<script>const ETF_DATA = ${JSON.stringify(merged)};</script>`;
let out = input.replace(/<!--\s*INJECT_ETF_DATA\s*-->/, script);

// ── Minify (production only) ──────────────────────────────────────────────────
if (!dev) out = minify(out);

fs.writeFileSync(outputPath, out, 'utf8');
console.log(`Built index.html — ${merged.length} ETFs [${dev ? 'dev' : 'production'}]`);
