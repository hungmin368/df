# AGENTS.md

This file provides guidance to the AI agent when working with code in this repository.

## Repository layout

- `game_db/` is the game's single source of truth and the only directory that ships. It contains `index.html`, `privacy.html`, `manifest.webmanifest`, `sw.js`, `css/`, `js/` and every asset the game actually loads. **All game feature work happens directly under `game_db/`**, preserving its internal relative layout so in-game links keep working.
- `working_db/` holds task artifacts that are not part of the shipped game, organized by category:
  - `working_db/reports/` — all HTML reports
  - `working_db/generated_assets/` — generated art/video/icon pipelines and intermediates (`dinos_2/`, `chests/`, `videos/`, `icons/`, `images/`)
  - `working_db/store/` — App Store screenshots and listing material
  - `working_db/builds/` — optional build outputs (`builds/dist/`)
  - `working_db/docs/` — design notes and reference docs
  - `working_db/archive/` — backups and retired scripts
- **Promotion rule (user directive 2026-10-22):** any new file produced by a task that the game does not directly use must first be written to an appropriate `working_db/` category. Move it into `game_db/` only when the user explicitly says to put it into the game.
- `tools/` holds repository maintenance scripts (`build_dist.py`, `build_ios_icons.py`, `shoot_ios_screenshots.py`). `ios/` is the Capacitor platform project. `worklogs/` holds worklogs for unfinished tasks only.
- The repository-root `index.html` is only a redirect launcher for GitHub Pages → `game_db/`. Do not put game logic there.

## Development

- This is a dependency-free static app: open `game_db/index.html` directly, or serve the repository root with `python3 -m http.server` and open `http://localhost:8000/game_db/`; no automated test or lint runner is configured.
- Keep `game_db/js/data.js` before `game_db/js/main.js` in `game_db/index.html`: `main.js` consumes the global `DINOS` and `LEGENDS` datasets.
- Keep all feature work on `game_db/index.html` and its `js/`/`css/`/`assets/` sources, and keep no single-file builds in the repo. Do not generate `dragonfinder_v<version>.html` bundles anymore — the game ships as `game_db/index.html` alone (user decision 2026-10-14, retiring the `build_single_file.mjs` release step).
- Player progress persists in browser `localStorage` under `dinodoku-*`; changes to persisted state require corresponding initialization/migration and developer-reset updates.
- `Patch*.py` scripts are one-off, in-place maintenance tools that create backups; do not run them as routine tooling.
- Do not edit historical `*.bak` files or `index_backup_*.html` snapshots.
- Keep player-facing UI text in Traditional Chinese.
- Capacitor uses `game_db` directly as `webDir` (`capacitor.config.json`); `npm run sync` runs `npx cap sync ios`. `npm run build` is optional and copies `game_db/` to `working_db/builds/dist/`.

## Art style registry

- 「風格A」(Style A) = the BanBan-family dino style, established 2026-10-16 from `game_db/assets/dinos_2/DFD-000_伴伴_2star.png`. Whenever the user says 風格A, generate/evaluate against exactly this style.
- Style A traits: cute chibi 3D toy-style render with soft organic satin skin sheen — subtle highlights, visible fine scale/feather texture, NO hard plastic/vinyl gloss, never glass-smooth: natural weathering with subtle dirt smudges, mud patches and grass/leaf fragments stuck to the body, amount scaling with star tier (user refinement 2026-10-16); big golden-amber round eyes with white specular highlights; cheerful open smile showing tiny white fangs and a pink tongue; creamy white belly; bright yellow-orange segmented horns/spikes/claws; pink inner ears / pink wing membranes; dynamic lively pose; plain pure white background; high-resolution digital art.
- Per-species rule under Style A: keep the family accents (golden eyes, yellow-orange horns/claws, cream belly, pink inner ears) but give each species its own instantly recognizable body color (e.g. Carnotaurus = vibrant crimson), with species-defining anatomy (horns, plates, crest, sail…) clearly readable.
- Silhouette envelope under Style A (user rule 2026-10-16): every tile's whole-body outline — including tail, neck, props and floating effects — must stay within a length:height ratio of 1:1.2 to 1.2:1 (square-box framing, squat wide stance preferred; injected as the SILHOUETTE ENVELOPE clause in generation prompts and gated as `ratio_1p2` in the post-chain).
- Compact clause for slender species under Style A (marked 「收攏體態」 in the spec sheet's 體態 column), split into TWO family variants (2026-10-16 trial lesson: sauropods fail too-tall, spinosaurids/crocs/marines fail too-wide, so one shared clause fights itself): ① sauropods/prosauropods = 「頸平低」 neck stretched FORWARD horizontally at shoulder height, never pointing up, head kept low just above the back line; ② spinosaurids/croc-line/marine = 「尾緊捲＋頭微抬」 tail coiled in a tight spiral flat against the hip (tip near the front feet, never behind the haunches), neck in a gentle S-curve with the head lifted slightly and snout angled up, seen from a slight three-quarter angle with legs planted wide so the body reads wide.
- Tile size rule (user rule 2026-10-16): the body's bounding-box coverage of the 512 tile must land in 50–60% (post-chain solves scale to 55%, gate `bbox_cov_50_60`); opaque-pixel coverage stays a secondary 14–60% metric.
- Fun extras (user addition 2026-10-16): each spec row draws one random fun element (`fun_zh/fun_en/fun_kind`) — action kinds (睡覺/吃食物/唱歌/踢腿/飛踢/瑜珈) REPLACE the base pose, mood kinds (搞笑/害羞/膽小/勇敢/粗暴) modify how the pose is performed; 5★ rows draw moods only so the 13-pose hero pool stays intact. Worded to keep the square envelope (squat/sit/curl).
- Approved Style A example: `working_db/generated_assets/dinos_2/bban_samples/gemini_carnotaurus_red.png`. Generation recipe: Gemini image model (`gemini-2.5-flash-image`) with the 伴伴 2-star image flattened to white as the style reference, prompt template in `working_db/generated_assets/dinos_2/bban_samples/_gen_gemini_2star_style.py`; post-chain rembg → trim/center → 512×512 RGBA WebP for game tiles (user update 2026-10-16, was 200×200). Promoted game tiles live in `game_db/assets/dinos/`.

## Treasure chest art

- The three chest tiers (iron 鐵箱／gold 黃金寶箱／plat 白金寶箱) are Gemini-generated 3D toy-style images at `game_db/assets/chests/<tier>.webp` (256×256 RGBA, transparent), rendered by `chestIconFor()` in `game_db/js/main.js`; do not revert them to inline SVG (user decision 2026-10-21).
- Chest style: same soft satin 3D toy family as Style A (style reference `game_db/assets/dinos_2/DFD-000_伴伴_2star.png`); a single CLOSED chest, chunky and squashed (wider than tall), rounded edges, no face/character. Tier language — iron = slate-blue iron plates + walnut wood + plain brass latch; gold = saturated honey-gold + red-brown wood + star gem + filigree; plat = platinum white + ice-blue crystal cluster + aquamarine gem + faint icy glow. Rarity must stay readable at ~50px in board cells.
- Pipeline lives in `working_db/generated_assets/chests/`: `_gen_chests.py` (Gemini; gold/plat chain the previous tier image as a design-language reference) → `_post_chests.py` (rembg → trim/center with 6% margin → 512 master + 256 WebP q92). Raw/cutout/master intermediates stay in `_raw/` and `_master/` (gitignored). Promote the resulting `<tier>.webp` into `game_db/assets/chests/` only when the user says so.

## HTML reports

- When the user asks for a report (報告), deliver it as a standalone HTML file named `<topic>_report.html` in `working_db/reports/`; the file should be self-contained and styled for readability.
- All report files live in `working_db/reports/`; new reports must be written there directly, never to the repository root or `game_db/`. When a report references project assets, use paths relative to `working_db/reports/` (game assets: `../../game_db/assets/...`; generated artifacts: `../generated_assets/...`).
- Whenever a task produces tables, lists, or long-form information, automatically render that content as an HTML file too, then notify the user to open it; do not dump large tables or long data into chat.
- Keep report content in Traditional Chinese.

## Git workflow

- Remote repository: https://github.com/hungmin368/df.git (branch `main`).
- GitHub Pages site: https://hungmin368.github.io/df/ (root redirects to `/df/game_db/`).
- After every change, verify locally before committing: serve with `python3 -m http.server` and check pages/assets over HTTP (e.g. `curl` status checks); never commit or push a change that fails verification.
- Commit and push to `main` only after verification passes; never force-push or rewrite published history.

## Worklog

- Every task must create and maintain a worklog at `worklogs/worklog_<slug>.md`, where `<slug>` is a short English task name.
- Update the worklog as work happens: record each step immediately after completing it; never backfill entries after the fact.
- Every step of task execution must also be recorded in the worklog, not just the final outcome.
- Structure: task title, date, task ID, step-by-step records (what was done, result/verification for each step), and a final status section with the commit hash.
- Commit the worklog file together with the task's changes.
- When a task is finished, delete its worklog file so that `worklogs/` keeps only unfinished tasks; do not keep a `worklogs/history/` archive (user directive 2026-10-22: history is preserved in the git commit log). A pending commit/push does not make a task unfinished.
