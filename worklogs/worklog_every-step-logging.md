# Require Every Step Logged in Worklog

- Date: 2026-09-23
- Task ID: every-step-logging
- Task: AGENTS.md 新增規則：任務執行的每一步都必須寫進工作日誌

## Steps

1. 建立 worklogs/worklog_every-step-logging.md（本檔案），格式依 AGENTS.md Worklog 章節規定。
2. AGENTS.md Worklog 章節於「record each step immediately」之後新增一條：「Every step of task execution must also be recorded in the worklog, not just the final outcome.」
3. 本地驗證：`python -m http.server 8765` 起服務，curl 檢查 index.html、AGENTS.md、js/data.js、js/main.js、worklogs/worklog_every-step-logging.md 皆回 200；另以 curl 取回 AGENTS.md 內容並 grep 確認新規則存在；驗證後關閉服務。

## Verification

- 通過：index.html / AGENTS.md / js/data.js / js/main.js / worklog 全部 HTTP 200；線上 AGENTS.md 含新規則文字（grep 計數 1）。

## Status

- Final：任務變更與工作日志已提交（d0bffc1），commit hash 回填於後續提交（慣例同 44dd00e）。
