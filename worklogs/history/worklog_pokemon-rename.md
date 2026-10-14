# Worklog：POKEMON → DINOS 改名

- 日期：2026-09-24
- 任務 ID：pokemon-rename
- 需求：找出代碼中的 `POKEMON`，確認是否有被使用；未使用則移除，有使用則改名。不執行 git commit/push。

## 步驟記錄

### 1. 全域盤點 `POKEMON`（含大小寫）
- Grep 全倉（排除 `.bak*`）：`js/data.js`（第 1 行註解＋第 3 行宣告）、`js/main.js`（4 行共 5 處使用：main.js:344、346（2 處）、1070、1466）、`agents.md`、`README.md`、`appstore_publish_report.html`、`dragonfinder_v1.9.10.html`（生成物）。
- 歷史檔 `js/main.bak012b.js`、`js/main.bak_before15_18.js` 與舊 worklog 亦有出現，依 AGENTS.md「不修改歷史 .bak／worklog」原則不動。
- 判定：`POKEMON` 是 `js/data.js` 宣告的全域資料集且被 `js/main.js` 實際使用 → 依需求「改名」，不移除。
- 新名稱 `DINOS`（與 `LEGENDS` 成對的恐龍資料集命名）；grep 確認無命名衝突。

### 2. 修改來源檔
- `js/data.js`：第 1 行標頭註解 `POKEMON＝常見 1★~2★` → `DINOS＝常見 1★~2★`；第 3 行 `const POKEMON = [...]` → `const DINOS = [...]`。
- `js/main.js`：5 處 `POKEMON` → `DINOS`（MON_BY_ID 建立、allMons()、棋盤生成 shuffle 遞補、dexPoolByTab）。
- 結果：grep 複查 `js/*.js`（排除 .bak）已無 `POKEMON`，`DINOS` 位置正確。

### 3. 同步文件描述
- `agents.md`：`main.js` consumes the global `DINOS` and `LEGENDS`。
- `README.md`：`恐龍資料 DINOS / LEGENDS（139 隻…）`。
- `appstore_publish_report.html`：該句改為「程式變數已更名為 `DINOS`（原 `POKEMON`）…」，保持報告內容正確。

### 4. 驗證
- `node --check js/data.js js/main.js js/tower.js` 通過。
- Node 載入 data.js 計數：`DINOS=76`、`LEGENDS=63`（合計 139，與 README 一致）。
- `node build_single_file.mjs` 重新產生 `dragonfinder_v1.9.10.html`（25.3 MB，腳本內建 sanity check 全過）；bundle 內 `POKEMON`=0、`DINOS`=7。
- `python -m http.server 8123`（本機，127.0.0.1），curl 檢查 `/`、`/js/data.js`、`/js/main.js`、`/js/tower.js`、`/css/style.css`、`/css/fonts.css`、`/assets/logo.png` 皆 HTTP 200。
- Headless Chrome（`--dump-dom --enable-logging=stderr`）載入：
  - `index.html`：DOM 含標題「尋龍高手 DragonFinder v1.9.10」，console 無任何錯誤（僅原有 AudioContext autoplay INFO 警告）；無 `not defined`／ReferenceError。
  - `dragonfinder_v1.9.10.html`（單檔 bundle）：同樣無 JS 錯誤、標題正確。
- 附註：SophCode 內建瀏覽器 MCP 於本次 session 異常（反覆 ERR_ABORTED），改用 headless Chrome 完成瀏覽器驗證。

## 最終狀態

- 完成：`POKEMON` 已改名為 `DINOS`（js/data.js、js/main.js）並同步 agents.md、README.md、appstore_publish_report.html；單檔 bundle 已重新產生；主頁與 bundle 瀏覽器載入均無錯誤。
- 依使用者指示不執行 git commit/push（本任務無 commit hash）。
