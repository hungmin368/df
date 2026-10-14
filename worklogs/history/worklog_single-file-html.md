# Worklog：打包單一檔 HTML（dragonfinder_v1.9.10.html）

- 日期：2026-09-24
- 任務 ID：single-file-html
- 需求：把 Dragon Finder 整個包裹成一個 HTML 檔，不連結任何其它檔案，輸出 `dragonfinder_版號.html`。

## 步驟記錄

### 1. 盤點外部依賴
- 結果：`index.html` 引用 `css/fonts.css`、`css/style.css`、`js/data.js`、`js/tower.js`、`js/main.js`、`assets/logo.png`（×2）。
- CSS 內引用：`assets/fonts/Huninn.woff2`、`assets/fonts/Iansui.woff2`、`assets/cursor.png`、`assets/map.png`。
- JS 內引用：`data.js` 139 張 `assets/dinos/*.webp`；`main.js` 7 張 `assets/dinos_2/DFD-000_*.png`（伴伴）＋故事章節圖以動態路徑 `'assets/story/s'+(s.lv||0)+'.svg'` 產生（main.js:807、825）。
- 全專案無 `fetch`／`XMLHttpRequest`／外部 http(s) 連結；只有 `location.reload()`（main.js:943、956），對單檔無影響。
- JS 內無 `</script>` 字串，可安全內嵌進 `<script>`。

### 2. 建立並執行打包腳本
- 新增 `build_single_file.mjs`（一次性打包工具，node 執行）：
  - 所有資產轉 data URI（webp/png/svg/woff2 各自 MIME）。
  - CSS 的 `url(...)` 全部換成 data URI；`index.html` 的 2 處 logo `<img>` 同步替換。
  - `data.js` 的 139 個 `"img":"assets/dinos/N.webp"` 逐個替換；缺圖會 throw。
  - `main.js` 的 7 張伴伴圖路徑逐個替換；故事章節圖改為 `__storyImg(s.lv||0)`，對應表注入在 `data.js` 的 `'use strict';` 之後。
  - 內嵌 SVG favicon，避免瀏覽器自動請求 /favicon.ico。
  - 多道防線檢查：組裝前檢查各 JS/CSS 無殘留 `assets/` 引用；組裝後檢查 HTML 無 `src/href` 指向 css/js/assets。
- 結果：`node build_single_file.mjs` 成功輸出 `dragonfinder_v1.9.10.html`（25.3 MB），所有檢查通過。

### 3. 驗證（進行中）
