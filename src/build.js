const fs   = require('fs');
const path = require('path');

const dev          = process.argv.includes('--dev');
const minifyOnly   = process.argv.includes('--minify-only');
const srcDir       = __dirname;
const root         = path.join(srcDir, '..');
const inputPath    = path.join(srcDir, 'input.html');
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
if (!fs.existsSync(inputPath)) {
  console.error(`Missing required file: ${path.basename(inputPath)}`);
  process.exit(1);
}

// ── Copy input.html to index.html ─────────────────────────────────────────────
let out = fs.readFileSync(inputPath, 'utf8');

// ── Minify (production only) ──────────────────────────────────────────────────
if (!dev) out = minify(out);

fs.writeFileSync(outputPath, out, 'utf8');
console.log(`Built index.html [${dev ? 'dev' : 'production'}]`);
