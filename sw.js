/* 恐龍快找 DragonFinder service worker
   策略：核心檔預快取（安裝時從 index.html 與 data.js 動態收集資產清單）；
   導覽 network-first（離線回退快取），其餘 GET stale-while-revalidate，
   影片（mp4）同 SWR 但跳過 Range 請求以免影響播放定位。 */
const VERSION = 'v1.9.17';
const CACHE = 'df-' + VERSION;

const CORE = [
  './',
  'index.html',
  'manifest.webmanifest',
  'css/fonts.css?v=1.9.17',
  'css/style.css?v=1.9.17',
  'js/data.js?v=1.9.17',
  'js/tower.js?v=1.9.17',
  'js/main.js?v=1.9.17',
  'js/tower_comments.js?v=1.9.17',
  'js/ads.js?v=1.9.17',
  'assets/fonts/Huninn.woff2',
  'assets/fonts/Iansui.woff2',
  'assets/cursor.png',
  'assets/map.png',
  'assets/dinos_2/game_logo.png',
  'CHANGELOG.md'
];

/* 從 index.html 與 data.js 收集 assets/ 引用（data.js 內含 139 張恐龍圖路徑） */
async function collectAssets() {
  const found = new Set(CORE);
  const re = /assets\/[A-Za-z0-9_\-./]+?\.(?:webp|png|jpg|svg|woff2)/g;
  for (const url of ['index.html', 'js/data.js?v=1.9.17', 'css/style.css?v=1.9.17']) {
    try {
      const t = await (await fetch(url, { cache: 'no-cache' })).text();
      for (const m of t.match(re) || []) found.add(m);
    } catch (e) { /* 收集失敗不阻擋安裝 */ }
  }
  // 影片不預快取（體積大），留待執行期快取
  for (const u of Array.from(found)) {
    if (/\.mp4$/.test(u)) found.delete(u);
  }
  return Array.from(found);
}

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const list = await collectAssets();
    const cache = await caches.open(CACHE);
    await Promise.allSettled(list.map((u) => cache.add(u)));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  // 影片 Range 請求直接走網路，避免快取整份 response 影響播放
  if (req.headers.has('range')) return;

  // 導覽：network-first，離線回退快取
  if (req.mode === 'navigate') {
    e.respondWith((async () => {
      try {
        const net = await fetch(req);
        const c = await caches.open(CACHE);
        c.put('index.html', net.clone());
        return net;
      } catch (err) {
        const hit = await caches.match('index.html');
        if (hit) return hit;
        throw err;
      }
    })());
    return;
  }

  // 其餘 GET：stale-while-revalidate
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(req, { ignoreSearch: true });
    const net = fetch(req).then((res) => {
      if (res && res.ok) cache.put(req, res.clone());
      return res;
    }).catch(() => null);
    return hit || (await net) || Response.error();
  })());
});
