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

// ── Load ETF configuration ────────────────────────────────────────────────────
const configPath = path.join(srcDir, 'etf-config.json');
let etfConfig = { etfFiles: [] };
if (fs.existsSync(configPath)) {
  const configContent = fs.readFileSync(configPath, 'utf8');
  etfConfig = JSON.parse(configContent);
}

// ── Copy etf folder to root ───────────────────────────────────────────────────
const srcEtfDir = path.join(srcDir, 'etf');
const destEtfDir = path.join(root, 'etf');

// Create etf directory in root if it doesn't exist
if (!fs.existsSync(destEtfDir)) {
  fs.mkdirSync(destEtfDir, { recursive: true });
}

// Copy ETF JSON files listed in config
if (fs.existsSync(srcEtfDir)) {
  let copiedCount = 0;
  etfConfig.etfFiles.forEach(file => {
    const srcFile = path.join(srcEtfDir, file);
    const destFile = path.join(destEtfDir, file);
    if (fs.existsSync(srcFile)) {
      fs.copyFileSync(srcFile, destFile);
      copiedCount++;
    } else {
      console.warn(`  Warning: ETF file not found: ${file}`);
    }
  });
  console.log(`Copied ${copiedCount} ETF JSON files (from config)`);
  
  // Also copy the config file itself
  fs.copyFileSync(configPath, path.join(root, 'etf-config.json'));
  console.log(`Copied etf-config.json`);
}

// ── Copy etf-prices.json to root ──────────────────────────────────────────────
const pricesPath = path.join(srcDir, 'etf-prices.json');
if (fs.existsSync(pricesPath)) {
  fs.copyFileSync(pricesPath, path.join(root, 'etf-prices.json'));
}

// ── Minify (production only) ──────────────────────────────────────────────────
if (!dev) out = minify(out);

fs.writeFileSync(outputPath, out, 'utf8');
console.log(`Built index.html [${dev ? 'dev' : 'production'}]`);
