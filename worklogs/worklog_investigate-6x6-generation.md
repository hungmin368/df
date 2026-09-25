# 6×6–13×13 Pre-generated Board Capacity Analysis

- Date: 2026-09-23
- Task ID: 1–3

## Step-by-step records

1. Created this worklog before the remaining source-level reproduction and validation work.
2. Expanded the investigation from 6×6 generation to the requested 6×6–13×13 pre-generated board capacity analysis.
3. Created a three-step task plan covering rule discovery, capacity calculation, and result verification.
4. Started a read-only repository investigation to locate the board layouts, generation algorithm, random inputs, and difficulty constraints.
5. Resumed the active goal, re-read all three global tasks, and confirmed that rule discovery remained in progress while calculation and reporting were pending.
6. Checked the working tree and confirmed that this investigation worklog is the only current untracked change; no unrelated source modifications were introduced.
7. After the interrupted session resumed, rechecked the global tasks, worklog, working tree, and recent commits; confirmed that only planning and logging were complete and that source analysis still needed to continue.
8. Located and reviewed the board rules and generator: each N×N board has N connected regions, one dinosaur in every row, column, and region, and no dinosaurs touching in eight directions; the puzzle is the region layout rather than a Sudoku-style clue-removal board.
9. Confirmed the runtime split: sizes 6–9 are dynamically generated, while sizes 10–13 use `POOL_DATA`, remove one base layout per play, and randomly apply one of eight rotations/reflections before solving it again.
10. Independently parsed `POOL_DATA` and counted fixed bases as 6:0, 7:0, 8:0, 9:0, 10:20, 11:18, 12:12, and 13:15.
11. Verified every 10–13 base layout with the production `solve2` implementation: all 65 layouts have N² cells, exactly N regions, and exactly one solution.
12. Canonicalized region labels and all eight geometric transforms: there are no duplicate bases, every base has eight distinct orientations, and the resulting display counts are 10:160, 11:144, 12:96, and 13:120.
13. Independently calculated valid dinosaur answer permutations under the row/column/non-touching rules as 6:90, 7:646, 8:5,242, 9:47,622, 10:479,306, 11:5,296,790, 12:63,779,034, and 13:831,283,558; these are answer patterns, not fixed puzzle layouts.
14. Verified both JavaScript files with `node --check`, confirmed `js/data.js` loads before `js/main.js`, and served the app locally; `index.html`, `js/data.js`, and `js/main.js` all returned HTTP 200.
15. The final working-tree check found an unrelated `index.html` version-label change from v1.9.3 to v1.9.6 that was not made by this analysis; it was inspected, left untouched, and does not affect the board-count results.

## Result summary

| Size | Fixed base layouts | Distinct geometric display variants | Valid answer patterns |
|---:|---:|---:|---:|
| 6×6 | 0 | 0 | 90 |
| 7×7 | 0 | 0 | 646 |
| 8×8 | 0 | 0 | 5,242 |
| 9×9 | 0 | 0 | 47,622 |
| 10×10 | 20 | 160 | 479,306 |
| 11×11 | 18 | 144 | 5,296,790 |
| 12×12 | 12 | 96 | 63,779,034 |
| 13×13 | 15 | 120 | 831,283,558 |

## Final status

- Complete. The recommended fixed-puzzle count is the base-layout column; geometric variants are potential presentations and answer patterns are not puzzle-layout counts.
- Commit hash: pending (no commit requested).
