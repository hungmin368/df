# Worklog：修正開場 logo 飛入選單時「到位急縮小」

- 日期：2026-09-24
- 任務 ID：logo-fly-shrink
- 需求：進遊戲時 logo 由畫面中央飛向主選單左上，到達定位時會突然急縮一下；希望到位時不要急縮。

## 步驟記錄

### 1. 定位動畫實作
- `js/main.js:3042-3081`：`#splash` 開場 IIFE。圖片載入後停 500ms（`HOLD`），接著 `fly()` 以 680ms（`FLY`）transition 將 logo 飛往 `#menu-logo img`，`FLY+60ms` 後 `finish()` 移除 splash 並讓真選單 logo 顯示。
- `css/style.css:1209-1221`：`#splash img` 以 `height:min(34.72vw,213.04px,62vh)` 等比顯示；`#menu-logo img`（`css/style.css:1147-1149`、手機版 1182）固定在 `186×73.38px`（手機 `150×59.20px`）盒子內用 `object-fit:contain`。
- 量測素材：`assets/dinos_2/game_logo.png` 為 1536×1024（比例 1.5）；選單盒子比例 2.535 → contain 後實際可見寬只有 `73.38×1.5 = 110.07px`。

### 2. 抓出急縮原因（修正前實測）
- 以 CDP 探針（注入頁面、記錄每幀 rect 與 fly() 寫入的 inline style）在真實 Chrome 視窗實測，修正前 `fly()` 寫入：
  - `transform: translate(-115.219px,-226.984px) scale(0.582074, 0.344433)` ← **非等比**縮放（水平被拉伸 1.69 倍）。
- 取消過場後量測最終落點：`186×73.4 @ (357,19)`；而真實選單 logo 可見範圍是 `110.1×73.4 @ (395,19)`。
- 結論：舊程式把 logo 縮進「整個選單盒子」（186 寬），到位換手顯示真實 logo（110.1 寬）時寬度瞬間跳縮 41%、左緣跳 38px → 即使用者看到的「急縮小」；且飛行全程 logo 被非等比拉寬。

### 3. 修正（js/main.js `fly()`）
- 改為對齊 `object-fit:contain` 的**可見範圍**並使用**單一等比縮放**：
  - `ar`＝圖片原始比例（`naturalWidth/naturalHeight`，退化時用實測 rect）。
  - 目標可見框：`tw=min(b.width, b.height*ar)`、`th=tw/ar`（置中偏移 `(b.width-tw)/2`）。
  - 來源可見框同理（`sw/sh/cx/cy`），`s=tw/sw` 單一比例。
  - `dx/dy` 讓換算後的可見框左上角精準落在目標可見框左上角（`-cx*s`、`-cy*s` 修正元素盒內偏移）。
- 過場時間、曲線（680ms、`cubic-bezier(.22,.85,.25,1)`）、`finish()` 時序皆未改動。

### 4. 修正後驗證（CDP 實測，真實 Chrome 視窗）
- 桌面 1280×800：fly 寫入 `translate(-77.25px,-226.984px) scale(0.344433)`（等比）；落點 `110.1×73.4 @ (395,19)` == 選單 logo 可見框 → 落差 dx=0.0 dy=0.0 ddx=0.0 ddy=0.0。
- 手機斷點 400×800：fly 寫入 `scale(0.340954)`（等比）；落點 `88.8×59.2 @ (205.6,13)` == 選單 logo 可見框 → 落差全 0。
- `node --check js/main.js` 通過。
- 附註：自動化環境的 Chrome 會讓 CSS transition「瞬間完成」（以獨立測試元素證實），因此無法逐幀錄下飛行過程；改以「fly() 實際寫入的 transform + 過渡取消後的落點量測」驗證，兩者正是急縮發生的前後端點。

### 5. 單檔 bundle 重新產生（連帶修正 build script）
- 產生時發現既有問題：`assets/dinos_2/game_logo.png`（logo 替換任務新增、只被 index.html 引用）被 `build_single_file.mjs` 當成必須被 main.js 引用而 throw；`伴伴擬貓女/緋紅女巫/超人.png` 三個未使用備用圖同理。
- 修正 `build_single_file.mjs`（最小改動）：
  - `logo` 變數改讀 `assets/dinos_2/game_logo.png`（原 `assets/logo.png` 已無任何引用）。
  - buddy 迴圈：未被 main.js 引用的素材改為跳過（不再 throw）；引用但沒內嵌的路徑仍由原有 `leftover asset reference` 檢查攔下。
  - HTML 組裝：`src="assets/dinos_2/game_logo.png"` → data URI。
- 重新產生 `dragonfinder_v1.9.10.html`（29.5 MB）：內含新修正（`tw/sw` 1 處、舊非等比式 0 處）、logo 外部引用 0、無 JS 錯誤、開場後正常進入劇情/選單。

### 6. 最終驗收（1420×900 視窗，重新對 index.html 與 bundle 各跑一次 CDP 探針）
- `index.html`：標題正確、JS 錯誤 0；fly 寫入 `translate(-77.25px,-276.984px) scale(0.344433)`（等比）；落點 `110.1×73.4 @ (475,19)` == 選單 logo 可見框（落差全 0）。
- `dragonfinder_v1.9.10.html`：標題正確、JS 錯誤 0；fly 寫入與落點量測結果與 index.html 完全一致（落差全 0）。
- 單檔內容再檢：新等比式存在、舊非等比式不存在、`(src|href)="(css|js|assets)/"` 外部引用 0。
- HTTP 檢查：`index.html`、`dragonfinder_v1.9.10.html`、`assets/dinos_2/game_logo.png`、`css/style.css`、`js/data.js`、`js/tower.js` 全部 200。

## 最終狀態

- 完成：logo 到位不再急縮（落點誤差 0）；飛行過程改為等比縮放不再橫向拉伸；單檔 bundle 已同步重生。
- 依指示未執行 git commit/push。
