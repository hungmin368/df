# Worklog：Android / iOS 上架準備報告

- 日期：2026-09-24
- 任務 ID：appstore-publish-report
- 需求：盤點把 Dragon Finder 上架 Google Play / App Store 尚需進行的事項，以流水號表格清楚區分「AI 可做」與「必須使用者本人做」，並輸出成 HTML 報告。依使用者明確指示：不需驗證、不上傳 git。

## 步驟記錄

### 1. 調查程式碼與素材現況
- 讀 `js/data.js`：`POKEMON`/`LEGENDS` 僅為變數名，內容為 139+ 隻真實恐龍的中文名（梁龍、三角龍、霸王龍等），無 Pokémon 版權內容。
- Grep 音訊相關：音效以 Web Audio API 合成（`tone()`），無 .mp3/.wav 音檔，無音樂授權議題。
- Grep `https?://`：index.html、js/、css/ 零外部連結 → App 完全離線，商店可申報「不收集任何資料」。
- Grep 版本字串：v1.9.10 硬編碼於 title、logo、footer、資源查詢字串。
- 讀 `index.html` head：viewport 未含 `viewport-fit=cover`，無 safe-area 處理（iOS 劉海需補）。
- 讀 `css/fonts.css`：內嵌 Huninn（jf open 粉圓）與 Iansui（芫荽），皆為 SIL OFL 開源字型，嵌入合法但需標示。
- 發現 footer「本遊戲不販賣、不公開，家庭自用」與公開上架矛盾，列入報告 R5。
- 結果：事實齊備，無 Pokémon 版權素材（僅變數命名），最高風險為 139 張恐龍圖檔的來源授權（僅使用者能確認）。

### 2. 撰寫 HTML 報告
- 產出 `appstore_publish_report.html`（repo 根目錄，單檔自足、inline CSS、繁體中文）。
- 內容結構：
  - 一、現況盤點：完全離線、單檔整合包已驗證、Web Audio 合成音效、無 Pokémon 實質內容、OFL 開源字型。
  - 二、六大風險：R1 圖檔著作權、R2 Google 新個人帳號 20 人×14 天封測政策、R3 iOS 需 Mac、R4 keystore 遺失、R5「家庭自用」聲明矛盾、R6 兒童向合規。
  - 三、流水號 01–44 完整工作表，八個階段分組，每項標註負責方（🤖 我可做／👤 必須你做／🤝 共同／選配）。
  - 四、費用總覽（Google US$25 一次性、Apple US$99/年）。
  - 五、時程預估（四種路徑，Android 新個人帳號受封測政策影響最長 4–6 週）。
  - 六、不需帳號即可立即動工的項目清單。
  - 七、建議啟動順序。
- 結果：報告完成，44 項工作中標記 🤖 我可做 16 項、👤 必須你做 10 項、🤝 共同 17 項、選配 1 項。

### 3. 驗證與 git 處理
- 依使用者明確指示「不用驗證不用上傳 git」：略過 HTTP 驗證與 commit/push。
- 本 worklog 僅建立檔案，不隨本任務提交。

## 最終狀態

- 狀態：完成（報告已交付；未 commit／未 push，依使用者指示）
- Commit hash：無（依使用者指示不上傳 git）
