# Worklog：龍塔結果畫面按鈕簡化（失敗去掉「選項」、過關只留「下一關／回地圖」）

- 日期：2026-09-23
- 任務 ID：tower-result-buttons
- 需求：
  1. 龍塔闖關失敗畫面不要有「選項」（選單）選擇。
  2. 過關畫面出現地圖 6×6 關卡名字（下拉選單「翠風草原（6×6）· 新手 ⏱6:00」與「⏱ 翠風草原 個人累積」列）不對，應該拿掉。
  3. 過關畫面也應該只有「下一關」跟「回地圖」兩個選項。

## 執行步驟記錄

### 1. 確認現況與問題點（完成）
- 讀取 `js/main.js` 結果畫面相關程式：`winRound()`／`failRound()`／`timeoutRound()` 共用 `#ov-result`；`#res-lv` 由 `setupResSel()` 以 `REGION_META[n].name` 填入地圖區域名稱；上一任務新增的 `resTowerFail(on)` 只在龍塔失敗時顯示 `#res-options`。
- 以瀏覽器實測重現兩個問題：
  - 龍塔失敗：可見按鈕＝`res-next`（重新挑戰）／`res-menu`（回地圖）／`res-options`（選項）→ 需移除「選項」。
  - 龍塔過關：可見按鈕＝`res-next`（下一局 ▶）／`res-menu`（換難度）／`res-reward`／`res-rest`／`res-lv`，且 `#res-lv` 內容為「翠風草原（6×6）· 新手 ⏱6:00」「碎岩丘陵（7×7）· 新手 ⏱7:00」，分數明細另有「⏱ 翠風草原 個人累積（360）」列 → 需全部移除，只留下一關／回地圖。
- 程式碼中並無任何 UI 文字為「選單」，確認使用者所稱「選單」即上一任務新增的「選項」按鈕（`#res-options`）。

### 2. 實作（完成，`node --check` 通過）
- `js/main.js`：
  - `resTowerFail(on)` 更名並簡化為 `resTowerUI(on)`：龍塔時隱藏 `#res-lv`／`#res-reward`／`#res-rest` 並把 `#res-menu` 標籤改為「回地圖」；一般關卡還原（`#res-menu` 回復「換難度」）。不再有 `#res-options`。
  - `failRound()`／`timeoutRound()`：原本無條件呼叫 `setupResSel()`，改為 `if(!towerFail) setupResSel();`（龍塔失敗不再填地圖關卡下拉），並改呼叫 `resTowerUI(towerFail)`。
  - `winRound()`：`resTowerFail(false)` → `resTowerUI(false)`；新增 `const towerWin=!!TOWER.level;`，`#res-next` 標籤改為 `towerWin ? '下一關 ▶' : '下一局 ▶'`，`resTowerUI(towerWin)`，且 `if(!towerWin) setupResSel();`（龍塔過關不顯示地圖關卡下拉）。
  - `winRound()` 分數明細：`if(!TOWER.level) bd+=row('⏱ '+REGION_META[G.N].name+' 個人累積', ...)`（龍塔不顯示地圖區域名）。
  - 刪除「選項」事件與僅供其使用的 `resOptsBack`：`$('reward-close').onclick` 還原為 `()=>hide('ov-reward')`。
  - `soundUI()` 還原為原本的 header 內嵌寫法（`#btn-sound` 文字切換），因唯一另一個使用者（`#opt-sound`）已刪除。
- `index.html`：刪除 `#res-options` 按鈕與整個 `#ov-opts` 選項面板（面板已無入口，避免死碼）；版號 1.9.7→1.9.8（`<title>`、2 個 `.ver-badge`、`#foot`、5 個 `?v=`）。
- `css/style.css`：刪除僅為該面板而加的 `#ov-opts{z-index:55}` 與 `#ov-help{z-index:60}`（還原原始疊層行為；玩法說明原本就只從 header／主選單開啟）。
- 全庫掃描確認已無 `res-options`／`ov-opts`／`opt-*`／`resOptsBack`／`soundUI`／`resTowerFail` 殘留。

### 3. 瀏覽器實測（完成）
本機服務 `python -m http.server 8126`（`index.html`、`css/style.css`、`js/main.js`、`js/tower.js`、`js/data.js` 皆 HTTP 200）。
- 龍塔失敗（球用完，6×6）：結果畫面可見按鈕僅 `res-next`（重新挑戰）／`res-menu`（回地圖）；`#res-options` 與 `#ov-opts` 皆不存在；`.cell.ghost`＝0、`.cell.cat`＝0（不揭示位置）；文案「捕捉器用完了，還有 6 隻恐龍沒找到（龍塔不揭示位置）」；截圖確認面板僅兩顆按鈕。
- 龍塔過關（捕獲 6/6）：可見按鈕僅 `res-next`（下一關 ▶）／`res-menu`（回地圖）；`#res-lv` `display:none`；分數明細為「🎯 捕獲恐龍（6 / 6）／🎟 獎勵券（+1）／⏳ 剩餘秒數（180 秒）+180／個人總分」，已無「翠風草原 個人累積」與任何地圖關卡名；截圖確認。
- 龍塔時間到失敗（`timeUp()` 路徑）：同樣僅兩顆按鈕、`重新挑戰`／`回地圖`、無 ghost／無恐龍現形、文案「（龍塔不揭示位置）」。
- 龍塔「回地圖」：關閉結果畫面、`TOWER.level`＝0、開啟主選單。
- 一般關卡迴歸（6×6）：
  - 失敗：5 個控制項齊全（`res-next`／`res-menu`／`res-reward`／`res-rest`／`res-lv`）、`再挑戰一局`／`換難度`、`.cell.ghost`＝6、文案「（位置已揭示）」、下拉含「翠風草原（6×6）· 新手 ⏱6:00」「碎岩丘陵（7×7）· 新手 ⏱7:00」。
  - 過關：5 個控制項齊全、`下一局 ▶`／`換難度`、下拉正常、明細含「⏱ 翠風草原 個人累積」。
  - 且在「龍塔失敗→重新挑戰→龍塔過關→回地圖→一般關卡失敗」連續流程後仍正確還原（`resTowerUI(false)` 無殘留）。
- 手機寬度（iframe 390×800／360×640）：龍塔失敗＝`[res-next,res-menu]`、龍塔過關＝`[res-next,res-menu]`（`下一關 ▶`／`回地圖`），按鈕皆在視窗內、modal 無橫向溢出。
- console：8126 頁面無新增錯誤；另於頁面安裝 `error`／`unhandledrejection` 收集器跑完上述完整流程，收集結果為空陣列。

### 4. 提交與線上驗證（完成）
- 僅提交 `index.html`、`css/style.css`、`js/main.js`、本工作日志；工作區另有其他工作階段的未追蹤檔案 `worklogs/worklog_investigate-6x6-generation.md`，不納入本次提交。commit：`97ff0c8`，已推送 `origin/main`。
- GitHub Pages 部署後檢查（https://hungmin368.github.io/df/）：
  - `index.html` 頁尾＝「尋龍高手 DragonFinder v1.9.8」、`.ver-badge`＝v1.9.8，HTML 已無 `res-options`／`ov-opts`；`css/style.css` 已無 `ov-opts`。
  - `js/main.js` 含 `resTowerUI`（5 處），無 `resTowerFail`／`soundUI`／`res-options`。
  - 以瀏覽器實測線上版本：龍塔失敗＝僅 `res-next`（重新挑戰）／`res-menu`（回地圖）、`.cell.ghost`＝0、無選項面板；龍塔過關＝僅 `res-next`（下一關 ▶）／`res-menu`（回地圖）、`#res-lv` 隱藏、明細無地圖關卡名；整段流程 `error` 事件收集結果為空。

## 最終狀態
- 交付：龍塔失敗畫面（重新挑戰／回地圖）、龍塔過關畫面（下一關／回地圖，無地圖關卡名與下拉）、移除「選項」按鈕與 `#ov-opts` 面板及相關死碼、版號 1.9.8。
- commit：`97ff0c8`（Cut the Dragon Tower result screens to two buttons）
