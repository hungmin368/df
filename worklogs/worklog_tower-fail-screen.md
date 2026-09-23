# Worklog：龍塔挑戰失敗畫面（重新挑戰／回地圖／選項）＋失敗不揭示位置

- 日期：2026-09-23
- 任務 ID：tower-fail-screen
- 需求（使用者原文）：「遊戲進入籠塔挑戰, 挑戰失敗畫面應該只有重新挑戰, 回地圖, 選項, 龍塔挑戰失敗也不可以把位置揭示」

## 執行步驟記錄

### 1. 研讀 agents.md 與現有失敗流程（完成）
- `AGENTS.md`：靜態 App（`python -m http.server` 驗證）、UI 文字用繁體中文、每個任務要有 worklog、驗證通過才 commit+push main。
- 結果畫面（`index.html` `#ov-result`）目前固定 5 個項目：`#res-lv`（難度下拉）、`#res-next`、`#res-menu`、`#res-reward`、`#res-rest`，由三處顯示：`winRound()`（main.js:2322）、`failRound()`（main.js:2385）、`timeoutRound()`（main.js:1395，時間到）。
- 龍塔狀態：`TOWER.level`（進行中關卡，不存檔）、`TOWER.max`（已通關最高層）；失敗重試同一層同一盤面＝`res-next` 內 `if(TOWER.level){ if(G.lastFail){ newBoard(); ... } }`（main.js:2416）；`res-menu`＝回主選單（main.js:2430）。
- 位置揭示來源：`failRound()` main.js:2391 與 `timeUp()` main.js:1372 對「未揭示且有恐龍」的格子加上 `.ghost` 類別（CSS 讓恐龍現形），且 `res-sub` 文字寫明「（位置已揭示）」（main.js:2396、1403）。

### 2. 瀏覽器重現現況（完成）
- 以 `python -m http.server 8123` 提供靜態檔；預先寫入存檔（`dinodoku-prog` max=7/clear{6:1}、`dinodoku-tower` max=0）後真實點擊龍塔地標進入第 1 層（HUD「塔1」），再以真實 click 逐格用完 9 顆捕捉器（6 隻恐龍 → 0 捕獲）。
- 實測結果（現況）：結果畫面顯示 5 個項目（難度下拉＋再挑戰一局＋換難度＋獎勵中心＋休息去），`.cell.ghost`＝6 格（全部未捕獲恐龍位置現形），`res-sub`＝「捕捉器用完了，還有 6 隻恐龍沒找到（位置已揭示）」。
- 結論：需在龍塔失敗時（a）把結果畫面精簡為三個項目（b）跳過 ghost 標記與「位置已揭示」文案。

### 3. 需求解讀與設計決定（完成）
- 「重新挑戰」＝重開同一層、同一張預生成盤面（沿用 `res-next` 既有 lastFail 分支）；「回地圖」＝`openMenu()`（沿用 `res-menu`，僅改標籤）。
- 「選項」＝新按鈕，開啟新「選項」面板（`#ov-opts`），內含：音效開關、獎勵中心、玩法說明、關閉。
  - 理由：遊戲內原本沒有「選項」畫面；被精簡掉的「獎勵中心」以選項入口保留可達性，音效／玩法說明為一般遊戲「選項」的標準內容。
  - 龍塔改難度／換區域的路徑＝「回地圖」後點地圖區域，因此失敗畫面不再放難度下拉（龍塔為線性樓層，下拉會直接跳出塔外，易混淆）。
- 範圍限定龍塔失敗：地圖一般關卡（含 4×4／5×5 教學）的失敗畫面維持原樣（含位置揭示）；龍塔過關畫面亦維持原樣（下一局 ▶）。

### 4. 實作（完成，node --check 通過）
- `index.html`：
  - `#ov-result` 新增 `#res-options`（「選項」，預設 `display:none`，僅龍塔失敗顯示）。
  - 新增 `#ov-opts` 選項面板（⚙️ 選項：`#opt-sound` 音效開關、`#opt-reward` 獎勵中心、`#opt-help` 玩法說明、`#opt-close` 關閉），置於 `#ov-result` 之後以確保疊在其上。
  - 版號 1.9.6→1.9.7（標題、兩處版號徽章、5 個 `?v=` 快取參數）。
- `css/style.css`：`#ov-opts{z-index:55}`（蓋過 `#ov-result`）、`#ov-help{z-index:60}`（由「選項」開說明時蓋過結果畫面）。
- `js/main.js`：
  - 新增 `resTowerFail(on)`：龍塔失敗時隱藏 `#res-lv`／`#res-reward`／`#res-rest`、顯示 `#res-options`，並把 `#res-menu` 標籤改為「回地圖」；一般情況還原（標籤回復「換難度」）。
  - `failRound()`／`timeoutRound()`：龍塔時不執行 ghost 標記（位置不揭示）、文案改「（龍塔不揭示位置）」、`#res-next` 標籤「重新挑戰」、呼叫 `resTowerFail(true)`。
  - `timeUp()`：龍塔時跳過 ghost 標記（時間到失敗亦不揭示）。
  - `winRound()`：開頭呼叫 `resTowerFail(false)` 還原按鈕組（前一場可能是龍塔失敗）。
  - 新增「選項」按鈕與面板事件；`#opt-reward` 進獎勵中心時以 `resOptsBack` 旗標記錄，關閉獎勵中心後回到結果畫面。
  - 音效抽出 `soundUI()`：同步 header 🔊/🔇 與選項面板「音效：開／關」文字。
- 驗證：`node --check js/main.js` 通過；`python -m http.server 8123` 下 index／main.js／style.css／tower.js 皆 HTTP 200，index.html 含 5 處 `?v=1.9.7`。

### 5. 瀏覽器實測（完成）
以 `python -m http.server 8123` 服務，MCP 瀏覽器實際操作（真實 PointerEvent 點龍塔地標、真實 click 逐格用完捕捉器）。

- 龍塔失敗狀態（球用完）：結果畫面可見按鈕僅 `res-next`（重新挑戰）／`res-menu`（回地圖）／`res-options`（選項），`res-lv`／`res-reward`／`res-rest` 皆 `display:none`；`.cell.ghost`＝0；`res-sub`＝「捕捉器用完了，還有 6 隻恐龍沒找到（龍塔不揭示位置）」。
- 重新挑戰：回到同一層（塔1）同一張盤面（`333555333355334455334415022411022211`），捕捉器 9 顆、標記 0。
- 選項面板：`#ov-opts`（z-index 55）正確蓋在結果畫面（z-index 50）之上；音效開關同步 header 🔊/🔇 與 localStorage `dinodoku-sound`；玩法說明（z-index 60）蓋在結果畫面上且可關閉返回；獎勵中心開啟時結果畫面隱藏，按「關閉」返回結果畫面且三按鈕仍在；「關閉」回結果畫面。
- 回地圖：關閉結果畫面並開啟主選單（`#ov-menu`），`TOWER.level` 歸 0。
- 龍塔時間到失敗（`timeUp()` 路徑）：同樣三按鈕、`ghost`＝0、文案「（龍塔不揭示位置）」；重新挑戰後同一盤面、計時 180 秒。
- 迴歸：地圖一般關卡球用完／時間到失敗仍為 6 格 ghost＋「（位置已揭示）」＋原本按鈕組；龍塔過關仍顯示「下一局 ▶」與原按鈕組，並正確推進到「塔2」。
- 手機寬度：`tmp_tower_fail_mobile.html`（390×800 與 360×640 iframe）實測，兩者結果畫面皆為 `btn=res-next,res-menu,res-options ghosts=0`；選項面板完整可見、不溢出視窗；390×800 截圖確認「遊戲結束」面板僅三按鈕、盤面無恐龍現形。
- 主控台無新增錯誤。

### 6. 提交內容隔離驗證（完成）
- 工作區另有前次任務（tower-direct-entry／龍塔規格重排）尚未提交的變更；為避免混入本次提交，以 `tmp_pick_hunks.py` 將本次任務的 hunk 套用到 HEAD 版本，產出「HEAD＋本次改動」檔案置於 `tmp_verify/`（`node --check` 通過）。
- 另將 `#res-menu` 事件改為 `TOWER.level=0; openMenu();`（原為龍塔失敗時開舊的龍塔選關彈窗，與新標籤「回地圖」不符），此為本次改動的一部分。
- 以 `python -m http.server 8124` 對 `tmp_verify/` 實測（即即將提交的內容）：
  - 龍塔失敗（球用完）：僅 `res-next`／`res-menu`／`res-options` 可見，`.cell.ghost`＝0，文案「（龍塔不揭示位置）」，`#res-menu`＝「回地圖」。
  - 選項面板：z-index 55 蓋過結果畫面（50）、音效開關同步 header 與 `dinodoku-sound`、玩法說明（60）可開可關、獎勵中心往返後仍回結果畫面且三按鈕不變。
  - 回地圖：關閉結果畫面→開啟 `#ov-menu`（不再開舊龍塔彈窗），`TOWER.level`＝0。
  - 龍塔時間到失敗：同樣三按鈕、`.cell.ghost`＝0、文案「（龍塔不揭示位置）」。
  - 迴歸：地圖 6×6 失敗仍為 5 控制項＋`.cell.ghost`＝6＋「（位置已揭示）」。
  - 重新整理後 console 無新增錯誤（唯一一筆 8124 錯誤來自測試腳本本身）。
- 提交時以 `git hash-object -w`＋`git update-index --cacheinfo` 直接將 `tmp_verify/` 的檔案內容寫入索引，確保提交位元組與驗證過的內容一致，且工作區未提交的前次任務變更不受影響。

## 最終狀態
- 交付：`index.html`（版號 1.9.7＋`#res-options`＋`#ov-opts` 選項面板）、`css/style.css`（`#ov-opts`／`#ov-help` z-index）、`js/main.js`（`resTowerFail()`、龍塔失敗不標記 ghost／不揭示位置、時間到失敗同步處理、選項面板事件、`soundUI()`、`#res-menu` 龍塔失敗回地圖）、本工作日志。
- commit：（提交後回填）
