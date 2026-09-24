# Worklog：AGENTS.md 新增「HTML 報告」規則

- 日期：2026-09-24
- 任務 ID：agents-html-report-rule
- 需求：使用者要求——若任務需要產出報告，必須做成 HTML 報告；任務中出現表格、列表或長資訊時，自動做成 HTML 並通知使用者打開查看。將此規則寫進 AGENTS.md。

## 步驟記錄

### 1. 寫入規則到 AGENTS.md
- 於「Keep player-facing UI text in Traditional Chinese.」與「## Git workflow」之間新增 `## HTML reports` 章節，共 3 條規則：
  - 使用者要求報告（報告/report）時，交付獨立 HTML 檔 `<topic>_report.html` 於 repo 根目錄（沿用既有慣例 `appstore_publish_report.html`），檔案自包含、樣式易讀。
  - 任務產出表格、列表或長資訊時，自動渲染成 HTML 檔並通知使用者打開；不得把大表格／長資料倒進對話。
  - 報告內容使用繁體中文。
- 結果：編輯成功；`git diff AGENTS.md` 顯示同一檔案尚有另一任務（pokemon-rename）的未提交改動（`POKEMON`→`DINOS` 一行）。經查 `worklogs/worklog_pokemon-rename.md`，該任務依使用者指示明確不執行 commit，故本任務提交時必須排除該行。

### 2. 驗證
- `python -m http.server 8125 --bind 127.0.0.1` 啟動本地伺服器。
- curl 檢查 `/`、`/js/data.js`、`/js/main.js`、`/css/style.css`、`/AGENTS.md` 皆 HTTP 200。
- `curl http://127.0.0.1:8125/AGENTS.md` 確認伺服端檔案含 `## HTML reports` 章節且 3 條規則內容完整。
- 驗證完成後以 taskkill 結束伺服器（背景命令因此回報非零退出碼，屬預期）。

### 3. 提交
- 提交策略：AGENTS.md 的 pokemon-rename 改動（`POKEMON`→`DINOS` 一行）先暫時還原 → 暫存 AGENTS.md 與本 worklog → 提交（僅含 HTML reports 規則）→ 再把該行還原回工作區，確保 pokemon-rename 的未提交改動原樣保留。
- 執行：`git add AGENTS.md worklogs/worklog_agents-html-report-rule.md` → commit（僅含 HTML reports hunk，經 diff 複核）→ `git push origin main` 成功。
- 提交後複核：`git status` 顯示 AGENTS.md 相對 HEAD 僅剩 `POKEMON`→`DINOS` 一行（pokemon-rename 的未提交改動原樣保留），其餘工作區檔案不受影響。

## 最終狀態

- 完成：AGENTS.md 已新增 `## HTML reports` 章節（報告須為獨立 HTML 檔、表格／列表／長資訊自動做成 HTML 並通知使用者打開、報告使用繁體中文），已提交並推送到 `main`。
- Commit：9df36711f50201225db68cbeabb277993ed338ab
- 驗證：本地 http.server（127.0.0.1:8125）curl 檢查 `/`、`/js/data.js`、`/js/main.js`、`/css/style.css`、`/AGENTS.md` 皆 200，且伺服端 AGENTS.md 含完整新章節；推播前 diff 複核提交內容僅含本任務變更。

