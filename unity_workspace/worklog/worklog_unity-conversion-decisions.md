# Unity Conversion Decisions

- Date: 2026-09-24
- Task ID: #5

## Step Records

1. Began collecting the decisions required before creating a Unity project or migrating game functionality.
   - Result: Windows is the first target platform; iOS work is deferred until the Windows version is mature.
2. Confirmed Unity 6 LTS with the URP 2D Renderer.
   - Result: the initial project will use this editor version and render pipeline.
3. Confirmed uGUI with TextMeshPro for the user interface.
   - Result: game screens, board controls, dialogs, and text will use uGUI components.
4. Confirmed the first Windows release as x86_64 for Windows 10 64-bit or newer, distributed as a standalone folder build.
   - Result: ARM64, an installer, and store packaging are outside the initial release scope.
5. Confirmed a playable vertical slice as the first conversion milestone.
   - Result: the milestone will cover startup and menu flow, one board size or difficulty, one complete playable round, a small representative dinosaur dataset, and basic local saving; the full collection and advanced features are deferred.
6. Confirmed JSON as the conversion interchange format with imported Unity ScriptableObject assets.
   - Result: stable IDs and source data will be converted through JSON, while runtime game data will use Unity assets rather than loading the interchange JSON directly.
7. Audited the current web implementation for remaining product decisions.
   - Result: identified a timer/UI conflict, the 4x4 demonstration and 5x5 tutorial flow, Windows layout and input choices, versioned save requirements, unverified asset provenance, synthesized SFX, offline operation, and accessibility scope.
8. Confirmed all remaining product decisions with the recommended option A.
   - Result: use a simplified 5x5 tutorial followed by the core 6x6 game and omit the 4x4 automated demonstration from the vertical slice.
   - Result: use an `N * 30` second countdown and `N + 3` catchers.
   - Result: use a scalable 16:9 Windows presentation with centered portrait content, mouse and keyboard support, and a touch-ready input abstraction.
   - Result: create a versioned JSON save with `saveVersion = 1`; do not import web saves or persist an active board in the vertical slice.
   - Result: use 6 to 12 assets with confirmed usage rights and temporary replacements for unverified assets; pixel-perfect reproduction is not required.
   - Result: recreate the existing short SFX in Unity with an SFX toggle and defer background music.
   - Result: remain fully offline with no analytics or crash-reporting service.
   - Result: provide full keyboard play, visible focus, non-color-only feedback, and UI scaling.

## Pending Decisions

- None. Explicit authorization to start conversion is tracked separately as task #6.

## Final Status

- Completed: all pre-conversion decisions are confirmed.
- Start authorization: confirmed by the user on 2026-09-24 for the playable vertical-slice conversion.
- Commit hash: not committed.
