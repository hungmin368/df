# Worklog：龍塔（預生成盤面闖關）

- 日期：2026-09-23
- 任務 ID：dragon-tower
- 需求：在地圖未使用的區塊增加「龍塔」，內用預生成盤面闖關；過關才能進下一關；預生成不做旋轉/鏡像變體；地圖其他區域維持即時生成。

## 盤面數量與關卡編號（依需求）

| 尺寸 | 預生成數 | 關卡編號 |
|---|---|---|
| 6×6 | 10 | 1–10 |
| 7×7 | 20（見下方註） | 11–20 |
| 8×8 | 30 | 21–50 |
| 9×9 | 50 | 51–100 |
| 10×10 | 200 | 101–300 |
| 11×11 | 400 | 301–700 |
| 12×12 | 600 | 701–1300 |
| 13×13 | 700 | 1301–2000 |

註：需求中 7×7「預生成 20 個」與「關卡 11 到 20」（共 10 關）數量不一致；其餘尺寸數量皆與關卡數相符。採用「單一筆誤」假設：以關卡範圍為準，7×7 生成 10 個盤面（1:1）。共 2000 關 / 2000 盤。

## 執行步驟記錄

### 1. 研讀程式碼（完成）
- main.js 為單一 194KB 檔；index.html 只載入 js/data.js + js/main.js。
- 盤面生成器：`randomRegions`（main.js:105）、`solve2`（main.js:140）、`generatePuzzle`（main.js:178）；POOL_DATA（main.js:258）為 10~14 的預生成 regionOf 池（CSV），執行期以 `transformBoard` 做旋轉/鏡像——龍塔不使用此函數（需求：不用旋轉/鏡像）。
- 地圖：`renderMap`（main.js:2793）只繪製 4~13 區塊；14~18 區塊（MAP_REGIONS main.js:406）為未使用死區，其中 18（蒼穹龍境，頂部中央天空帶 x34-64/y0-22）預計作為龍塔位置。
- 過關：`winRound`（main.js:2287）＋ monkey-patch（main.js:938）；存檔 key 皆 `dinodoku-*`；`wipeAllRecords` 掃描前綴，`dev-wipe` 為固定清單（需加新 key）。
- index.html 有未提交版本號修改（1.9.3→1.9.6），與本任務無衝突，保留不動。

### 2. 預生成腳本 tmp_gen_tower.js（完成）
- 以 tmp_test_gen.js 同款技法從 main.js 截取 `function shuffle`～`const POOL_DATA` 間的生成器程式碼（eval），保證與遊戲內生成器逐字一致。
- 只收「純唯一解」盤：`generatePuzzle(N, 20000, true)`（noChest 跳過關鍵寶箱路徑），再以 `solve2` 複驗恰 1 解且與 pz.cats 一致；N≤9 另以獨立枚舉器 bruteUnique 交叉驗證。
- D4 去重：對 (regionOf, 解) 做 8 變換（轉置/翻轉，同 transformBoard 規則），區塊依讀序重編後取字典序最小當 key；key 重複即棄盤（不使用旋轉/鏡像產生變體）。
- 存檔格式：每盤為 regionOf 的 base36 字串（長 N×N），暫存 tmp_tower_<N>.json（含 key，可續跑），完成後彙整為 js/tower.js（TOWER_START/TOWER_COUNTS/TOWER_TOTAL/TOWER_DATA）。
- 6×6 試跑：10 盤 10 次嘗試 0 秒完成。背景全量執行中。

### 3. 遊戲端實作（完成，語法檢查通過）
- js/tower.js：由腳本生成；index.html 於 data.js 之後、main.js 之前引入。
- main.js：
  - TOWER 狀態（`dinodoku-tower` 只存 max；level 為進行中關卡不存檔）＋ towerSizeOf/towerDecode 工具。
  - TOWER_GEO：龍塔地標＝未繪製的 18 區頂部天空帶多邊形（renderMap 最上層繪製，永遠可進，副標顯示通關進度）。
  - renderMap 點擊：navFromEvent/regionAt/keydown 優先辨識龍塔（pointer 事件與鍵盤皆可）。
  - newBoard 塔分支置頂：直接用預生成盤面（不旋轉/不鏡像）、solve2 取解；資料異常時退回一般生成。
  - 過關（winRound patch）：TOWER.max 解鎖至過關層；res-next 過關→下一層（跨尺寸自動換 N），失敗→重試同一層同一盤；res-menu→回龍塔選關。
  - openLevel/dev-jump/res-lv 一律清除 TOWER.level（一般區域維持即時生成）。
  - HUD 局號顯示「塔N」；ov-tower overlay（尺寸分頁 8 頁＋關卡格，已通關/下一層/鎖定三態）。
  - dev-wipe 固定清單加入 dinodoku-tower（wipeAllRecords 本即掃前綴）。
- css/style.css：.mtower 地標樣式（脈動邊線）、#tower-tabs/#tower-grid/.tlv 三態樣式。

### 4. 全量預生成與資料驗證（完成）
- 背景執行 `node tmp_gen_tower.js`（可斷點續跑）已跑完：8 種尺寸共 2000 盤全部生成完畢，js/tower.js 280KB。
- js/tower.js 內容：TOWER_START{6:1,7:11,8:21,9:51,10:101,11:301,12:701,13:1301}、TOWER_COUNTS{6:10,7:10,8:30,9:50,10:200,11:400,12:600,13:700}、TOWER_TOTAL=2000；每筆為長 N×N 的 base36 regionOf 字串。
- 資料驗證腳本 tmp_check_tower.js（獨立於生成器）檢查：每盤 solve2 恰 1 解、區塊數＝N、每區塊 ≥2 格且連通、同尺寸任兩盤不為 D4 旋轉/鏡像等價、數量符合規格。
  - 修正：`const` 宣告不會自 eval 洩漏，改以 var 取出 TOWER_DATA；eval 變數名稱衝突修正。
  - 結果：6×6、7×7、8×8、9×9、10×10、11×11、12×12、13×13 全部通過（ALL OK，對最終版 tower.js 複驗）。

### 5. 瀏覽器實測（localhost:8000，python http.server；完成）
- 全部資源 HTTP 200（index/data/tower/main/style.css/map.png/logo.png，tower.js 280KB）。
- 首載：TOWER_DATA 2000 盤載入、龍塔地標出現在地圖頂部天空帶；序章故事可跳過。
- 點地標（真實 pointerdown/up 事件路徑）→ ov-tower 開啟：8 尺寸分頁、預設停在下一層尺寸。
- 第 1 層：盤面與 TOWER_DATA["6"][0] 逐格一致、HUD「塔1」、36 格、state=marking。
- 第 1 層完整實玩：進入捕捉器模式後以真實 click 逐格捕獲 6 隻 → 過關（state=ending→done）、結果頁「過關！」、dinodoku-tower={max:1} 寫入。
- 模擬過關（winRound 真實路徑）：「下一局 ▶」→ 第 2 層自動開始（盤面=["6"][1]）。
- 鎖定防護：全新存檔（max=0）下選關格 1=next、其餘 locked；towerStart(9) 於 max=0 時被拒（層級不變）；max=1 時 towerStart(5) 亦被拒。
- 重新載入：max 保留、進行中層重置、地標副標「✓ 已通關 N 層」、選關格狀態依 max 重建。
- 尺寸邊界：第 10 層過關→「下一局」自動進第 11 層（7×7，盤面=["7"][0]）；第 700 層過關→「下一局」自動進第 701 層（12×12，盤面=["12"][0]）。
- 大尺寸：第 101 層（10×10，balls=13）、第 1300 層（12×12，最後一盤）、第 1301 層（13×13，第一盤，169 格、solve2 執行期 56ms、計時 390s、balls=16）、第 2000 層（13×13，最後一盤 index 699）皆與 TOWER_DATA 完全一致且執行期複驗唯一解。
- 失敗重試：G.lastFail 時按「下一局 ▶」→ 同層同盤面重開（盤面字串一致、標記清空）。
- 全塔完成：第 2000 層過關 → max=2000 →「下一局 ▶」回到龍塔選關（不會嘗試第 2001 層），13×13 分頁 700 格全為 done、副標「已通關 2000 / 2000 層 🎉」。
- 地圖區域 6（openLevel 真實路徑）：TOWER.level 歸零、HUD 顯示局數「1」、盤面為即時生成（不在塔資料中）、執行期唯一解 → 其他區域維持原即時生成。
- 載入期間 console 無任何與龍塔相關的 JS 錯誤（僅瀏覽器 session 中其他來源的歷史紀錄）。

## 最終狀態
- 交付：js/tower.js（2000 盤，8 尺寸）、js/main.js 龍塔模組、index.html（ov-tower＋引入 tower.js）、css/style.css（龍塔樣式）、本工作日志。
- 驗證：tmp_check_tower.js 全尺寸 ALL OK（唯一解／連通／區塊≥2 格／D4 去重／數量）；HTTP 資產全 200；瀏覽器實測逐項通過。
- 需求對照：地圖未使用區塊（18 區天空帶）設龍塔 ✅；預生成盤面闖關 ✅；尺寸數量依規格（7×7 以關卡數 10 為準）✅；過關才解鎖下一層 ✅；預生成不使用旋轉/鏡像 ✅；地圖其他區域維持即時生成 ✅。
- Commit：<待補>
