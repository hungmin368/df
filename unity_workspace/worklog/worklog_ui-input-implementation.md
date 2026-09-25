# Playable UI and Input Implementation (uGUI/TextMeshPro)

- Date: 2026-09-24
- Task ID: ui-input (playable vertical-slice job「可玩 UI 與輸入」，任務清單 #6–#11 之一)

## Step Records

1. Read the root `AGENTS.md` and `unity_workspace/AGENTS.md`; resumed from an interrupted session and confirmed the completed state of the earlier steps.
   - Result: work stays inside `unity_workspace/`; Traditional-Chinese UI text, worklog and report rules, and the no-commit-unless-requested rule remain in force.
2. Read the Unity jobs context (`worklog_playable-vertical-slice.md`, tasks #6–#11) and audited the existing UI implementation against this job's acceptance conditions.
   - Result: the uGUI/TextMeshPro stack, 16:9 centered portrait layout (`Presentation16x9` 720×1000 inside a 1920×1080 `CanvasScaler` canvas), main menu, 5×5 tutorial, 6×6 formal round, and pointer input were already in place; three keyboard-focus defects and one touch gap were found (step 4).
3. Confirmed the input-stack facts from the com.unity.inputsystem 1.20.0 package source in `Library/PackageCache`.
   - Result: `DefaultInputActions` UI.Navigate already binds arrows plus a WASD `2DVector` composite; UI.Submit is `*/{Submit}` (keyboard Enter) and UI.Cancel is `*/{Cancel}` (Escape), so full keyboard navigation/submit is native to `InputSystemUIInputModule`.
4. Audited `AppBootstrap.HandleKeyboard` against the native UI actions.
   - Result: Enter fired both the native uGUI submit (Button.onClick → `HandleCell`) and the custom `enterKey` handler (another `HandleCell`), double-toggling marks or double-capturing; arrows moved both native automatic navigation and the custom focus tracker (double moves); M only worked in-game although the menu label promised it globally; touch was only implicit.
5. Refactored `AppBootstrap` so EventSystem/uGUI is the single keyboard path: removed the custom Enter and arrow/WASD handling, kept Space/C/R/Esc in `HandleGameKeys`, moved M into a global `HandleGlobalKeys`, added `SyncFocusFromSelection` so the focus outline follows the EventSystem selection, and exposed `FocusedCellIndex` for tests.
   - Result: deterministic single-path activation; game functions stay keyboard-reachable; cell Buttons keep hover/selected visuals and pointer clicks.
6. Added four PlayMode input tests to `InterfaceSmokeTests.cs`: menu arrow navigation, Enter activates the focused cell exactly once, arrows plus WASD move the board focus outline, and a simulated touchscreen tap toggles a cell mark.
   - Result: tests written; `TouchPhase` needed qualifying to `UnityEngine.InputSystem.TouchPhase` (ambiguous with `UnityEngine.TouchPhase`).
7. Ran the PlayMode suite and hit two test-environment pitfalls.
   - Result: `-quit` silently suppresses `-runTests` (stale XML, exit 0), and without `-quit` the four input tests failed because injected keyboard/touch events were inert in batch mode.
8. Diagnosed the inert-input failure with a temporary probe test.
   - Result: queued state events were not processed by the per-frame dynamic update; an explicit `InputSystem.Update()` applied them but the state was reset on the next frame.
9. Root-caused against the package source: the default `editorInputBehaviorInPlayMode = PointersAndKeyboardsRespectGameViewFocus` routes pointer/keyboard input to the editor whenever the game view is unfocused (always true in batch mode), and `InputManager.gameHasFocus` additionally requires `backgroundBehavior = IgnoreFocus` for unfocused play; Unity's own `InputTestFixture` flips these for editor playmode tests.
   - Result: setting `editorInputBehaviorInPlayMode = AllDeviceInputAlwaysGoesToGameView` plus `backgroundBehavior = IgnoreFocus` in `[UnitySetUp]` (both saved and restored in `[UnityTearDown]`) makes injected input flow naturally; the temporary probe was removed.
10. Re-ran the full PlayMode suite through `-runTests -testPlatform PlayMode` (no `-quit`, matching the proven invocation).
    - Result: 7 of 7 tests passed, process exit code 0 — the 3 original smoke tests plus the 4 new input tests (menu navigation, single-fire Enter, arrow/WASD focus, touch tap).
11. Re-ran the EditMode suite; the first attempt reused the stale `-quit` form and skipped execution (old XML), then was rerun without `-quit`.
    - Result: 13 of 13 tests passed, fresh `TestResults/editmode.xml`, process exit code 0.
12. Rebuilt the Windows x64 player through `DragonFinder.Editor.WindowsBuild.BuildRelease`.
    - Result: exit code 0 and `Windows build completed`; `Builds/Windows` managed assemblies are fresh (`DragonFinder.Runtime.dll` 23:27) and `DragonFinder.exe`/`UnityPlayer.dll` remain PE32+ x86-64 (the exe stub is unchanged for managed-only edits, which is expected).
13. Launched the built player as a smoke test (10 seconds) and inspected `Player.log`.
    - Result: fresh log at 23:47 with zero exceptions, zero missing-glyph warnings, and normal input initialization (`Using Windows.Gaming.Input`); the process stayed alive until stopped.
14. Recorded that no commit and no push were performed, per the workspace rule and the user's instruction.
    - Result: nothing was uploaded; unrelated web-app changes remain untouched.

## Final Status

- Completed: the playable UI & input job is implemented and verified — uGUI + TextMeshPro on a 16:9 centered portrait layout with main menu, 5×5 tutorial, and 6×6 game screen; mouse via the standard uGUI pointer path; full keyboard focus through the single EventSystem path (arrows/WASD navigation, Enter/Space activation, C/R/Esc/M shortcuts, visible focus outline); touch reserved and proven through the same pointer pipeline.
- Fixed: the Enter double-fire and arrow double-navigation defects, the menu-only M shortcut gap, and the batch-mode test input routing (`editorInputBehaviorInPlayMode` + `backgroundBehavior`, test-scoped only).
- Verified: EditMode 13/13 and PlayMode 7/7 (fresh XML results, exit code 0 each), a successful `StandaloneWindows64` rebuild, and a launch smoke test whose `Player.log` shows no exceptions and no missing-glyph warnings.
- Not covered: an interactive end-to-end round in the built player and the manual interface sweep at 1280×720 / 1600×900 / 1920×1080 still have to be done by hand.
- Not uploaded: no commit and no push were made (not requested).
- Commit hash: not committed.
