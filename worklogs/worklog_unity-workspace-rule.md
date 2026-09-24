# Worklog：AGENTS.md 新增「Unity workspace」隔離規則

- 日期：2026-09-24
- 任務 ID：unity-workspace-rule
- 需求：使用者要求——有關 Unity 程式的開發都在 `unity_workspace` 目錄下，不可以與上層交互使用檔案。將此規則寫進 AGENTS.md。

## 步驟記錄

### 1. 寫入規則到 AGENTS.md
- 於 `## HTML reports` 與 `## Git workflow` 之間新增 `## Unity workspace` 章節：所有 Unity 開發都在 `unity_workspace/` 下且保持自包含；不得在 `unity_workspace/` 與上層網頁應用之間 reference、import 或共用檔案（雙向禁止跨界使用檔案）。
- 環境確認：`unity_workspace/` 已存在，內含其專屬 `AGENTS.md`、`unity_conversion_plan_report.html` 與 `worklog/`，與本規則「自包含」精神一致。
- 結果：編輯成功；`git diff` 顯示 AGENTS.md 尚有 pokemon-rename 任務的未提交改動（`POKEMON`→`DINOS` 一行），依該任務 worklog 指示不提交，本任務提交時將暫時還原該行以排除。

### 2. 驗證
- `python -m http.server 8126 --bind 127.0.0.1` 啟動本地伺服器。
- curl 檢查 `/`、`/js/data.js`、`/js/main.js`、`/css/style.css`、`/AGENTS.md` 皆 HTTP 200。
- `curl http://127.0.0.1:8126/AGENTS.md` 確認伺服端檔案含 `## Unity workspace` 章節且規則內容完整。
- 驗證完成後以 taskkill 結束伺服器（背景命令因此回報非零退出碼，屬預期）。

