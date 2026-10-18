# Worklog — 9A 共同項目施工（9a-common-prep）

- 任務：依序完成 9 個「🤖 我可獨立完成」的共同項目：A14 → A16 → A02 → A04 → A03 → A01 → A13 → A15 → A12。
- 日期：2026-10-17
- 任務 ID：9a-common-prep
- 本檔同時是**驗收記憶**：中斷後對我說「**檢查9A**」，我會讀此檔，從第一個非 ✅ 項目繼續，直到全部 ✅。

## 恢復協議（說「檢查9A」時執行）

1. 讀本檔狀態表，找到第一個非 ✅ 項目。
2. 先檢查該項「修改檔案」的磁碟現況（可能部分完成），比對「驗收標準」逐條確認。
3. 已完成的補驗收並標 ✅；未完成的繼續施工；之後依序推進。
4. 全部 ✅ 後跑「整體迴歸」（第十四項），再回報。
5. 規則：每完成一項立即更新狀態表與對應小節（不可事後補記）；遊戲程式碼異動後必做最小迴歸（本機 HTTP 開頁、主選單、進一關、console 無錯）。

## 狀態表（唯一事實來源）

| 順序 | ID | 內容 | 狀態 | 完成時間 |
|---|---|---|---|---|
| 1 | A14 | og/twitter/description meta | ✅ | 2026-10-17 |
| 2 | A16 | CHANGELOG.md | ✅ | 2026-10-17 |
| 3 | A02 | manifest.webmanifest | ✅ | 2026-10-17 |
| 4 | A04 | 圖標尺寸組 | ✅ | 2026-10-17 |
| 5 | A03 | service worker | ✅ | 2026-10-17 |
| 6 | A01 | build_dist.py 出貨包 | ✅ | 2026-10-17 |
| 7 | A13 | 載入效能（影片延後＋lazy） | ✅ | 2026-10-17 |
| 8 | A15 | 遊戲內關於/授權頁 | ✅ | 2026-10-17 |
| 9 | A12 | js/ads.js 廣告節點 | ✅ | 2026-10-17 |
| 10 | — | 整體迴歸收尾 | ✅ | 2026-10-17 |

圖例：⬜ 未做 / 🔨 進行中 / ✅ 已完成且已驗收

## 完成紀錄（2026-10-17 一次施工完成並驗收）

- A14：`index.html` head 加入 description、og:title/description/type/url/locale/image、twitter:card，值已核對。
- A16：新建 `CHANGELOG.md`，首筆 `[1.9.17] - 2026-10-17` 內容取自 git log 真實紀錄，版本號與 UI ver-badge 一致。
- A02：新建 `manifest.webmanifest`（standalone、theme `#fffdf9`、icons 指向 A04 產物），`index.html` 已掛 `<link rel="manifest">`。
- A04：`assets/icons/` 產出 favicon.ico（16/32/48）、favicon-48、apple-touch-icon 180、icon-192、icon-512、icon-512-maskable（內容 78% 置中於 #fffdf9 底）；Pillow 12.3.0 縮放；目視確認龍圖正確。
- A03：`sw.js`（CACHE `df-v1.9.17`，安裝時解析 index.html/data.js/css 收集 assets 清單預快取、mp4 排除並走 SWR、Range 請求直通）；`index.html` 註冊。驗收：caches.keys=`[df-v1.9.17]`、預快取 158 筆、**關閉伺服器後重整頁面主選單與地圖仍正常（swControlled=true）**。
- A01：`build_dist.py` 執行成功：dist 178 檔、25.1MB、所有 assets/ 引用核對 `[OK]`（修掉結尾 ✓ 字元在 cp950 主控台崩潰的問題）；dist 可獨立 HTTP 200。
- A13：`intro-vid` preload 改 `metadata`（main.js 播放時機已確認不需 auto）；兩處圖鑑 grid 的 img 加 `loading="lazy" decoding="async"`；map.png 不動（視覺變更待你確認）。
- A15：主選單第 6 鍵「關於」＋`ov-about` overlay（版本、字型 OFL、AI 揭露、隱私、CHANGELOG 連結）；CSS grid 5→6 欄；開關驗收含截圖。
- A12：新建 `js/ads.js`（偵測 CrazyGames→GD，無 SDK 降級）；`index.html` 掛載；`newBoard` 接 gameplayStart、4 處結果畫面接 gameplayStop、`res-next` 包 `Ads.break`。驗收：無 SDK 時過關→下一局流程逐點正常（36 格新盤、第 2 局）；注入 CrazyGames stub 後 `__adsLog=[init,loadingStop,gps,gpstop,ad:midgame,break-cb]` 全部正確。
- 整體迴歸：主選單 6 鍵、關於開關、進 4×4 盤、6×6 過關→下一局、離線重開、SW 快取、廣告雙路徑——全部通過，無遊戲本身的 console 錯誤（僅見 MCP 注入腳本的 evaluate 包裝錯誤與他埠舊錯誤）。
- 未 commit，等你確認。

---

## A14 — og/twitter/description meta
- 修改檔案：`index.html`（head）
- 內容：`<meta name="description">`、`og:title`、`og:description`、`og:type=website`、`og:url=https://hungmin368.github.io/df/`、`og:locale=zh_TW`、`og:image`（用絕對網址指向 logo 圖）、`twitter:card=summary_large_image`。
- 驗收標準：① 原始碼可見全部標籤；② 值正確無空值；③ 不影響遊戲載入。
- 狀態：⬜

## A16 — CHANGELOG.md
- 修改檔案：`CHANGELOG.md`（新建）
- 內容：格式說明（語意化版本、日期）、首筆 v1.9.17 條目（內容取 git log 近期真實紀錄）、註明更早歷史見 git log 與 worklogs。
- 驗收標準：① 檔案存在；② 頂部版本號與 UI ver-badge（index.html 內 v1.9.17）一致。
- 狀態：⬜

## A02 — manifest.webmanifest
- 修改檔案：`manifest.webmanifest`（新建）、`index.html`（掛 link）
- 內容：name「恐龍快找 DragonFinder」、short_name「恐龍快找」、start_url `.`、scope `.`、display `standalone`、background_color/theme_color `#fffdf9`（與現有 theme-color 一致）、icons 192/512/maskable（路徑指向 A04 產物）。
- 驗收標準：① 合法 JSON；② index.html 有 `<link rel="manifest">`；③ 圖標檔於 A04 完成後存在。
- 狀態：⬜

## A04 — 圖標尺寸組
- 修改檔案：新建 `assets/icons/`（favicon.ico、favicon-48.png、apple-touch-icon.png 180×180、icon-192.png、icon-512.png、icon-512-maskable.png）、`index.html`（icon link）、`manifest.webmanifest`（icons 陣列）
- 內容：以 `app_icon.png`（1254×1254）縮放產出；maskable 版加安全邊距與白底；工具用 python+Pillow（無則裝或改 Node 方案）。
- 驗收標準：① 各檔尺寸正確；② index.html 引用 favicon 與 apple-touch-icon；③ manifest icons 全部可 200 取得。
- 狀態：⬜

## A03 — service worker
- 修改檔案：`sw.js`（新建）、`index.html`（註冊腳本）
- 內容：CACHE 名 `df-v1.9.17`；install 預快取：index.html、css、js（main/tower/tower_comments/data）、fonts、cursor、map.png、story svgs、assets/dinos/*.webp、logo 圖（不含 mp4）；activate 清舊版快取；fetch：導覽 network-first  fallback cache，其餘 cache-first，mp4 執行期快取（限制只快取成功 response）。
- 驗收標準：① 註冊成功（evaluate `navigator.serviceWorker.controller` 或 registration 存在）；② `caches.keys()` 含 `df-v1.9.17` 且預快取數 >100；③ 關網路重開仍見主選單（或至少 fetch 靜態檔回 cache）。
- 狀態：⬜

## A01 — build_dist.py 出貨包
- 修改檔案：`build_dist.py`（新建，放倉庫根，一次性維護工具）
- 內容：清空並重建 `dist/`；複製 index.html、css/、js/（排除 *.bak*）、assets/fonts、dinos、story、map.png、cursor.png、game.mp4、story_lv4_720p.mp4、dinos_2/game_logo.png；列印檔數與總大小；不做 minify（保持無建置依賴精神）。
- 驗收標準：① 執行成功；② dist 總大小 <30MB；③ 本機 HTTP 下 dist/index.html 與抽樣資產（含 game_logo.png、dino webp、字體）皆 200；④ 對 index.html/css/js 內所有 assets/ 引用逐一確認 dist 內存在。
- 狀態：⬜

## A13 — 載入效能
- 修改檔案：`index.html`（intro video preload）、`js/main.js`（恐龍圖 img 加 loading="lazy"，找 createElement('img')/innerHTML 產圖處）
- 內容：① `<video id="intro-vid">` 的 `preload="auto"` → `"metadata"`（若主選單流程需要即播，配合 main.js 在要播時才 load，先看 main.js:3213 附近用法再定）；② 所有動態產生的恐龍/卡面 img 加 `loading="lazy"` 與 `decoding="async"`；③ `map.png` 本階段不動（視覺變更需你確認，列為後續選項）。
- 驗收標準：① 屬性正確；② 主選單→進關→回主選單流程無異常、console 無錯；③ 首屏（index+css+js+字體）不再含 2.4MB 影片搶頻寬（檢查 preload 值與網路時序即可）。
- 狀態：⬜

## A15 — 遊戲內關於/授權頁
- 修改檔案：`index.html`（主選單加「關於」按鈕＋overlay 結構）、`css/style.css`（overlay 樣式）、`js/main.js`（開關邏輯）
- 內容：overlay 顯示：遊戲名＋版本號（與 ver-badge 一致）、字型授權（jf open 粉圓／粉圓，OFL，可商用重散布）、AI 生成素材說明、CHANGELOG.md 連結（GitHub Pages 絕對網址）、關閉按鈕。
- 驗收標準：① 主選單可開關；② 內容正確含三要素；③ 開關不影響遊戲流程、console 無錯。
- 狀態：⬜

## A12 — js/ads.js 廣告節點
- 修改檔案：`js/ads.js`（新建）、`index.html`（script 引用，放 main.js 之前）、`js/main.js`（節點接入）
- 內容：統一 API：`Ads.init()`、`Ads.break(cb)`（插頁，cb 於廣告結束或無 SDK 時呼叫）、`Ads.gameplayStart()`、`Ads.gameplayStop()`；偵測 `window.CrazyGames.SDK` 與 GD SDK，優先 CrazyGames；無 SDK 全部降級為立即回調。節點：一般關卡過關結算後繼續、龍塔失敗重試、龍塔過關後。
- 驗收標準：① 無 SDK 時主流程與原版逐點一致（進關、過關、重試、回主選單）；② 用 evaluate 注入 stub（`window.__adsLog` 記錄）後過關，`__adsLog` 出現 break 記錄；③ console 無錯。
- 狀態：⬜

## 整體迴歸（全部 ✅ 後執行）
- 本機 HTTP 開遊戲：主選單→進一關→過關→回主選單→開關於頁；console 無錯；SW 註冊且快取存在；dist/ 可獨立伺服並可玩；九項狀態全 ✅。
- 注意：`js/main.js` 是 216K 大檔，異動一律走 Edit 最小差異；完成後不 commit（等你確認）。
