# 遊戲更名：「尋龍高手」→「恐龍快找」

- 日期：2026-10-15
- Task ID：rename-game-name
- 背景：`game_naming_report.html`（2026-10-14）評估「尋龍高手」有撞名疑慮（華碩文化同名繪本＋《馴龍高手》混淆）。使用者選定新名稱「恐龍快找」，並要求進行全面替換。

## 事前評估

- 網路初篩：「恐龍快找」無同名產品；已知顧慮為與街機《恐龍快打》一字之差，使用者知情後確認採用。
- 盤點工作區：工作區存在前批已驗證、刻意未提交的變更（v1.9.16 龍塔留言、地圖去色塊、.gitignore、build_single_file.mjs，詳見 `pending_work_report.html`），與本任務修改檔案（index.html、js/main.js）重疊；提交策略於驗證後另向使用者確認。

## 步驟紀錄

1. 盤點舊名稱出現位置（全倉 grep 尋龍高手／高手／尋龍）：
   - index.html：6 處玩家可見（title、splash logo alt、HUD logo、menu-logo title/alt、版權宣告、退出訊息）。
   - js/main.js:2646：教學訊息「歡迎來到尋龍高手 🎬」。
   - build_single_file.mjs:102：單檔封裝註解（建置步驟已退役，字串一併更新保持一致）。
   - 不動：css/js 內部註解「尋龍地圖」（功能名、玩家不可見）、故事對白「游泳高手」等、歷史報告與 docs、`*.bak`、localStorage `dinodoku-*`、英文名 DragonFinder。
2. 建立 worklog（本檔）。
3. 執行替換：
   - index.html：7 處「尋龍高手」→「恐龍快找」（title、splash alt、HUD logo、menu-logo title 與 alt、版權宣告、退出訊息）。
   - js/main.js:2646：教學訊息改為「歡迎來到恐龍快找 🎬」。
   - build_single_file.mjs:102：單檔封裝註解名稱同步更新。
   - 版本號維持 v1.9.16 不變（前批 v1.9.16 變更尚未提交，更名不另跳版，待提交時一併上線）。

4. 驗證（`python3 -m http.server 8123`）：
   - HTTP 檢查：index.html、js/main.js、js/data.js、js/tower.js、js/tower_comments.js、css/style.css、css/fonts.css、assets/dinos_2/game_logo.png 全部 200。
   - 內容檢查：線上 index.html 含「恐龍快找」6 行、js/main.js 1 處；兩檔案「尋龍高手」皆為 0 筆。
   - 瀏覽器檢查（SophCode controlled browser）：
     - 頁面 title「恐龍快找 DragonFinder v1.9.16 — 恐龍解謎」，console 無遊戲錯誤。
     - 主選單正常渲染，頁尾「© 2026 恐龍快找 DragonFinder · 保留一切權利」。
     - 退出彈窗顯示「要離開恐龍快找了嗎？」。
     - 進入起源地 4×4，教學示範正常播放（首段訊息字串已於 main.js:2646 更新為「歡迎來到恐龍快找 🎬」），HUD 顯示「⚡ 恐龍快找 DragonFinder v1.9.16」，盤面互動正常。
   - 附註：期間唯一的 console error 為驗證工具對 SVG 元素不支援 `.click()` 事件（改以 `dispatchEvent` 觸發），與遊戲本體無關。
5. 提交策略：使用者以「解決既有未提交變更的提交策略並依 AGENTS.md 流程提交」指示續行，採方案 A（分兩段提交）。
6. 前批 v1.9.16 提交：暫時還原本任務 9 處更名字串，使工作區回到純前批狀態；煙霧測試（HTTP 200 ×4、線上 index.html「尋龍高手」6 行／「恐龍快找」0 筆、瀏覽器 title 與主選單正常）後，以前批訊息提交（含 6 個修改檔、3 個 logo 素材刪除、`game_logo_1.jpg` 新增、7 份任務報告；`english_mode_assessment_report.html` 依先前指示不入庫；`css/style.css` 僅換行狀態差異、無內容變更，未列入）→ commit `e6aa52f`。
7. 重新套用本任務 9 處更名字串，重跑完整驗證：HTTP 200 ×8、線上 index.html「恐龍快找」6 行／main.js 1 處／「尋龍高手」0 筆；瀏覽器實測 title、頁尾版權「© 2026 恐龍快找 DragonFinder · 保留一切權利」、退出彈窗「要離開恐龍快找了嗎？」、進入 4×4 後 HUD「⚡ 恐龍快找 DragonFinder v1.9.16」、盤面正常、console 無新錯誤。
8. 提交本任務更名變更（index.html、js/main.js、build_single_file.mjs、本 worklog）→ commit `b79d31f`。

## 最終狀態

- 狀態：已完成（另產生前批 v1.9.16 提交 `e6aa52f`）
- Commit hash：`b79d31f`
