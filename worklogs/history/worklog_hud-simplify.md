# worklog_hud-simplify

- 任務：依使用者指示精簡遊戲中（進行關卡時）頂部 HUD——移除紅框標示的 6 個項目：🎟 獎勵券、🌌 星願種子、🧪 進化藥水三個計數，以及 🏆 戰績、📖 圖鑑、🔊 音效三個 icon 按鈕；保留關卡標籤、分數、沙漏、愛心與 ❓ 玩法說明，讓畫面簡潔。紅框範圍經截圖放大與像素掃描確認為該 6 項（❓ 在框外）。
- 日期：2026-10-13
- Task ID：hud-simplify

## 步驟紀錄

1. 截圖判讀：附件（龍塔第 236 關行動版遊玩畫面）以 PIL 裁切 (130,30,640,100) 3 倍放大檢視，辨識紅框內容為 🎟250、🌌28、🧪108、🏆、📖、🔇 共 6 項；再以像素掃描定位紅框邊界（垂直線 x=146–149、537–540；水平線 y=44–47、89–92），確認與 6 項位置吻合，框外的「龍塔第 236」標籤與 ❓ 按鈕保留。
2. 引用盤點（js/main.js）：
   - `econRender()`（326–334 行）：`$('tickets')`、`$('seeds')` 為未防護存取（元素移除後會拋錯）、`$('potions')` 已有 null 防護；`rw-tickets`（獎勵視窗內）與 `#reward-games` 按鈕停用邏輯保留。
   - 事件綁定：1754 行 `$('btn-lv')`、1765 行 `$('btn-dex')`、3033–3038 行 `btn-sound`。
   - `updateHUD()`（1341–1348 行）僅操作 round/round-pre/round-post/score/hud-score/hearts，不涉及被移除元素，無需修改。
3. 功能替代路徑確認：戰績可由主選單「🏆 戰績」開啟（`menu-record`，1756 行）；圖鑑可由主選單圖鑑完成度橫幅開啟（`#dex-banner`，1753 行）；音效開啟狀態沿用存檔偏好 `dinodoku-sound`（70 行），移除切換鈕後維持既有設定。種子數仍顯示於「提示 🌿」按鈕文字（2290 行），獎勵券張數仍顯示於獎勵中心視窗（`rw-tickets`）。
4. index.html 移除元素：刪除 `🎟 tickets`、`🌌 seeds`、`🧪 potions` 三個計數 span 與 `btn-lv`、`btn-dex`、`btn-sound` 三個按鈕；HUD 現存關卡標籤、分數、沙漏、愛心、❓ 共 5 項。
5. js/main.js 清理引用：
   - `econRender()`：刪除 tickets/seeds/potions 的 DOM 同步 3 行（前兩行原為未防護存取，移除後不再有 null 風險）；保留 `rw-tickets` 與獎勵按鈕停用邏輯。
   - 刪除 `$('btn-lv').onclick`（原 1754 行）、`$('btn-dex').onclick = openDexFull;`（原 1765 行）、`btn-sound` 綁定與初始化共 6 行。
   - `soundOn` 變數與 `dinodoku-sound` 偏好讀取保留，音效依最後設定運作。
6. 版本號 bump：index.html 全數 8 處 `1.9.13` → `1.9.14`（title、2 個 CSS 連結、2 個版本徽章、3 個 JS 連結）。
7. 靜態驗證：`node --check js/main.js` 通過；`python -m http.server 8975` 起服務，`index.html`／`js/main.js`／`js/data.js`／`js/tower.js`／`css/style.css` 皆 200；`index.html` 內 `1.9.14` 出現 8 處。
8. 瀏覽器驗證（http://127.0.0.1:8975/，新版頁面）：
   - DOM 檢查：`tickets`／`seeds`／`potions`／`btn-lv`／`btn-dex`／`btn-sound` 皆已不存在；`btn-help`、`score`、`hearts`、`hud-timer`、`btn-hint`、`btn-ball` 保留；版本徽章 v1.9.14。
   - `econRender()` 呼叫測試：暫設 ECON.tickets=7 後 `rw-tickets` 更新為 7、6 個獎勵按鈕全數啟用；還原後回 0，全程無例外（證明移除的未防護存取行不再拋錯）。
   - 主選單：圖鑑橫幅開啟 `ov-dexfull`（140 格）、獎勵中心開啟（`rw-tickets`=0、按鈕正確停用）、`menu-record` 開啟戰績（8 區列）。
   - 關卡內（4×4 教學局）：HUD 僅「第 1 局 分數 0 ❓」；提示按鈕顯示「提示 🌿 🌌N」且隨 ECON.seeds 更新（暫設 5 → 🌌5）。
   - 龍塔模式（dev-tower-jump 至第 236 層）：HUD 僅「龍塔第236 ❓」，分數／沙漏／提示皆正確隱藏；盤面可操作（state=marking）。
   - 一般關卡（6×6）：沙漏正常倒數顯示（3:00 起算），HUD「第 1 局 分數 0 2:41 ❓」。
   - Console：全頁面來源 8975 僅 1 筆錯誤，為瀏覽器自動化工具對 SVG `<g>` 呼叫 `.click()` 所致（工具端限制，改用 dispatchEvent 後正常），非應用程式錯誤；其餘皆為他埠舊紀錄。
9. 收尾：
   - 刪除分析用暫存檔 `tmp_hud_crop.png`（已確認不存在）。
   - 還原測試瀏覽器存檔：移除本次驗證產生的全部 `dinodoku-*` 鍵（dex/friend/skills/prog/potential/buddy/frag/hab/econ/recent/story），使測試瀏覽器回到全新狀態（與本次驗證開始前一致：開場故事＋教學會重新播放）。
   - 關閉測試伺服器（port 8975，PID 55760，已停止）。
   - `git status` 複核：本次變更為 `index.html`、`js/main.js`（M，未暫存）；本次 worklog 歸檔後移入 `worklogs/history/`。
10. 歸檔：本紀錄移入 `worklogs/history/`。

## 最終狀態

- 完成：HUD 紅框內 6 項（🎟／🌌／🧪 計數、🏆／📖／🔊 按鈕）已自遊戲畫面移除；main.js 引用清理完畢（econRender、3 個事件綁定）；版本號 1.9.14；語法、HTTP、瀏覽器（含龍塔 236 與 6×6 關卡內 HUD）驗證全數通過，無應用程式 console 錯誤。
- 替代入口：戰績＝主選單「🏆 戰績」；圖鑑＝主選單圖鑑完成度橫幅；種子數＝「提示 🌿」按鈕；券數＝獎勵中心視窗；音效沿用存檔偏好（無切換鈕）。
- 未動產物：`worklogs/worklog_tutorial-4x4-report.md`（前次未完成任務，保持原狀）、根目錄既有未追蹤報告 HTML。
- Commit：（無——變更已備妥，另待使用者對整體提交範圍之指示）

## 補充驗證（歸檔後複核）

- CSS 複核：`css/style.css` 無任何綁定已移除元素（tickets/seeds/potions/btn-lv/btn-dex/btn-sound）之規則；`.hud`（21–24 行）與行動版 media query（1228–1229 行）皆為通用 `> span`／`.icon-btn` 樣式，無需修改。
- 全新首次載入冒煙（port 8976，localStorage 空）：頁面正常載入 v1.9.14、開場故事播放、跳過後進入主選單、進入 4×4 教學局自動示範——HUD 全程僅「第 1 局 分數 0 ❓」，無 8976 來源 console 錯誤。
- 伺服器已停止（port 8976，PID 17352）；測試瀏覽器存檔再次清除為全新狀態；`git status` 維持 `M index.html`、`M js/main.js`、`?? worklogs/history/worklog_hud-simplify.md`。
