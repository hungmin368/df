# Worklog：把 DragonFinder 上傳 git

- 日期：2026-09-24
- 任務 ID：git-upload
- 需求：讀入 AGENTS.md，把 dragonfinder 專案目前的所有變更提交並推送到 https://github.com/hungmin368/df.git（main 分支）。

## 步驟記錄

### 1. 讀入 AGENTS.md 與盤點工作樹
- 讀入 AGENTS.md：確認 Git workflow 規則（先本機驗證才 commit/push 到 main、禁 force-push、禁改寫已發布歷史）、worklog 規範、unity_workspace 自包含規則。
- `git status`：5 個修改檔（AGENTS.md、README.md、assets/dinos_2/game_logo.png、js/data.js、js/main.js）＋多個未追蹤檔（app_icon.png、3 張娃娃圖、game_logo_1.png、docs/ 4 份 txt、build_single_file.mjs、dragonfinder_v1.9.10.html、logo_fly_fix_report.html、unity_workspace/、6 份 worklog）。
- `git diff`：主線變更為 POKEMON→DINOS 資料集改名（data.js＋main.js 共 6 處）、開場 logo 飛入選單的等比縮放修正（main.js fly()）、game_logo.png 瘦身（2.68MB→1.80MB）。

### 2. 檢查 unity_workspace 體積與既有追蹤慣例
- `du`：unity_workspace 共 1.6GB，其中 DragonFinder/Library 即佔 1.6GB（Unity 自動產生的本地快取，不可提交）；真正原始內容 Assets(317K)＋Packages(20K)＋ProjectSettings(102K)＋worklog(20K)。
- `git ls-files`：docs/ 已有追蹤慣例（cmd_example.html、task-delivery-guide.html）；dragonfinder_v*.html 歷史從未追蹤，本次單檔 30MB 在 GitHub 單檔 100MB 限制內，可上傳。
- `git remote -v`：origin = https://github.com/hungmin368/df.git，本地 size-pack 18.5MB。

### 3. 確認排除項（依先前任務內記錄的使用者明確指示）
- `worklogs/worklog_dino-200-rarity-3d.md`：該任務結尾載明「依使用者要求：未提交 git」→ 本次不上傳，保持未追蹤。
- `worklogs/worklog_appstore-publish-report.md` 與 `appstore_publish_report.html`：該任務結尾載明「依使用者明確指示『不用驗證不用上傳 git』」→ 本次不上傳，保持未追蹤。
- 其餘未追蹤素材（assets/dinos_2/ 3 張娃娃圖、assets/game_logo_1.png、app_icon.png）未被任何程式引用，屬使用者自行放置的素材 → 照常上傳。
- grep `POKEMON`：原始碼（index.html、js/、css/）已無殘留，僅存在於歷史 worklog 與報告文字（歷史檔不動）。

### 4. 排除 Unity 自動產生快取
- 發現 `unity_workspace/.gitignore` 已存在（Unity 標準規則 `**/[Ll]ibrary/` 等），已能正確擋掉 Library/Logs/TestResults/UserSettings。
- 在根 `.gitignore` 再加入 `unity_workspace/*/` 的 Library/Temp/obj/Build/Builds/Logs/MemoryCaptures/Recordings/TestResults/UserSettings 規則作為第二層防護。
- 最終 `git diff --cached`：Unity workspace 與根 `.gitignore` 共 223 檔；最大必要資源為 TextMesh Pro 的 LiberationSans SDF（約 2.26MB），無任何檔案超過 GitHub 100MB 限制。
- `git diff --cached --name-only -- unity_workspace/DragonFinder/Library` 結果為 0，確認 1.6GB Library 快取未進入提交。

### 5. 本機 HTTP 與瀏覽器驗證
- 以 `python -m http.server 8765 --bind 127.0.0.1` 啟動本機伺服器。
- curl 驗證 20 個 URL 全部 HTTP 200：index.html、css/style.css、css/fonts.css、js/data.js、js/main.js、js/tower.js、2 個字型、cursor/map/logo、2 個恐龍圖、game_logo.png、game_logo_1.png、app_icon.png、2 個既有 docs 頁、logo_fly_fix_report.html、dragonfinder_v1.9.10.html。
- 瀏覽器載入 `http://127.0.0.1:8765/index.html`：標題與遊戲 UI 完整顯示，document.readyState=`complete`。
- 執行期確認：`typeof DINOS === 'object'`、DINOS 76 筆、LEGENDS 63 筆、`allMons()` 139 筆，證實 POKEMON→DINOS 改名後程式可正常初始化。
- 瀏覽器 console 緩衝含其他舊 session/port 的歷史錯誤，但本次 `127.0.0.1:8765` 載入後沒有新增錯誤。

### 6. 分組提交
- `c3e4f50` — `Rename the dinosaur dataset and refine logo presentation`：主線 DINOS 改名、logo 動畫修正及最新 app/角色/logo 素材，共 10 檔。
- `2928ad0` — `Add the standalone release bundle and project references`：單檔建置器、v1.9.10 整合包、4 份設計文件及 logo 驗證報告，共 7 檔。
- `438a0db` — `Add the self-contained Unity prototype workspace`：Unity 可重建原始內容、測試、工具、報告與快取排除規則，共 223 檔；確認無 Library 檔案。
- `786e287` — `Record completed web app investigations and delivery work`：提交 4 份可上傳的既有 worklog。
- 每組 commit 前均以 `git status` 與 `git diff --cached --stat` 檢查 staged 範圍；未夾帶 `appstore_publish_report.html`、`worklog_appstore-publish-report.md`、`worklog_dino-200-rarity-3d.md`。

### 7. 推送與遠端確認
- 執行 `git push origin main`：成功將 `f07ccc0..786e287` 推送至 `main`，未使用 force push。
- `git rev-parse HEAD` 與 `git ls-remote origin refs/heads/main` 均為 `786e287180c94da5247041eb2442a9a5afe6b5df`，確認遠端已更新。

## 最終狀態

- 狀態：內容提交與首次推送完成；本 worklog 待最後單獨提交並再次推送。
- 內容提交：`c3e4f50`、`2928ad0`、`438a0db`、`786e287`。
- Worklog commit hash：待建立。
