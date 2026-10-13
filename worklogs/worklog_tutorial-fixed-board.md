# worklog_tutorial-fixed-board

- 任務：第一次教學（4×4 示範／5×5 引導）改成預生成的固定盤面，讓每位首次玩家看到相同的教學盤
- 日期：2026-10-13
- Task ID：tutorial-fixed-board

## 步驟紀錄

1. 教學引擎研究：`startDemo()`（4×4 自動示範）與 `startGuided()`（5×5 玩家操作引導）原本使用 `generatePuzzle()` 隨機生成，教學步驟靠 `findForced()`／`whyReveal()` 動態推理；入手點為 `finishBoard()` 末端的教學派發（js/main.js:1124-1125）與 `newBoard()` 的龍塔預生成分支（js/main.js:1003-1018）。
2. 固定盤面設計（編碼格式同龍塔：每格一個 base-36 字元＝區域 id）：
   - 4×4 手工設計 `0001201122332333`（盤面 A A A B／C A B B／C C D D／C D D D）：4×4 滿足八向不相鄰的排列只有 2 種，區域設計破壞其中 1 種 → 唯一解 [1,3,0,2]。
   - 5×5 手工設計測試後發現仍有其他解存活，改寫暫存腳本 `tmp_tut_board.mjs`（已 gitignore）以排列回溯＋連通性檢查做自動搜尋，找到唯一解盤 `0000020001222314233142311`（row0 全 A），解 [2,4,1,3,0]。
3. 實作（js/main.js，`newBoard()` 前新增）：常數 `TUT_BOARDS={4:…,5:…}`；`newBoard()` 開頭加分支——`G.tutorial && TUT_BOARDS[N]` 時走 `towerDecode(N, code)` → `solve2(N, ro)`，恰 1 解才以 `finishBoard({cats, regionOf})`（cats＝r*N+sol[0][r]）生成固定盤；資料缺損或非唯一解則落入原本隨機生成流程（防禦性回退）。
4. 語法檢查：`node --check js/main.js` 通過。
5. 瀏覽器實機驗證（本機 :8977，清存檔模擬首次玩家）：
   - 4×4 首次進入：`G.tutorial='demo'`、`G.regionOf='0001201122332333'`、`G.cats=[1,7,8,14]`，與預生成盤一致；局內「重來」後盤面完全相同。
   - 示範自動播放於固定盤完整跑完：推理提示（第 2 列／第 3 列／第 3 欄）逐隻揭示，4/4 捕獲、結果畫面出現「去 5×5 引導 ▶」、`dinodoku-prog` 寫入 `tut4:true`。
   - 5×5 引導：進入即固定盤（`regionOf='0000020001222314233142311'`、`cats=[2,9,11,18,20]`）；以腳本驅動完整互動流程（✕ 三態練習→捕捉器切換→列／欄／斜角／色塊排除→4 隻逐一丟球），5/5 捕獲、`tut5:true` 寫入。
   - 教學後回歸：一般 4×4 兩次進入盤面互不相同、一般 5×5 亦為隨機盤，且 `G.tutorial` 皆為 null（不再觸發教學）。
   - 清存檔重測：再次進入 4×4 仍為同一固定盤（跨存檔狀態確定性）；「跳過教學」正常（設 `tut4`、回主選單；此時 5×5 因 4×4 未過關維持鎖定，屬既有解鎖邏輯）。
   - 插曲：教學中按「重來／放棄」會彈原生 `confirm()`，自動化瀏覽器無法關閉造成逾時假象；覆寫 `confirm` 後一切正常，屬遊戲既有行為、非本次變更缺陷。
   - console 僅剩歷史其他 origin（:8765）訊息與測試腳本自身時序錯誤，遊戲程式碼零錯誤。
6. HTTP 檢查：`/index.html`、`/js/main.js` 回應 200（:8977）。
7. 版控：工作樹混有前次工作階段多項未提交變更與暫存的 worklogs 搬移，比照 d502f11／fd999e8／6f90267 前例採手術式提交——只提交本任務的 `TUT_BOARDS` hunk、本 worklog 與驗證報告，不動其他內容（index.html 版本號提升留待使用者決定）。

## 最終狀態

- 完成：4×4 示範與 5×5 引導皆改為預生成固定盤，首次玩家每次所見一致；教學腳本在固定盤上完整可跑；教學後一般盤面維持隨機。
- 產出：js/main.js（`TUT_BOARDS`＋`newBoard()` 分支）、`tutorial_fixed_board_report.html`、本工作日志。
- Commit：8ca236f（Use pre-generated fixed boards for the first-time tutorials，僅含 js/main.js 的 `TUT_BOARDS` hunk、本 worklog 與 tutorial_fixed_board_report.html；工作樹中其他暫存／未提交變更未動）
