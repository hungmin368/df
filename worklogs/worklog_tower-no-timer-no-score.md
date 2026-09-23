# Worklog：龍塔不計時不計分（盤面無計時器、結算無分數/時間）

- 日期：2026-09-24
- 任務 ID：tower-no-timer-no-score
- 需求（使用者原文）：「遊戲中龍塔闖關不計時不算分數，是看闖到第幾關，所以龍塔遊戲盤面上不要有計時器，過關或失敗畫面有不要有分數或時間」

## 執行步驟記錄

### 1. 研讀 AGENTS.md 與現有計時／計分流程（完成）
- `AGENTS.md`：靜態 App（`python -m http.server` 驗證）、UI 文字用繁體中文、每個任務要有 worklog、驗證通過才 commit+push main。
- 計時器：`timerStart()`（main.js:1328）在非教學且 `G.N>=6` 時啟動沙漏 HUD（`#hud-timer`），`G.N*30` 秒倒數；`timeUp()`（main.js:1372）→ `timeoutRound()`（main.js:1398）。龍塔關卡尺寸 6×13，目前進塔會有 180 秒起跳的沙漏。
- 計分：`winRound()`（main.js:2366-2385）以 `TIMER.left` 換算分數寫入 `LV` 戰績；過關／失敗結算都會列「個人總分」`fmtSec(lvTotal())`。
- 龍塔狀態：`TOWER.level`（進行中關卡）、`TOWER.max`（已通關最高層，main.js:963 過關時更新）；`resTowerUI()`（main.js:2397）只精簡按鈕，未處理計時／計分。
- 附帶影響點：隨行技能 `time15`/`time30`（main.js:764-765）呼叫 `timerAdd()`；捕捉成功 +30 秒（main.js:1244，有 `TIMER.on` 防護）；HUD「分數」（main.js:1315，`updateHUD()` 每次开局都會呼叫）。

### 2. 實作（完成，node --check 通過）
- `js/main.js`：
  - `timerStart()`：條件加入 `TOWER.level`——龍塔進行中隱藏 `#hud-timer` 且不啟動倒數，`timeUp` 路徑不再觸發（捕捉 +30 秒原本就有 `TIMER.on` 防護）。
  - 隨行技能 `time15`/`time30`：合併為一支並比照 `hint1`，龍塔中以訊息「龍塔的考驗不計時～時間技能在這裡派不上用場！」擋下，避免無效果又誤導。
  - `winRound()`：龍塔時不取 `TIMER.left`、不寫入 `LV` 戰績；`res-sub` 改「第 X 關通過！龍塔只看你能闖到第幾關！」；明細列「🐉 龍塔進度 第 X 關／最高第 Y 關」，不列「⏳ 剩餘秒數」「⏱ 個人累積」「個人總分」。
  - `failRound()`／`timeoutRound()`：龍塔失敗明細列「🐉 龍塔進度 止步第 X 關／最高第 Y 關」，不列「個人總分」（timeoutRound 在龍塔已不會觸發，仍一併防護）；地圖模式維持原樣。
  - `updateHUD()`：龍塔進行中隱藏 HUD「分數」列（新增 `#hud-score`），回地圖恢復。
- `index.html`：HUD 分數 span 加 `id="hud-score"`；版號 1.9.9→1.9.10（標題、2 處 CSS、3 處徽章、頁尾、3 處 JS 快取參數，共 9 處）。
- 驗證：`node --check js/main.js` 通過。

### 3. 瀏覽器實測（完成）
以 `python -m http.server 8123` 服務工作區，MCP 瀏覽器以真實 PointerEvent／click 操作（預先寫入 `dinodoku-prog` clear{6:1}、`dinodoku-tower` max=0 解鎖龍塔）。

- 進入龍塔第 1 關（6×6、9 顆捕捉器、HUD「塔1」）：`#hud-timer` display=none、`TIMER.on`=false、`#hud-score` display=none——盤面無計時器、無分數。
- 龍塔失敗（捕捉器用完 9 顆）：標題「遊戲結束」、`res-sub`＝「捕捉器用完了，還有 6 隻恐龍沒找到（龍塔不揭示位置）」、明細僅「捕獲恐龍 0/6」＋「🐉 龍塔進度 止步第 1 關／最高第 0 關」，無「個人總分」；按鈕「重新挑戰／回地圖」；`.ghost`=0（截圖確認）。
- 重新挑戰→同一層同一盤面；捕捉全部 6 隻→過關：`res-sub`＝「第 1 關通過！龍塔只看你能闖到第幾關！」、明細含「🐉 龍塔進度 第 1 關／最高第 1 關」，無「剩餘秒數」無「個人總分」；按鈕「下一關 ▶／回地圖」；`TOWER.max` 正確更新為 1。
- 龍塔過關不計分驗證：`lvTotal()` 過關前後皆 360，`LV[6]` 未變（best=180/total=360 為先前地圖測試所留）。
- 時間技能：龍塔第 2 關中設定隨行觸發 `time30`，出現「龍塔的考驗不計時～時間技能在這裡派不上用場！」且 `TIMER.on` 維持 false。
- 迴歸（地圖 6×6）：`#hud-timer` display=flex、`TIMER.on`=true（180 秒）、`#hud-score` display=block；球用完失敗畫面有「個人總分 6:00」、無「龍塔進度」列、ghost=6、文案「（位置已揭示）」；過關畫面有「剩餘秒數 180 秒 +180」「⏱ 翠風草原 個人累積 540」「個人總分 9:00」，`lvTotal()` 360→540（+180 正確計分）。
- 主控台無本次改動相關的新錯誤（僅一筆測試工具對 SVG 元素 `el.click` 的限制，屬測試操作本身）。
- 測試完清除瀏覽器測試存檔（`dinodoku-*`）。

## 最終狀態
- 交付：`js/main.js`（龍塔不啟動計時器、過關/失敗結算無分數與時間並顯示龍塔進度、時間技能於龍塔擋下、HUD 分數於龍塔隱藏）、`index.html`（`#hud-score` id、版號 1.9.10）、本工作日志。
- commit：（尚未提交）
