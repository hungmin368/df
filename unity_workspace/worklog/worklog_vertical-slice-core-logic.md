# Vertical Slice Core Logic Audit and Test Completion

- Date: 2026-09-24
- Task ID: core-logic-audit (continuation of playable vertical slice, task IDs #6–#11)

## Step Records

1. Read the root `AGENTS.md` and `unity_workspace/AGENTS.md`; confirmed the Unity isolation boundary, Traditional-Chinese UI text, worklog, and no-commit-without-request rules.
   - Result: work stays inside `unity_workspace/`; no web-app files are touched.
2. Audited the existing Domain implementation against the live web logic in `js/main.js`.
   - Result: `GameSession` matches the web round rules exactly — `TIMER.total = G.N*30` (js/main.js:1333) ↔ `InitialSeconds = Size*30`; timer off for tutorial and N≤5 (js/main.js:1332) ↔ tutorial session constructed untimed; `G.balls = N+3` (js/main.js:1086) ↔ `CatchersLeft = Size+3`; catch grants `+30s` capped at total (js/main.js:1246–1248, 1351) ↔ `RemainingSeconds = Min(InitialSeconds, RemainingSeconds + 30)` when timed; miss auto-marks × (js/main.js:1282) ↔ `marked[index] = true`; win-before-exhaustion order (js/main.js:2327–2331) ↔ `Found >= Size` checked before `CatchersLeft <= 0`.
3. Audited the board rules and solver against the web `solve2` (js/main.js:140).
   - Result: `BoardRules.IsValidSolution` and `BoardSolver.Search` enforce the same constraints — one answer per row, per column, per connected region, and consecutive rows' columns differ by more than 1 (8-direction non-touching).
4. Audited the runtime flow in `AppBootstrap`.
   - Result: `StartTutorial` builds the fixed 5x5 `Tutorial5`/`TutorialBoardDefinition` puzzle untimed; `StartFormalRound` generates a unique 6x6 board with `BoardGenerator.GenerateUnique(6, seed)` timed; `Update` ticks with pause on unfocused window and the result overlay; `CompleteRound` branches tutorial completion, formal win (dex collection, totalWins, bestRemainingSeconds, save), catcher exhaustion, and timeout with Traditional-Chinese text.
5. Found one test-coverage gap: no EditMode test exercised the 5x5 tutorial round rules (untimed, 8 catchers, no time bonus), the +30s cap, or miss marking with catcher exhaustion.
   - Result: added `TutorialRoundIsUntimedWithFivePlusThreeCatchers`, `CatchingRestoresThirtySecondsCappedAtTotal`, and `MissedCaptureMarksCellAndLosesWhenCatchersRunOut` to `DomainTests.cs`.
6. Ran the EditMode test suite through Unity batch mode (`-runTests -testPlatform EditMode`, Unity `6000.3.24f1`).
   - Result: process exit code 0; `TestResults/editmode.xml` reports 13 of 13 tests passed (0 failed, 0 skipped), including the three newly added tests; the log contains only routine batch-mode noise (licensing-client validation ignored, thread-abort messages at shutdown), no test or compilation errors. PlayMode was not re-run because no production code changed — only EditMode test coverage was extended.
7. Confirmed the tutorial ScriptableObject matches the fixed puzzle.
   - Result: `Resources/Content/TutorialBoard.asset` holds size 5, the same regions/answerColumns as `BoardPuzzle.Tutorial5()`, and `safeCell: 0`, so the runtime tutorial board equals the tested fixed puzzle.
8. Rendered the audit outcome as a standalone HTML report per the repository's report convention.
   - Result: `unity_workspace/vertical_slice_core_logic_report.html` (Traditional Chinese) lists the rule-by-rule web-to-Unity mapping, the pure-C# boundary evidence, the added tests, and the verification results.
9. Ran the PlayMode suite as well, so both suites are verified within this session.
   - Result: process exit code 0; `TestResults/playmode.xml` reports 3 of 3 tests passed — the Main scene loads, the tutorial builds a 5x5 untimed board of 25 cells with a focused cell, and the formal round initialises 6x6 with 180 seconds, 9 catchers, and 36 cells with a visible focus outline.

## Final Status

- Completed: the migrated vertical-slice core logic is verified against the live web implementation — simplified 5x5 tutorial (untimed, 5+3 catchers), formal 6x6 round (unique-solution generation, N*30-second countdown with pause, N+3 catchers), judgement order (win before catcher exhaustion, miss auto-mark, catch +30s capped at total), and completion flow (tutorial completion save, formal win dex/save, catcher exhaustion and timeout loss screens) — all organized as Unity-free pure C# in `DragonFinder.Domain` (`noEngineReferences: true`, covered by `DomainAssemblyHasNoUnityEngineReference`).
- Gap fixed: EditMode coverage now also pins the 5x5 tutorial round rules, the +30s bonus cap, and miss marking with catcher-exhaustion loss (`DomainTests.cs`).
- Verified: EditMode 13/13 and PlayMode 3/3 passed via Unity batch mode in this session, both exit code 0.
- Not uploaded: no commit and no push were made (not requested).
- Commit hash: not committed.

