# Unity Workspace Guidance

This directory contains all Unity-specific work for Dragon Finder.

## Scope

- Keep Unity projects, C# source, Unity assets, build outputs, and Unity documentation inside `unity_workspace/`.
- Do not modify the parent web application's `index.html`, `js/`, `css/`, or `assets/` when working on the Unity port unless the user explicitly requests it.
- Do not edit generated Unity files by hand when Unity owns them.
- The Windows build is the first release target. Begin iOS-specific adaptation only after the Windows version is mature and the user authorizes it.
- Keep player-facing UI text in Traditional Chinese.

## Project Decisions

- Do not create a Unity project or begin feature migration until all required conversion decisions are confirmed and the user explicitly authorizes work to start.
- Keep game rules independent from platform-specific input, storage, and UI code so iOS can be added later.
- Store persistent player data with an explicit save-data version and migration path.

## Conversion Tracking

- Three documents track the HTML-to-Unity conversion and all live inside `unity_workspace/`:
  - `html2unity.md` — step catalogue: every conversion step (already finished and still open) grouped by phase, with its scope and the matching web-app feature; add new steps here.
  - `html2unity_v<source-version>.md` — the single live status tracker: one table row per step with 流水號 (serial number), 階段 (phase), 步驟 (step), 狀態 (status) and 補充說明 (remarks). `<source-version>` must match the HTML game version being converted (the badge in `index.html`; currently `v1.9.10`).
  - `html2unity_report.html` — dated snapshot report: a self-contained Traditional-Chinese HTML walkthrough that details every step with its do-how, evidence or source reference, and status; regenerate it at phase ends and milestones.
- Allowed status values: `未進行` (not started), `進行中` (started, not yet verified), `已完成` (implemented and verified with evidence), `故障` (failed or blocked by a defect), `待決策` (needs a user decision before work can continue).
- Every Unity task must update the tracker as part of the task: mark affected steps `進行中` when work starts, and `已完成`／`故障`／`待決策` with evidence (test results, artifacts, timestamps) in the remarks column when it ends; then keep the status summary counts and the `html2unity.md` progress snapshot in sync.
- The tracker is the authoritative status source: never mark a step `已完成` without verification evidence, and record the tracker update in the task worklog.
- When the HTML game version changes, create a new `html2unity_v<new-version>.md` tracker, update the source version in `html2unity.md`, and note the switch in the report.

## Worklog

- Record every Unity task in `unity_workspace/worklog/worklog_<slug>.md`.
- Update the worklog immediately after each completed step with its result and verification status.
- Include task title, date, task ID, chronological step records, final status, and commit hash when a commit is made.

## Verification and Git

- Verify relevant Unity changes locally before any commit.
- Do not commit, push, publish, or create external releases unless the user explicitly requests it.
