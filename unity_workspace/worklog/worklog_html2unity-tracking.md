# HTML-to-Unity Conversion Tracking Documents

- Date: 2026-09-25
- Task ID: html2unity-tracking（為 v1.9.10 → Unity 建立步驟總表、詳細報告與狀態追蹤表，作為後續每個任務的狀態更新入口）

## Step Records

1. Read the request and the guidance files (`AGENTS.md`, `unity_workspace/AGENTS.md`); the task is to create three tracking documents and then stop.
   - Result: confirmed the files must stay inside `unity_workspace/`, use Traditional Chinese, and that no commit or push may happen without an explicit request.
2. Determined the HTML game version that conversion is based on.
   - Result: `index.html` title and version badges read `v1.9.10`, and the single-file bundle is `dragonfinder_v1.9.10.html`, so the tracker is named `html2unity_v1.9.10.md`.
3. Inventoried the HTML feature surface to enumerate conversion steps.
   - Result: menu (`#ov-menu`, map nodes, buddy panel), regions `REGION_META` 4×4–18×18 (15 areas), 140-entry dex (`DINOS` 76 + `LEGENDS` 63 + companion No.000), economy `ECON` (tickets/seeds/potions), six reward minigames, buddy skills/potential/friendship, chest key mechanic, story system, tower mode (`js/tower.js`, 2000 levels), dev panel, and 16 `dinodoku-*` localStorage keys.
4. Inventoried the Unity-side completed work from the seven existing worklogs and the verification report.
   - Result: 38 steps are verifiably complete (decisions, project skeleton, domain rules, content import, save v1, UI/input, SFX, Windows build, tests, offline audit, real-machine save round-trip).
5. Established the canonical step list: 70 steps in eight phases (A 前置與決策, B 專案骨架, C 核心規則層, D 內容與存檔, E 介面與輸入, F 素材與音訊, G 建置與驗證, H 追蹤與發行) with statuses 已完成 38 / 進行中 1 / 待決策 1 / 未進行 30 / 故障 0.
   - Result: numbering fixed; later documents reuse the same numbers so status updates stay unambiguous.
6. Created `unity_workspace/html2unity.md`.
   - Result: the step-definition document (source version, phase breakdown, production targets, state definitions, update rules) including both completed and pending steps.
7. Created `unity_workspace/html2unity_v1.9.10.md`.
   - Result: the live tracker with the serial-number table (流水號／階段／步驟／狀態／補充說明), status legend, summary counts, and the update procedure.
8. Created `unity_workspace/html2unity_report.html`.
   - Result: the standalone Traditional-Chinese HTML report detailing all 70 steps per phase with do-how, evidence or source reference, status badges, an evidence summary, known limitations, and the maintenance procedure.
9. Added the Conversion Tracking section to `unity_workspace/AGENTS.md`.
   - Result: every future Unity task is now required to update the tracker (進行中 on start; 已完成／故障／待決策 with evidence on completion) and to keep summary counts in sync; the tracker version must match the HTML game version.
10. Recorded the two inconsistencies found during the inventory in the tracker instead of silently fixing them.
    - Result: step 61 (report claims the verification launcher and build entry were removed, but `TutorialVerificationBuild.cs` and `TutorialVerificationRunner.cs` still exist) is 待決策; step 70 (worklog stops at 10:35 while verification ran until 11:08) is 未進行.
11. Verified the produced documents.
    - Result: `html2unity_report.html` parses cleanly (6 sections, 8 tables); the tracker holds 70 numbered rows matching the step list; the report and tracker agree on every status; filenames match the source version v1.9.10.

12. Served the three files over HTTP and rendered the report in the browser.
    - Result: `html2unity_report.html` (32,889 bytes), `html2unity.md` (11,436 bytes), `html2unity_v1.9.10.md` (11,969 bytes) all returned HTTP 200; the report rendered with the correct title, KPI cards (38/1/1/30/0/70) and tables. Port 8129 was used because another session's preview server already holds 8099; the test server was stopped afterwards (port confirmed closed).
13. Re-checked the repository Git state and found a stale statement in the produced documents.
    - Result: `unity_workspace/` had been committed at 09-25 11:19 as `438a0db` (222 files, including `TutorialVerificationBuild.cs` and `TutorialVerificationRunner.cs`), so the "not yet tracked in Git" notes in `html2unity_report.html` and `unity_progress_status_report.html` were outdated.
14. Corrected the stale Git statements and the related notes.
    - Result: `html2unity_report.html` now records the workspace as committed in `438a0db` and notes that the two verification-only files are part of that commit; `unity_progress_status_report.html` banner, summary and risk list updated; tracker step 61 remark and last-updated line updated.
15. Re-ran the cross-document consistency check and HTML validation after the corrections.
    - Result: 70 report rows / 70 tracker rows / 70 step-list entries, numbering 1–70 complete, 0 name or status mismatches, status counts still 已完成 38 / 進行中 1 / 待決策 1 / 未進行 30 / 故障 0.

## Final Status

- Completed: the three tracking documents plus the guidance update; no Unity source, asset, or configuration was modified. A follow-up correction pass fixed the outdated Git statements in the two reports and the tracker after the workspace commit `438a0db` was discovered.
- Verified: HTML parse check passed; HTTP 200 for all three files; browser render confirmed; step numbering and statuses consistent across `html2unity.md`, `html2unity_v1.9.10.md`, and `html2unity_report.html` (70/70/70, 0 mismatches).
- Not covered: steps marked 未進行／待決策 remain open, as recorded in the tracker.
- Not committed: no commit or push was requested; the new documents are untracked working-tree files.
- Commit hash: not committed.
