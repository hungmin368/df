# worklog_history-archive

- 任務：依使用者指示，將「已結束」的 worklog 歸檔至 `worklogs/history/`（判定規則：未結束僅剩 commit/push 者視為已結束）
- 日期：2026-10-13
- Task ID：history-archive

## 步驟紀錄

1. 複核 `worklogs/` 全部 37 份紀錄的最終狀態（逐檔抽取「最終狀態／Status／目前結論」段落；格式異常者交叉核對 git 歷史）：
   - 35 份屬「已完成」（含僅剩 commit/push、依使用者指示不 commit、commit hash 待補等情形）。
   - 保留 2 份非 commit/push 之未結案者：
     - `worklog_tower193-pregen-check.md`：缺陷調查仍等待使用者補充症狀。
     - `worklog_dino-200-rarity-3d.md`：生圖管道待決定（確認後重產 12 張、再產其餘 188 張）。
   - 交叉查證：`worklog_tutorial-reveal-reason.md` 之 commit＝`677f484`（該提交含本 worklog）；`worklog_replace-game-logo.md` 之後續 `game_logo_1.png` 換圖已於 `c3e4f50` 落實（`assets/game_logo_1.png` 與更新後 `assets/dinos_2/game_logo.png` 同版）；`worklog_single-file-html.md` 紀錄止於「驗證（進行中）」，惟其主體（單檔 bundle）早已完成並經後續任務驗證、且已由 index-mainline 決議自 repo 移除，無未結工作。
2. 建立 `worklogs/history/`，將 35 份已結束紀錄移入（28 份已追蹤＋7 份未追蹤）；`worklogs/` 僅保留上述 2 份未結案紀錄。驗證：`moved=35`、`worklogs/` 餘 2 檔、`history/` 計 35 檔。
3. 更新 `AGENTS.md` Worklog 章節，新增慣例：「When a task is finished, move its worklog to `worklogs/history/` (create it if needed) so that `worklogs/` keeps only unfinished tasks; a pending commit/push does not make a task unfinished.」
4. 版控暫存：`git add -u worklogs/`（暫存 28 筆舊路徑刪除、含 unity-archive-pause 內容變更之位移）＋`git add worklogs/history/`（暫存 35 筆新路徑），使位移在索引中成對、避免日後只提交刪除或只提交新增。
5. 驗證：本機 HTTP——`/worklogs/worklog_tower193-pregen-check.md`、`/worklogs/worklog_dino-200-rarity-3d.md`、`/worklogs/history/worklog_chest-tier-fifty.md` 皆 200；舊路徑 `/worklogs/worklog_chest-tier-fifty.md` = 404；`/index.html` = 200；`git status` 顯示 28 筆 rename＋7 筆（原未追蹤）新增，共 35 筆已入索引。
6. 收尾：本紀錄依同一慣例於完成後移入 `worklogs/history/`。

## 最終狀態

- 完成：`worklogs/` 已僅保留 2 份未結案紀錄（`tower193-pregen-check`、`dino-200-rarity-3d`）；35 份已結束紀錄歸檔於 `worklogs/history/`。
- 產出：`worklogs/history/`（35 份＋本紀錄）、`AGENTS.md` Worklog 歸檔慣例。
- Commit：（無——依慣例待使用者確認提交範圍；檔案位移已暫存於索引）
