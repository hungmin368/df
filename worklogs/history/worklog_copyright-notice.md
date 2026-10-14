# worklog_copyright_notice

- 任務：移除舊的「家庭自用」版權聲明，放入適合公開發行的正確版權宣告
- 日期：2026-10-14
- Task ID：copyright-notice
- 需求來源：使用者指示「把正確的版權宣告放進來，移除舊的」；對應 `appstore_publish_report.html` R5／流水號 08（「家庭自用」footer 與公開發行矛盾，應改為適合公開發行的版權聲明）。

## 步驟紀錄

1. 盤點現況：全倉搜尋 Copyright／©／版權／盜用 等字串。舊宣告「尋龍高手 DragonFinder v1.9.10 · 本遊戲不販賣、不公開，家庭自用，請勿盜用」位於已發布 HEAD 的 `index.html` `#foot`（遊戲畫面頁尾）；工作區未提交修改（ui-status-foot-towerlabel 任務）已移除 `#foot`，但尚未補上任何版權宣告。
2. 決定文案：`© 2026 尋龍高手 DragonFinder · 保留一切權利`（專案品牌署名、繁中、無「家庭自用」矛盾；年份取今年 2026）。擺放位置：主選單（`#ov-menu`）底部導覽列之後——遊戲畫面頁尾已於前一任務為版面空間刻意移除，主選單為每次開遊戲必經畫面，可見且不佔遊戲區空間。
3. 修改 `index.html`：於 `.menu-nav` 後新增 `<div class="menu-copy">© 2026 尋龍高手 DragonFinder · 保留一切權利</div>`。
4. 修改 `css/style.css`：新增 `.menu-copy{ margin-top:7px; font-size:11px; color:#b3a795; text-align:center; letter-spacing:.4px; }`（沿用舊 `#foot` 的淡化配色，字級再小一號）。
5. 本機驗證（`python3 -m http.server 8331`）：
   - `curl` index.html／css/style.css 皆 200，`menu-copy` 已在回應中。
   - 瀏覽器實測：主選單底部顯示「© 2026 尋龍高手 DragonFinder · 保留一切權利」（11px、淡棕、可見），`#ov-menu .modal` scrollHeight−clientHeight＝0（無溢出）；`#foot` 不存在。
   - console：本 origin (8331) 無錯誤（清單中僅 8765／8977／8991 等舊測試 origin 的歷史訊息與字型載入 info）。
   - 版面彈性：`.map-wrap`／`#map` 為 `flex:1; min-height:0` 內部捲動，任何視窗高度下版權列不致溢出（手機 ≤620px 媒體查詢未隱藏此列，維持可見）。
   - 遊戲回歸：跳過故事與教學後 `openLevel(4)` 正常開盤；`markToggle()` 實測 ✕ 標記可切換（`cell st1 cat` → `cell st1 cat x` → 還原）；盤面其餘 ✕ 為教學示範之既有自動標記。
6. 提交：本任務變更（`index.html`、`css/style.css`）連同工作區內已完成驗證之 ui-status-foot-towerlabel 任務變更（`#status`／`#foot` 移除、HUD 局數標籤、sizeFont 收斂、newBoard 競態修復，皆在其 worklog 完成驗證）一併以 `js/main.js` 同 commit 提交，避免 index.html 與 main.js 版本不一致造成線上故障（`#status` 已自 HTML 移除，須搭配移除 `updateStatus()` 的 main.js）。另 `index.html` v1.9.15 引用 `js/tower_comments.js`（龍塔留言任務產出、尚未納入版控），為避免 GitHub Pages 404，將該檔一併納入本 commit。採 pathspec 限定提交範圍，未含其他待提交工作（AGENTS.md、worklog 歸檔更名、教學報告等保持原狀）。

## 最終狀態

- 狀態：完成。舊「家庭自用」宣告已隨 `#foot` 移除（本次 commit 自已發布版本中移除），正確版權宣告已顯示於主選單底部，驗證全數通過。
- commit hash：c1d0852（含同版面相依之 ui-status-foot-towerlabel 任務變更與 `js/tower_comments.js`，詳步驟 6）
