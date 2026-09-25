# Codify the html2unity Tracking Rules in unity_workspace/AGENTS.md

- Date: 2026-09-25
- Task ID: unity-agents-html2unity-rule（把 html2unity 追蹤規則完整寫進 `unity_workspace/AGENTS.md`，並依規則同步追蹤表與工作紀錄）

## Step Records

1. Read the request and the guidance files; the task is to write the html2unity rules into `unity_workspace/AGENTS.md` and stop afterwards.
   - Result: scope is limited to the Unity workspace guidance file plus the rule-mandated tracker and worklog updates; no Unity source or asset is touched.
2. Inspected the existing `Conversion Tracking` section in `unity_workspace/AGENTS.md`.
   - Result: it named the three documents and the per-task update duty, but omitted the status values, the table columns, the version-alignment detail, the version-switch procedure, and the worklog linkage.
3. Expanded the section into the complete rule set.
   - Result: the section now documents (a) the three documents and their roles — `html2unity.md` step catalogue, `html2unity_v<source-version>.md` live tracker, `html2unity_report.html` dated snapshot; (b) the five allowed status values `未進行`／`進行中`／`已完成`／`故障`／`待決策` with meanings; (c) the table columns 流水號／階段／步驟／狀態／補充說明; (d) version alignment with the `index.html` badge (currently `v1.9.10`); (e) the per-task update duty including summary-count and `html2unity.md` snapshot sync; (f) the authoritative-source rule (no `已完成` without evidence) and worklog linkage; (g) the version-switch procedure.
4. Applied the rule to this task's tracker update.
   - Result: `html2unity_v1.9.10.md` step 69 remarks now record that the rules live in the `Conversion Tracking` section, and the last-updated line records the change.
5. Verified the guidance file and the cross-document consistency.
   - Result: all eight rule checks pass (section present; three documents named; five statuses present; five columns documented; version-alignment rule; per-task update duty; worklog linkage; version-switch rule). Cross-document check unchanged: 70 report rows / 70 tracker rows / 70 step-list entries, numbering 1–70 complete, 0 name or status mismatches, counts 已完成 38 / 進行中 1 / 待決策 1 / 未進行 30 / 故障 0.

## Final Status

- Completed: the html2unity tracking rules are now codified in `unity_workspace/AGENTS.md`, and the tracker reflects the codification.
- Verified: rule-content checks all pass; cross-document numbering and statuses remain consistent (70/70/70, 0 mismatches).
- Not committed: no commit or push was requested.
- Commit hash: not committed.
