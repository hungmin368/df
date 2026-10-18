# Worklog — 上架任務清單（publish-task-checklist）

- 任務：以第一／第二梯隊平台為目標，產出「共同要求但尚未完成」與「平台特別要求」兩份任務清單，並標記只能使用者來做的任務，輸出 HTML 報告。
- 日期：2026-10-17
- 任務 ID：publish-task-checklist
- 產出：`publish_task_checklist_report.html`

## 步驟記錄

### 步驟 1：建立任務計畫
- 動作：TaskCreate 4 項（稽核、撰寫報告、驗證、worklog）。
- 結果：#1 稽核、#2 報告、#3 驗證、#4 worklog。

### 步驟 2：倉庫稽核（決定「尚未完成」的證據）
- 動作：grep / ls / python 讀 PNG 尺寸。
- 結果（逐項證據）：
  - 隱私政策／服務條款：全倉 grep privacy／隱私／terms／服務條款 = **0 筆** → 未完成（A05/A06）。
  - PWA：`index.html` 僅有 `theme-color` meta，**無 manifest、無 serviceWorker、無 favicon/apple-touch-icon** → 未完成（A02/A03/A04）。
  - 英文介面：`js/main.js` 無 i18n 關鍵字；`english_mode_assessment_report.html` 僅評估未實施 → 未完成（A11）。
  - 影片載入：`index.html:15` 開場影片 `preload="auto"`（2.4MB）；`js/main.js:274` 的 `story-vid` 無初始 src（按需載入，已就緒）→ 部分未完成（A13）。
  - 圖標：`app_icon.png` = 1254×1254（源檔可用），但無任何尺寸組 → 未完成（A04）。
  - 授權文字：倉庫無 LICENSE／OFL 檔（僅報告內提及）→ 未完成（A15）。
  - 廣告 SDK：grep admob／adsense／crazygames／poki／gamedistribution = **0 筆** → 未完成（A12）。
  - 聯絡方式：grep mailto／聯絡／support = **0 筆** → 未完成（A07）。
  - og meta：grep og:／twitter:／description = **0 筆** → 未完成（A14）。
  - lazy-load：`loading="lazy"` 出現 0 次 → 未完成（A13）。
  - changelog：僅 UI ver-badge，無 changelog 檔 → 未完成（A16）。
  - 網路請求：grep fetch(／XMLHttpRequest／analytics／sendBeacon = **0 筆** → 已就緒（data safety 可填不蒐集）。
  - 出貨體積風險：`assets/dinos_2/` 461MB、`js/*.bak*` 4 檔、`tmp_*.mjs` 3 檔 → 未完成（A01）。

### 步驟 3：撰寫報告
- 動作：產出 `publish_task_checklist_report.html`。
- 結構：badge 判定原則（🤖／🤝／👤）→ 👤 快速清單 Y01–Y17 → 清單 A（A01–A20，共同要求未完成，含證據與驗收標準）→ 清單 B（B01–B33，10 個平台特別要求）→ 執行波次 Wave 0–5 → 已完成 6 項 → 風險提醒。
- 計數：A=20、B=33、👤=17（A 5 + B 12）、已完成=6。

### 步驟 4：修正
- 動作：修正 B02 列的空徽章（補上 🤖 標籤）。
- 結果：1 處替換成功。

### 步驟 5：HTTP 與瀏覽器驗證
- 動作：背景執行 `python -m http.server 8899`，curl 檢查狀態碼，瀏覽器開啟報告截圖並以 JS 統計 DOM 計數，驗證後依 PID 關閉伺服器。
- 結果：
  - `publish_task_checklist_report.html` = 200、`worklogs/worklog_publish-task-checklist.md` = 200、`index.html` = 200。
  - 瀏覽器 DOM 統計：表格 13 張（Y 快速清單 1＋A 1＋B 10 平台＋執行波次 1）；A 列 = 20、B 列 = 33、Y 列 = 17；紅底 `row-you` 列 = 34（Y 17＋A 5＋B 12）；負責徽章 🤖 20、🤝 16、👤 17（另圖例各 1），總計 53 = 20+33，全部與報告標示的計數一致。
  - 截圖確認 hero、badge 圖例、計數卡、👤 快速清單紅列、清單 A 表格（含徽章與紅底 A07 列）渲染正確。
  - 驗證完畢後已關閉 8899 port 伺服器。

## 最終狀態

- 報告：`publish_task_checklist_report.html`。
- 驗證：HTTP 200 ×3、瀏覽器渲染與計數統計全部通過、伺服器已關閉。
- 未修改任何遊戲程式碼。
- commit hash：`30d6c6c`（連同上架前置批次一併提交）。
