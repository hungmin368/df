# Worklog — 上架平台評估（publish-platforms-survey）

- 任務：使用者提問「如果想把遊戲上架，哪些平台合適？」，需盤點現況、比較各平台門檻與成本，給出建議順序。
- 日期：2026-10-17
- 任務 ID：publish-platforms-survey
- 產出：`game_publish_platforms_report.html`（繁體中文 HTML 報告，依 AGENTS.md 報告慣例）

## 步驟記錄

### 步驟 1：盤點倉庫現況
- 動作：`ls` 倉庫根目錄、`du -sh` 各資源目錄、列出既有 `*_report.html`。
- 結果：純靜態專案（`index.html` + `css/` + `js/` + `assets/`），無建置步驟；`assets/` 總計 579MB，其中 `assets/dinos_2/` 佔 461MB（AI 素材生成工作區，非出貨內容）；已存在 `appstore_publish_report.html`（Google Play / App Store 準備報告，含 01–44 工作清單）。

### 步驟 2：計算實際出貨體積與引用檔案
- 動作：grep `index.html` / `js/*.js` / `css/*.css` 中所有 `assets/...` 與 `.mp4` 引用；`du -sh` 各出貨目錄。
- 結果：實際出貨約 25MB —— 恐龍圖 `assets/dinos/`（139 張 webp）4.7MB、`assets/map.png` 3MB、`assets/fonts/` 0.66MB、`assets/game.mp4` 2.4MB（開場）、`js/main.js:816` 引用的 `assets/story_lv4_720p.mp4` 13MB、`assets/dinos_2/game_logo.png` 0.98MB、`assets/story/*.svg` 0.13MB、JS/CSS 約 0.7MB。
- 驗證：`css/style.css:1295`、`index.html:15`、`js/main.js:3213` 三處引用 `game.mp4`；43MB 的 `intro_forest_story*.mp4` 已無程式引用（不屬出貨內容）。

### 步驟 3：檢查 PWA 就緒度與語言／字型
- 動作：查 `manifest` / `serviceWorker` 關鍵字、列 `assets/fonts/`、grep `index.html` 的 `<title>` 與 `lang`。
- 結果：**無 manifest、無 service worker** → 目前不可安裝到主畫面，也無法直接走 TWA 上 Google Play；介面為繁中（`lang="zh-Hant"`，標題「恐龍快找 DragonFinder v1.9.17 — 恐龍解謎」）；字型為 `Huninn.woff2`、`Iansui.woff2`。

### 步驟 4：查證各平台目前門檻（2026-10）
- 動作：web 搜尋與官方文件查證。
- 結果：
  - Google Play：個人帳號（2023-11-13 後建立）需封閉測試 **12 名測試者 × 連續 14 天** 才能上正式版；US$25 一次性。
  - Microsoft Store：**個人開發者註冊已免費**（原 US$19）。
  - Poki：提供網頁獨家（約 5 年）與非獨家兩種分成合約，**必須整合 Poki SDK**。
  - CrazyGames：接受 HTML5/JS，廣告需接官方 SDK。
  - GamePix / GameMonetize：約 **45%** 廣告分成。
  - itch.io：自助上傳、不需 SDK、分成比例可自訂。
  - 微信小遊戲：**IAP 需版號 + 軟著**，官方文件未免除個人主體；小遊戲環境無 DOM（本作需重寫渲染層）。
  - 字型：jf open 粉圓（Huninn）與粉圓（Iansui）為 justfont 開源字型，可商用與重散布，需附授權文字。

### 步驟 5：產出 HTML 報告
- 動作：撰寫 `game_publish_platforms_report.html`，內容含：一句話結論、現況盤點表、三梯隊平台總表（含移植成本／費用／分成／審核／流量／適合度）、重點平台詳評、8 項共同前置工作、8 步啟動順序與成本、風險提醒、參考來源。
- 建議順序：出货包瘦身 → 補 PWA → itch.io → CrazyGames/GameDistribution → 隱私政策等文件 → Google Play（含 14 天封測）→ 看數據再談 Poki/英文 → Microsoft Store/Amazon；App Store、Steam、中國渠道暫緩。
- 報告刻意不重複 `appstore_publish_report.html` 的 01–44 細項，僅做平台選擇決策並交叉引用。

### 步驟 6：本地 HTTP 驗證
- 動作：`python -m http.server 8899` 起本機伺服器，curl 檢查狀態碼，再以瀏覽器開啟報告截圖確認渲染，最後依 PID 關閉伺服器。
- 結果：`/game_publish_platforms_report.html`、`/index.html`、`/worklogs/worklog_publish-platforms-survey.md` 皆回 **200**；瀏覽器開啟報告標題正確、5 張表格與 3 個梯隊標頭皆正常渲染、無本頁 console 錯誤；驗證完畢後已關閉 8899 port 伺服器。

## 最終狀態

- 報告已產出：`game_publish_platforms_report.html`。
- 本次為評估與文件產出，**未修改任何遊戲程式碼**，無需遊戲功能迴歸。
- commit hash：`30d6c6c`（連同上架前置批次一併提交）。
