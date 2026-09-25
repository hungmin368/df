# HTML-to-Unity 步驟 19：盤面池預生成與旋轉鏡像

- Date: 2026-09-25
- Task ID: html2unity-board-pool（對應轉換步驟 19；來源 `js/main.js` 的 `poolInit`／`poolRefill`／`transformBoard`／`poolTake` 與 `js/pool1518.js`）
- 目標：在 Unity 專案加入盤面池（閒置時預生成、取用時套用 8 種旋轉／鏡像變體），並讓 6×6 正式局優先使用池中盤面。

## Step Records

1. 讀取 `AGENTS.md`、`unity_workspace/AGENTS.md`、`html2unity.md`、`html2unity_v1.9.10.md`，確認步驟 19 的範圍與追蹤規則。
   - Result：步驟 19 定義為「盤面池預生成與旋轉鏡像」，對應網頁版 `pool1518.js`／`poolInit`／`poolRefill`／`transformBoard`（8 種變體）；狀態需在任務開始改「進行中」、結束附證據改「已完成」。
2. 確認 Unity 編輯器可用性。
   - Result：`C:\Program Files\Unity\Hub\Editor\6000.3.24f1\Editor\Unity.exe` 存在，沿用既有批次測試指令（`-batchmode -nographics -runTests`，不加 `-quit`）。
3. 研讀網頁版來源語意。
   - Result：`poolInit` 從 `POOL_DATA`（10–14）與 `POOL_EXTRA`（15–18）載入既有盤面；`poolTake` 隨機取出並呼叫 `transformBoard` 套用 8 種變體；`transformBoard` 先轉置（T&1）、再上下鏡像（T&2）、再左右鏡像（T&4）；`poolRefill` 僅在閒置時每 2600ms 補 1 片，目標每尺寸 6 片，且跳過含關鍵寶箱的盤面。
4. 檢視 Unity 端現況。
   - Result：`Domain` 已有 `BoardPuzzle`／`BoardRules`／`BoardSolver`／`BoardGenerator`／`GameSession`；`AppBootstrap.StartFormalRound` 目前以 `BoardGenerator.GenerateUnique(6, seed)` 即時生成，尚無池化。
5. 新增 `Domain/BoardTransforms.cs`。
   - Result：`Map`／`Apply`／`ApplyToAnswer`，變體數 8，運算順序與網頁版 `transformBoard` 完全一致（轉置→上下→左右）。
6. 新增 `Domain/BoardPool.cs`。
   - Result：`BoardPool(targetPerSize, params sizes)`、`Count`／`NeedsRefill`／`SizesNeedingRefill`／`TryAdd`／`Take`（取出後套用隨機變體）／`RefillOnce`（閒置補貨一次，factory 回傳 null 代表跳過該盤面，對應網頁版跳過關鍵寶箱盤）。
7. 在 `BoardPuzzle` 新增 `Transform(variant)`。
   - Result：區域與答案一起套用同一變體，建構子會重新驗證區域與解答合法性。
8. 在 `AppBootstrap` 接線盤面池。
   - Result：`boardPool = new BoardPool(6, 6)`；`Update` 開頭呼叫 `PumpBoardPool()`（非 `Playing` 狀態且間隔 1 秒才補 1 片）；`StartFormalRound` 改為優先 `boardPool.Take(6, random)`，池空時回退 `BoardGenerator.GenerateUnique(6, seed)`；新增 `PooledFormalBoardCount` 供測試觀察。
9. 新增 `Tests/EditMode/BoardPoolTests.cs`。
   - Result：8 個測試涵蓋變體合法性與唯一解保持、與網頁版方位語意一致、答案與區域同步搬移、取用套用隨機變體且移出池、空池回傳 null、補貨到目標數並跳過被拒盤面、固定種子決定性、6 片 6×6 補貨時間預算。
10. 新增 PlayMode 測試 `BoardPoolPrewarmsWhileIdleAndFormalRoundTakesFreshBoard`。
    - Result：驗證選單閒置時會逐步暖池、正式局取用後池數量減 1 且取用盤面仍為唯一解，並確認遊玩中不補貨。
11. 更新 `unity_workspace/html2unity_v1.9.10.md` 步驟 19 狀態為「進行中」。
    - Result：狀態統計同步為 已完成 38／進行中 2／待決策 1／未進行 29。
12. 以 Unity 6000.3.24f1 批次模式執行 EditMode 套件。
    - Result：`Unity.exe -batchmode -nographics -runTests -testPlatform EditMode`（不加 `-quit`），輸出 `TestResults/pool-editmode.xml`。
      - `test-run`：total 21／passed 21／failed 0（含新增 `BoardPoolTests` 8 項全過）。
      - 時間預算測試日誌：`Filled a 6-board 6x6 pool in 17 ms (avg 2.8 ms per board).`（門檻 3000ms）。
13. 以 Unity 6000.3.24f1 批次模式執行 PlayMode 套件。
    - Result：`-runTests -testPlatform PlayMode`，輸出 `TestResults/pool-playmode.xml`。
      - `test-run`：total 9／passed 9／failed 0；含新增 `BoardPoolPrewarmsWhileIdleAndFormalRoundTakesFreshBoard`（暖池後取用、池量遞減、盤面仍為唯一解、遊玩中不補貨）。
14. 更新 `unity_workspace/html2unity_v1.9.10.md` 步驟 19 狀態為「已完成」並附證據。
    - Result：狀態統計同步為 已完成 39／進行中 1／待決策 1／未進行 29；`html2unity.md` 進度快照同步更新。

## Final Status

- 已完成：實作（`BoardTransforms`／`BoardPool`／`BoardPuzzle.Transform`／`AppBootstrap` 暖池接線）＋EditMode 21 項、PlayMode 9 項批次測試全數通過。
- Commit hash: 尚未提交（依 `unity_workspace/AGENTS.md`，未經使用者明示不提交）。
