# AGENTS.md

This file provides guidance to the AI agent when working with code in this repository.

- This is a dependency-free static app: open `index.html` directly or serve it with `python3 -m http.server`; no automated test or lint runner is configured.
- Keep `js/data.js` before `js/main.js` in `index.html`: `main.js` consumes the global `POKEMON` and `LEGENDS` datasets.
- Player progress persists in browser `localStorage` under `dinodoku-*`; changes to persisted state require corresponding initialization/migration and developer-reset updates.
- `Patch*.py` scripts are one-off, in-place maintenance tools that create backups; do not run them as routine tooling.
- Do not edit historical `*.bak` files or `index_backup_*.html` snapshots.
- Keep player-facing UI text in Traditional Chinese.

## Git workflow

- Remote repository: https://github.com/hungmin368/df.git (branch `main`).
- GitHub Pages site: https://hungmin368.github.io/df/.
- After every change, verify locally before committing: serve with `python3 -m http.server` and check pages/assets over HTTP (e.g. `curl` status checks); never commit or push a change that fails verification.
- Commit and push to `main` only after verification passes; never force-push or rewrite published history.

## Worklog

- Every task must create and maintain a worklog at `worklogs/worklog_<slug>.md`, where `<slug>` is a short English task name.
- Update the worklog as work happens: record each step immediately after completing it; never backfill entries after the fact.
- Every step of task execution must also be recorded in the worklog, not just the final outcome.
- Structure: task title, date, task ID, step-by-step records (what was done, result/verification for each step), and a final status section with the commit hash.
- Commit the worklog file together with the task's changes.
