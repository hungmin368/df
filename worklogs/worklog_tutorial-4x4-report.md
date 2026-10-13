# worklog_tutorial-4x4-report

- 任務：把 4×4 教學做成 HTML 報告，詳列每一個教學步驟訊息
- 日期：2026-10-13
- Task ID：tutorial-4x4-report

## 步驟紀錄
1. 定位教學程式：js/main.js:2493「教學引擎」區段；4×4 使用 `startDemo()`（自動示範，main.js:2620-2692），觸發條件在 main.js:995（`PROG.tut4` 未完成時 tutorial='demo'）。
2. 蒐集所有教學訊息：startDemo 主流程訊息、demoEliminate() 推理訊息、findForced()/whyReveal() 動態理由文案、tutHide() 收尾訊息、結果畫面訊息（main.js:2357-2367）、跳過教學行為（main.js:2777-2787）、教學盤特殊行為（不計時 main.js:1357、清除按鈕禁用 main.js:1116、隱藏物全為恐龍 main.js:1081、無鑰匙寶箱 main.js:1053）。
3. 產生 tutorial_4x4_report.html：自包含（inline CSS）、繁體中文，包含概述、教學盤特殊行為、五大階段完整訊息時間軸（A 開場規則／B 第一隻恐龍／C 推理排除／D 第二～四隻／E 收尾結算）、動態訊息模板總表（findForced／whyReveal）、操作與 UI 細節、原始碼對照表。

## 最終狀態
4. 驗證：`python -m http.server 8642` 啟動後 `curl` 回報 HTTP 200；以瀏覽器開啟 http://127.0.0.1:8642/tutorial_4x4_report.html 截圖檢查：標題、六大章節、時間軸表格、動態模板、原始碼對照皆正常渲染，本頁無 console 錯誤（console 中僅有先前其他頁面/port 的歷史紀錄）。
- 已改檔：tutorial_4x4_report.html（新增）、worklogs/worklog_tutorial-4x4-report.md（新增）
- commit：23188b2（Add the 4x4 tutorial steps HTML report，僅含報告與本 worklog 兩檔；工作樹中其他暫存變更未動）
