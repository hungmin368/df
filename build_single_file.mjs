// One-off build tool: bundle the whole Dragon Finder app into one self-contained HTML file.
// Usage: node build_single_file.mjs   →  dragonfinder_v<VERSION>.html
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { extname } from 'node:path';
import { execSync } from 'node:child_process';

const htmlSrc = readFileSync('index.html', 'utf8');
const m = htmlSrc.match(/v(\d+\.\d+\.\d+)/);
if (!m) throw new Error('version not found in index.html');
const VERSION = m[1];
const OUT = `dragonfinder_v${VERSION}.html`;

let commit = 'unknown';
try { commit = execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim(); } catch {}

const MIME = {
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2',
};

function dataUri(file) {
  const b64 = readFileSync(file).toString('base64');
  return `data:${MIME[extname(file).toLowerCase()]};base64,${b64}`;
}

// ---------- collect assets ----------
const dinos = {};
for (const f of readdirSync('assets/dinos')) {
  const d = f.match(/^(\d+)\.webp$/);
  if (d) dinos[d[1]] = dataUri('assets/dinos/' + f);
}

const buddy = {};
for (const f of readdirSync('assets/dinos_2')) buddy['assets/dinos_2/' + f] = dataUri('assets/dinos_2/' + f);

const story = {};
for (const f of readdirSync('assets/story')) {
  const s = f.match(/^s(\d+)\.svg$/);
  if (s) story[s[1]] = dataUri('assets/story/' + f);
}

const gameLogo = dataUri('assets/dinos_2/game_logo.png');
const cursor = dataUri('assets/cursor.png');
const mapBg = dataUri('assets/map.png');
const huninn = dataUri('assets/fonts/Huninn.woff2');
const iansui = dataUri('assets/fonts/Iansui.woff2');

// ---------- inline css ----------
const fontsCss = readFileSync('css/fonts.css', 'utf8')
  .replaceAll('url(../assets/fonts/Huninn.woff2)', `url("${huninn}")`)
  .replaceAll('url(../assets/fonts/Iansui.woff2)', `url("${iansui}")`);

const styleCss = readFileSync('css/style.css', 'utf8')
  .replaceAll("url('../assets/cursor.png')", `url("${cursor}")`)
  .replaceAll("url('../assets/map.png')", `url("${mapBg}")`);

// ---------- inline js ----------
const storyMap =
  `const __STORY_IMG_MAP=${JSON.stringify(story)};\n` +
  `function __storyImg(n){ return __STORY_IMG_MAP[n] || ""; }\n`;

let dataJs = readFileSync('js/data.js', 'utf8');
dataJs = dataJs.replace(/"img"\s*:\s*"assets\/dinos\/(\d+)\.webp"/g, (mm, id) => {
  if (!dinos[id]) throw new Error('missing dino image: ' + id);
  return `"img":"${dinos[id]}"`;
});
dataJs = dataJs.replace("'use strict';", "'use strict';\n" + storyMap);

const towerJs = readFileSync('js/tower.js', 'utf8');

let mainJs = readFileSync('js/main.js', 'utf8');
for (const [p, uri] of Object.entries(buddy)) {
  if (!mainJs.includes(`'${p}'`)) continue; /* 未被 main.js 引用的素材（備用圖、只給 index.html 用的 logo）不內嵌 */
  mainJs = mainJs.split(`'${p}'`).join(`'${uri}'`);
}
mainJs = mainJs
  .replaceAll("'assets/story/s'+(s.lv||0)+'.svg'", '__storyImg(s.lv||0)')
  .replaceAll("'url(assets/story/s'+(s.lv||0)+'.svg)'", "'url('+__storyImg(s.lv||0)+')'");

// ---------- sanity checks ----------
for (const [name, src] of [['data.js', dataJs], ['tower.js', towerJs], ['main.js', mainJs], ['fonts.css', fontsCss], ['style.css', styleCss]]) {
  if (/['"(]assets\//.test(src)) throw new Error(`leftover asset reference in ${name}`);
}

// ---------- assemble html ----------
const favicon = 'data:image/svg+xml,' + encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="0.9em" font-size="90">\u26a1</text></svg>`);

let html = htmlSrc
  .replace('<link rel="stylesheet" href="css/fonts.css?v=' + VERSION + '">', () => `<style>\n${fontsCss}</style>`)
  .replace('<link rel="stylesheet" href="css/style.css?v=' + VERSION + '">', () => `<style>\n${styleCss}</style>`)
  .replace('<script src="js/data.js?v=' + VERSION + '"></script>', () => `<script>\n${dataJs}</script>`)
  .replace('<script src="js/tower.js?v=' + VERSION + '"></script>', () => `<script>\n${towerJs}</script>`)
  .replace('<script src="js/main.js?v=' + VERSION + '"></script>', () => `<script>\n${mainJs}</script>`)
  .split('src="assets/dinos_2/game_logo.png"').join(`src="${gameLogo}"`)
  .replace('<meta name="theme-color" content="#fffdf9">',
    `<meta name="theme-color" content="#fffdf9">\n<link rel="icon" href="${favicon}">`)
  .replace('<!DOCTYPE html>', `<!DOCTYPE html>\n<!-- 尋龍高手 DragonFinder v${VERSION} 單檔封裝版（build_single_file.mjs 自動生成於 2026-09-24，來源 commit ${commit}）。完全自給自足，無外部資源引用，可直接以瀏覽器開啟。 -->`);

if (/(src|href)="(css|js|assets)\//.test(html)) throw new Error('leftover external reference in html');

writeFileSync(OUT, html);
console.log(`${OUT} written (${(html.length / 1024 / 1024).toFixed(1)} MB, ${html.length} chars)`);
