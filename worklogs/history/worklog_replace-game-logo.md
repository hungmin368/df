# Replace Game Logo

- Date: 2026-09-24
- Task ID: 1-3

## Step-by-step record

1. Read `AGENTS.md` and inspected the main menu implementation. Both the splash screen and `#menu-logo` reference `assets/logo.png`; `#menu-logo img` currently uses `height:auto`, so the replacement requires an explicit existing height to preserve the menu layout. Result: replacement targets and layout constraint confirmed.
2. Replaced both Logo image sources with `assets/dinos_2/game_logo.png`. Fixed the main-menu Logo containers to the original desktop (`186×73.38px`) and mobile (`150×59.20px`) display dimensions, using `object-fit: contain`; also limited the splash Logo to the original responsive height. Result: the new square asset cannot reflow adjacent menu content.

## Final status

- Status: Complete（顯示層改版；後續 commit 另以 `game_logo_1.png` 換入正式美術圖）
- Commit hash: Pending
