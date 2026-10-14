# worklog_ui-status-foot-towerlabel

- 任務：移除盤面下方狀態列與頁尾聲明列；龍塔闖關時 HUD 局數標籤改為「龍塔第N局」；順帶修復兩項實測暴露的既有缺陷
- 日期：2026-10-12
- Task ID：ui-status-foot-towerlabel

## 步驟紀錄

1. 定位紅框元素：狀態列＝`index.html` `#status`（文字由 `js/main.js` `updateStatus()` 產生）；頁尾＝`#foot`；HUD 局數＝`.hud > span` 內「第 `<b id="round">` 局」，龍塔時 `updateHUD()` 寫入「塔N」導致顯示「第 塔N 局」。
2. 移除 `#status`、`#foot` 兩個元素（index.html），並刪除 `css/style.css` 對應規則（桌面版 `#status`／`#status b`／`#foot` 與手機版 media query 內兩條）。
3. 刪除 `updateStatus()` 函式與全部 15 處呼叫（技能 sweep/reveal、dev-win、newRun、markToggle、setBallMode、捕獲／寶箱／落空分支、清除 ✕、提示閃光、`fitMobileBoard` 的高度量測）；捕捉器模式提示隨狀態列移除，模式本身仍由 `body.ball-mode` 與按鈕 active 呈現。
4. HUD 標籤：`index.html` 將前後文字包入 `#round-pre`／`#round-post`；`updateHUD()` 改為龍塔時 `龍塔第`＋N＋``、地圖時 `第 `＋N＋` 局`。
5. 瀏覽器實測（新 origin 8125 避快取）：地圖標籤「第 1 局」、龍塔 205「龍塔第205」、193「龍塔第193」；`#status`／`#foot` 不存在；標 ✕／取消／捕捉器開關皆無例外。
6. 實測發現既有缺陷一：跨局換大尺寸（6→10）後棋盤橫向溢出——`sizeFont()` 單輪量測用到舊字級撐大的 board 寬度而不收斂（`#board-scroll` scrollWidth 510 > clientWidth 476，末列被裁）。修复：`sizeFont()` 改為量測→套字級→再量測兩輪收斂；實測 6→205、205→193 溢出皆 0，字級收斂 22px。
7. 實測發現既有缺陷二（console `Cannot read properties of undefined (reading 'add')`，stack：`assignRegionColors` ← `finishBoard` ← `newBoard` 的 60ms `setTimeout`）：小於 10×10 的地圖盤在 60ms 回呼內生成，若期間另開新局，舊回呼會把舊尺寸盤面寫入新局（舊盤較大→拋錯中斷開局；較小→盤面靜默損壞）。修复：排程時記住 `g0=G`，回呼內先 `hide('ov-loading')` 再 `if(G!==g0) return;`。
8. 競態復現驗證（新 origin 8126，裝 `window.onerror` 收集器）：同 tick 內 7→6（舊盤較大，修復前必拋錯）與 6→龍塔193（舊盤較小，修復前靜默損壞塔盤）兩組競態皆 `errs=[]`；盤面完整（36 格／regionOf 36；塔193 貓位 `[0,12,24,39,46,51,65,77,83,98]` 與報告一致）、`ov-loading` 正確隱藏。
9. 回歸：連續 10 次跨尺寸跳關（6/205/193/600/601/2000/7/194/131/280，穿插標 ✕ 與捕捉器開關）零錯誤、零溢出；dev-lv 下拉無 14+ 選項，大盤面 loading 路徑不受本次改動影響（`hide` 僅前移）。
10. 備註：console 中 8123／8124／8125 的歷史錯誤為舊 origin 與測試腳本與頁面載入競態所生（含兩筆 8125 的 'add'，即缺陷二修復前所拋），8126 修復後無應用錯誤。

## 最終狀態

- 狀態：兩處 UI 已移除、龍塔標籤已更正、兩項既有缺陷（sizeFont 收斂、newBoard 非同步競態）已修復並驗證。
- 產出：`index.html`、`js/main.js`、`css/style.css`、本工作日志。
- commit hash：c1d0852（與 copyright-notice 任務合併提交，兩任務變更交錯於相同檔案，慣例同 b384b1a）
