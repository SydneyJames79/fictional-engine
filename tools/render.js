// Rasterize an SVG with headless Chromium via Playwright.
// Usage: node tools/render.js <in.svg> <out.png> [width=1616] [background=transparent]
const fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); }
catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }

(async () => {
  const [,, inSvg, outPng, widthArg, bgArg] = process.argv;
  if (!inSvg || !outPng) { console.error('usage: node tools/render.js <in.svg> <out.png> [width] [background]'); process.exit(2); }
  const width = parseInt(widthArg || '1616', 10);
  const bg = bgArg || 'transparent';
  const svg = fs.readFileSync(inSvg, 'utf8');
  const m = svg.match(/viewBox="([^"]+)"/);
  const vb = m ? m[1].trim().split(/[\s,]+/).map(Number) : [0, 0, 1616, 1076];
  const height = Math.round(width * vb[3] / vb[2]);
  const launch = { args: ['--no-sandbox'] };
  if (fs.existsSync('/opt/pw-browsers/chromium')) launch.executablePath = '/opt/pw-browsers/chromium';
  const browser = await chromium.launch(launch);
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  const sized = svg.replace(/<svg([^>]*)>/, (s, a) =>
    `<svg${a.replace(/\swidth="[^"]*"/, '').replace(/\sheight="[^"]*"/, '')} width="${width}" height="${height}">`);
  await page.setContent(`<!doctype html><html><body style="margin:0;background:${bg}">${sized}</body></html>`, { waitUntil: 'load' });
  await page.screenshot({ path: outPng, omitBackground: bg === 'transparent' });
  await browser.close();
  console.log(`rendered ${inSvg} -> ${outPng} (${width}x${height}, background ${bg})`);
})().catch(e => { console.error(e); process.exit(1); });
