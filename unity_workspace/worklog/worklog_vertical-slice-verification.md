# Unity Vertical Slice Verification

- Date: 2026-09-24
- Task ID: vertical-slice-verification（驗證 Unity 垂直切片：編輯器測試、Play Mode 流程、Windows 建置、離線、存檔、輸入、無障礙、主控台錯誤）

## Step Records

1. Read the root `AGENTS.md` and `unity_workspace/AGENTS.md`, then re-read the Unity job worklogs (`worklog_playable-vertical-slice.md`, `worklog_ui-input-implementation.md`, `worklog_data-save-versioning.md`, `worklog_vertical-slice-core-logic.md`) to reconstruct the acceptance baseline.
   - Result: verification targets confirmed — EditMode suite, PlayMode suite, Windows x64 build, launch smoke test with console/log audit, offline behavior, save round-trip, input and accessibility feedback; all work stays inside `unity_workspace/`, UI text is Traditional Chinese, no commit unless requested.
2. Audited the runtime source (`AppBootstrap.cs`, `GameSession.cs`, `JsonSaveRepository.cs`, `SfxPlayer.cs`) and confirmed the save triggers (tutorial completion, formal win, SFX toggle), the save path (`Application.persistentDataPath/dragonfinder.save.json` → `%USERPROFILE%\AppData\LocalLow\Dragon Finder Studio\Dragon Finder\`), and the tutorial win flow (3 marks, catcher mode, 5 captures).
   - Result: the interactive playthrough plan for the built player is deterministic — Space ×3, C, Enter ×5 — because the tutorial moves keyboard focus to each highlighted target automatically.
3. Ran the EditMode suite with Unity 6000.3.24f1 batch mode (`-batchmode -nographics -runTests -testPlatform EditMode`, no `-quit`).
   - Result: exit code 0; `TestResults/editmode.xml` reports 13/13 passed, 0 failed, 0 skipped; the log contains no compile or test errors (only a harmless licensing token notice).
4. Ran the PlayMode suite (`-runTests -testPlatform PlayMode`, no `-quit`).
   - Result: exit code 0; `TestResults/playmode.xml` reports 7/7 passed, 0 failed, 0 skipped — scene/menu smoke, 5×5 tutorial board, 6×6 formal state (180s, 9 catchers), keyboard navigation, single-fire Enter, arrow/WASD focus, touch tap; no exceptions or missing-glyph warnings in the log.
5. Audited offline behavior: grepped all `Assets/` sources for `UnityWebRequest|System.Net|Socket|HttpClient|WebClient|NetworkTransport` (no matches) and listed `Packages/manifest.json`.
   - Result: no game code path uses networking; the manifest carries only Unity's default module set (no multiplayer/network packages in use); the in-game menu states 「離線遊玩・不收集資料」; the previous `Player.log` shows no network activity — the standalone build runs fully offline.
6. Audited accessibility feedback in code: per-cell `Outline` focus ring (white for focus, yellow for tutorial target), region letters (區A–區F) on every cell, `CanvasScaler` ScaleWithScreenSize plus a 90–110% interface-scale button, distinct button selected/highlighted colors, SFX tones per action with a global M toggle, textual status feedback for every action, and keyboard/gamepad navigation through `InputSystemUIInputModule`.
   - Result: all accessibility feedback paths are present in code; PlayMode tests assert the focus outline, region letters, and keyboard/touch input; real-player screenshots are captured in the playthrough step for visual confirmation.
7. Rebuilt the Windows x64 player through `DragonFinder.Editor.WindowsBuild.BuildRelease` (incremental, no code changes since the last build).
   - Result: exit code 0 and `Windows build completed` in the fresh log; `Builds/Windows` holds `DragonFinder.exe`, `UnityPlayer.dll`, `DragonFinder_Data`, `MonoBleedingEdge`, and `D3D12`; `file` reports PE32+ x86-64 for the exe and `UnityPlayer.dll`; managed `DragonFinder.Runtime.dll` is the build output shared with the test suites.
8. Attempted an automated end-to-end keyboard playthrough of the built player (Space ×3 → C → Enter ×5 tutorial win) via WScript.Shell and then raw `SendInput`, with `PrintWindow` screenshots.
   - Result: the tutorial never started; diagnosis showed three environment obstacles in sequence — (a) keys sent while the window existed but before the game finished loading, (b) `PrintWindow` returning an all-white pre-present surface that fooled naive readiness checks, and (c) most fundamentally, synthetic input being dropped on this machine: with the menu confirmed on screen and `GetForegroundWindow` confirmed as the game process, `SendInput` keyboard events returned success yet the game never reacted, and a global `Win+D` probe produced no effect either, i.e. OS-level input injection is filtered on this host (HIPS-style protection), independent of the game.
9. Pivoted the built-player verification away from synthetic input: pre-seeded a valid `saveVersion = 1` JSON (`tutorialCompleted: true`, `caughtDragonIds: [DF001, DF003]`, `totalWins: 2`, `bestRemainingSeconds: 71`) at `%USERPROFILE%\AppData\LocalLow\Dragon Finder Studio\Dragon Finder\dragonfinder.save.json`, launched the built player, and captured the menu via `PrintWindow` (best-of loop because single captures intermittently return the stale surface).
   - Result: the real player rendered the menu from the seeded save — 教學：已完成、收集：2/8、勝場：2、開始按鈕變為「開始 6×6 正式探索」— proving the on-disk save read path, the version gate, and menu-state wiring end-to-end in the Windows build.
10. Added one PlayMode test, `TutorialCompletesViaKeyboardAndPersistsSave`, that plays the whole tutorial through the real UI input path (simulated Space ×3, C, Enter ×5 through `InputSystemUIInputModule`, the technique the existing input tests proved), asserts the round is Won with the 「教學完成」 result overlay, and asserts the on-disk save at `Application.persistentDataPath` loads back with `tutorialCompleted = true`; the test restores any pre-existing save file.
    - Result: closes the input→flow→save-write seam at app level inside the real scene, compensating for the machine's blocked synthetic OS input.
11. Re-ran the PlayMode suite after adding the full tutorial-save test.
    - Result: Unity batch mode exited 0; `TestResults/playmode.xml` reports 8/8 passed, 0 failed, 0 skipped. The new `TutorialCompletesViaKeyboardAndPersistsSave` case passed in 3.36 seconds.
12. Resumed the verification session and re-ran the Windows player launch smoke test for 10 seconds.
    - Result: `DragonFinder.exe` was alive after the wait (`PLAYER_ALIVE=True`); it was then stopped as the test-owned process. The fresh `Player.log` has normal Unity/D3D11/Input System initialization only—no exception, error, or missing-glyph warning.
13. Re-checked offline behavior and accessibility evidence.
    - Result: source contains no `UnityWebRequest`, `System.Net`, `Socket`, `HttpClient`, `WebClient`, or `NetworkTransport` use; the player log has no network activity. Keyboard navigation/shortcuts, visible focus outlines, region letters, `CanvasScaler` scaling, status text, and optional SFX are covered by source audit and the 8 passing PlayMode tests.
14. Attempted a second built-player tutorial automation route with `WM_KEYDOWN`/`WM_KEYUP` window messages after the prior `SendInput` attempt was filtered by the host.
    - Result: the player did not receive the posted M shortcut either. This confirms that interactive automated input is blocked in this environment; it does not invalidate the engine-level complete tutorial/save test or the built-player seeded-save read test. No save fixture was left in the player data directory.
15. Verified the standalone Traditional-Chinese HTML report has no unresolved embedded-image placeholders and is self-contained; served it from the workspace with Python HTTP server.
    - Result: `vertical_slice_verification_report.html` has two embedded PNG data URIs and returned HTTP 200 with 133,219 bytes. The report explicitly records the host input-injection limitation and separates it from the verified automated evidence.

## Final Status

- Verified: EditMode 13/13; PlayMode 8/8 including full keyboard tutorial completion and `saveVersion = 1` write/read; successful Windows x64 build; latest standalone player smoke test alive after 10 seconds with a clean `Player.log`; source/log offline audit; built-player seeded-save read; keyboard/mouse/touch input and accessibility feedback coverage.
- Limitation: this host blocks all synthetic input injections (`WScript.Shell`, `SendInput`, and posted window keyboard messages), so an OS-level automated physical-input playthrough of the built player cannot run here. The equivalent interaction-to-save flow is verified in the real PlayMode scene, and the built player verifies save reading and normal launch.
- Manual follow-up: complete one tutorial with physical input in the built player and visually sweep 1280×720, 1600×900, and 1920×1080.
- Report: `unity_workspace/vertical_slice_verification_report.html`.
- Not committed or pushed: no commit or push was requested.
- Commit hash: not committed.
