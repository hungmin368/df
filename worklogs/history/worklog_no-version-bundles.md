# worklog_no-version-bundles

- 任務：依使用者決定，停止產生 `dragonfinder_v<version>.html` 發佈包，遊戲只以 `index.html` 啟動
- 日期：2026-10-14
- Task ID：no-version-bundles

## 步驟紀錄

1. 盤點：根目錄存在 `dragonfinder_v1.9.15.html`（gitignore 內的產生物），經 grep 驗證其內容未含今日教學變更（無 `TUT_BOARDS`／秘訣文案），屬過時產物；`build_single_file.mjs` 本身有其他工作階段的未提交變更，不在本任務動它。
2. 修改 `AGENTS.md` 開發目標條目：由「release 時以 `node build_single_file.mjs` 產生自包含發佈包」改為「不再產生 `dragonfinder_v<version>.html` 發佈包，遊戲只以 `index.html` 出貨（使用者決定 2026-10-14，停用 `build_single_file.mjs` release 步驟）」。`.gitignore` 的 `dragonfinder_v*.html` 防護規則保留，避免未來誤產生的包檔混入版控。
3. 刪除根目錄過時的 `dragonfinder_v1.9.15.html`（gitignore 產物，非版控檔案）。
4. 驗證：本機 HTTP——`/index.html` 200、`/js/main.js` 200、`/dragonfinder_v1.9.15.html` 404（已不存在）；根目錄 glob 無任何 `dragonfinder_v*.html`。
5. 版控：工作樹混有其他工作階段的未提交變更（AGENTS.md 另有一處 worklog 慣例增補），比照前例採手術式提交——只提交本任務的 AGENTS.md 發佈包條目 hunk 與本 worklog。

## 最終狀態

- 完成：專案政策確立為「僅 index.html 啟動，不再產生版本後綴發佈包」；既有發佈包已清除。
- 產出：AGENTS.md 條目更新、本工作日志。
- Commit：5d62467（Ship index.html only and stop generating version bundles，僅含 AGENTS.md 發佈包條目 hunk 與本 worklog；AGENTS.md 內其他工作階段的未提交增補未一併提交）
