# 精簡 Git 歷史與舊素材清理

- 日期：2026-11-02
- 任務 ID：history_squash
- 目標：把 GitHub 上的 177 個 commit 壓成單一快照，並移除重複影片與漫畫中間版本，降低倉庫容量。

## 執行記錄

### 步驟 1：盤點現況

- `.git` 293 MB，歷史物件 258 MB，177 個 commit。
- 目前追蹤的工作樹 168 MB，其中 `working_db` 151 MB。
- 歷史肥大來源：兩支 43 MB 森林影片、7 個漫畫舊版 PNG（每個約 4.4–5.5 MB）、舊單檔 bundle。
- 遠端 `origin/main` 在 `b42273a`，本地多一個未推送的 `eafbed8`。
- 狀態：完成。

### 步驟 2：備份完整歷史

- 執行 `git bundle create ../df_history_backup_20261102.bundle --all`（存於倉庫外 `C:/MY_AI_JOBS/`）。
- `git bundle verify` 回報 complete history，檔案 291 MB，含 `main`、`origin/main` 與 177 個 commit。
- 狀態：完成。

### 步驟 3：刪除舊素材

- 刪除舊版森林影片 `intro_forest_story_720p.mp4`（43 MB，僅被已退役的 archive 報告引用）。
- 刪除漫畫舊版 `propA_ch01_page1.png`、`_v2.png`、`_v2_m31.png`、`_v2_mnb.png`、`_v2_v3.png`、`_v2_v5.png`、`_v2_v6.png`（合計約 35 MB）。
- 保留現行 `intro_forest_story_v2_720p.mp4` 與 `propA_ch01_page1_v7.png`。
- 報告內的舊版圖片皆以 base64 內嵌，刪檔後仍可正常顯示。
- 追蹤檔案總量 168 MB → 125 MB。
- 狀態：完成。

### 步驟 4：本地驗證

- 本機 `http.server` 檢查：`/game_db/`、`index.html`、`data.js`、`main.js`、`story_lv4_720p.mp4`、v7 漫畫、v2 影片全部 200；已刪除的舊影片正確回 404。
- 狀態：完成。
