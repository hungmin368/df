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

## Worklog

- Record every Unity task in `unity_workspace/worklog/worklog_<slug>.md`.
- Update the worklog immediately after each completed step with its result and verification status.
- Include task title, date, task ID, chronological step records, final status, and commit hash when a commit is made.

## Verification and Git

- Verify relevant Unity changes locally before any commit.
- Do not commit, push, publish, or create external releases unless the user explicitly requests it.
