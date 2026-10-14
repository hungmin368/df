# worklog_index-mainline

- 任務：依一致性檢查結論，確立 `index.html` 為唯一開發主線——刪除單檔封裝版 `dragonfinder_v1.9.10.html`，更新 `AGENTS.md`／`.gitignore` 規則；單檔版改為「發表前才生成」
- 日期：2026-10-12
- Task ID：index-mainline

## 步驟紀錄

1. 刪除前核對差異方向（承接 worklog_bundle-consistency-check）：`grep whyReveal` 於 `js/main.js` = 4 處、於現有 bundle = 0 處，確認 6 行差異全部是「bundle 落後、網頁主線較新」；`index.html` 已是內容超集，沒有任何內容只存在於 bundle → `index.html` 不需任何修改。
2. 引用掃描：全 repo `grep dragonfinder_v1`——`index.html`、`js/`、`css/`、`README.md`、`docs/` 皆無引用（僅歷史 worklog 與報告提到檔名），刪除不影響任何功能。
3. 刪除 `dragonfinder_v1.9.10.html`（`git rm`；檔案仍留存於 git 歷史 `5e46812`，必要時可還原）。
4. 規則更新：
   - `AGENTS.md`：主線條目改為「`index.html` 為唯一開發目標、repo 不保留單檔打包；僅發表前以 `node build_single_file.mjs` 生成」。
   - `.gitignore`：新增 `dragonfinder_v*.html`（單檔打包不再入版控）。
5. 本機 HTTP 驗證（`python -m http.server 8139` + `curl`）：`/index.html`、`/js/main.js`、`/js/data.js`、`/css/style.css`、`/assets/dinos/1.webp` 全部 200；`/dragonfinder_v1.9.10.html` = 404（確認已刪除）。
6. `bundle_consistency_report.html` 建議段追加「後續」註記（單檔版已刪除、改為發表時生成）。

## 最終狀態

- 結論：`index.html`（含 `js/`／`css/`／`assets/`）為唯一開發主線；單檔 `dragonfinder_v1.9.10.html` 已自 repo 刪除，日後僅在發表前以 `build_single_file.mjs` 生成。
- 已改檔：`AGENTS.md`、`.gitignore`；刪除：`dragonfinder_v1.9.10.html`；追加註記：`bundle_consistency_report.html`
- commit：（尚未 commit——本 worklog 與上述變更、`worklog_bundle-consistency-check.md`、`worklog_unity-archive-pause.md` 後記待一併提交）
