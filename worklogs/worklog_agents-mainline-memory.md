# Worklog：AGENTS.md 新增主線開發記憶

- 日期：2026-09-24
- 任務 ID：agents-mainline-memory
- 需求：讀入 AGENTS.md，新增記憶：只用 `index.html` 作為主線開發目標；`dragonfinder_v<版號>.html` 是整合測試包（驗證整個包裹成單一檔案後是否正常），維持原來主線在 `index.html` 開發。

## 步驟記錄

### 1. 讀入 AGENTS.md 與單檔打包 worklog
- 讀 `agents.md` 確認現有規則清單位置。
- 讀 `worklogs/worklog_single-file-html.md` 確認整合包背景：`dragonfinder_v1.9.10.html` 由 `build_single_file.mjs` 產出（單檔、無外部連結），用途是把整個包裹成單一 HTML 驗證是否正常。
- 結果：脈絡確認，無衝突的既有規則。

### 2. 新增記憶條目至 AGENTS.md
- 在 `js/data.js` 順序規則之後新增一條：
  - `index.html` 是唯一主線開發目標（含其 `js/`、`css/`、`assets/` 原始檔）。
  - `dragonfinder_v<version>.html` 僅為 `build_single_file.mjs` 產出的單檔整合測試包，只用來測試整包成單檔後是否正常——不可手動編輯、不可在其上開發。
- 結果：編輯成功，檔案內容確認無誤。

### 3. 本地驗證
- `python -m http.server 8765` 起本地伺服器，curl 檢查：
  - `index.html` → 200
  - `js/data.js` → 200
  - `js/main.js` → 200
  - `js/tower.js` → 200
  - `css/style.css` → 200
  - `css/fonts.css` → 200
  - `assets/logo.png` → 200
- 結果：全部 200，驗證通過；已關閉伺服器。

## 最終狀態

- 狀態：完成
- Commit hash：（待提交後填入）
