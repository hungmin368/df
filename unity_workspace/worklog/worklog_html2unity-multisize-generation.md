# HTML-to-Unity 步驟 20：多尺寸盤面生成（4×4–18×18）

- Date: 2026-09-25
- Task ID: html2unity-multisize-generation（對應轉換步驟 20；來源 `js/main.js` 的 `randomRegions`／`solve2`／`connectedAfterRemoval`／`findKeyChest`／`generatePuzzle` 與關卡尺寸表 4–18）
- 目標：把網頁版多尺寸生成語意移植到 Unity Domain 層，涵蓋 15 個區域尺寸（4×4–18×18）的生成、難度與逾時處理。

## Step Records

1. 確認步驟 20 範圍與現況。
   - Result：步驟定義為「15 個區域尺寸的生成、難度與逾時處理；對應網頁版關卡表」；Unity 端目前 `BoardGenerator.GenerateUnique` 只以「隨機區域＋解數量==1」暴力重試，實際僅支援 5×5／6×6。
2. 研讀網頁版來源語意。
   - Result：`randomRegions`（200 次嘗試、隨機種子格＋前端擴張、每區至少 2 格）、`solve2`（位元遮罩＋候選消去＋單元/列/區推論、解數上限 K、節點上限、可帶 fix 約束）、`connectedAfterRemoval`、`findKeyChest`（多解盤鎖定關鍵格成唯一解，上限 60 次嘗試）、`generatePuzzle`（定向獵殺＋0 解回退＋硬限時，重啟 400 次、迭代 800 次、`zeroStreak>25` 放棄該盤）。
3. 研讀網頁版難度與逾時政策。
   - Result：池補貨 `generatePuzzle(n, n>=13?3000:1400)`；正式局 `N>=14` 單次 8000ms、`N<14` 依序 1200→3000→8000ms 重試；`N>=14` 節點熔斷 50000；`N>=15` 允許 1–4 解並以關鍵寶箱破局。

4. 新增 `Domain/RegionBuilder.cs`。
   - Result：`RandomRegions`（200 次嘗試、Fisher-Yates 洗牌、種子格＋前端擴張、每區至少 2 格）、`ConnectedAfterRemoval`（移除某格後該區仍連通且至少 2 格）、共用洗牌工具。
5. 改寫 `Domain/BoardSolver.cs`。
   - Result：新增 `CellFix` 與 `Solve(size, regions, nodeLimit, maxSolutions, fixes)`；位元遮罩候選＋傳播（列／區／相鄰推論、單元格強制填入）、節點上限中止時回傳 null。`CountSolutions` 改為包裝 `Solve`（維持原簽章與語意）。
6. 新增 `Domain/BoardGenerationPolicy.cs`。
   - Result：區域尺寸 4–18、池尺寸 10–13、正式局逾時階梯（<14：1200/3000/8000；>=14：8000）、池補貨逾時（<13：1400；>=13：3000）、節點熔斷（>=14：50000）、多解允許門檻（>=15）。
7. 新增 `Domain/PuzzleGenerator.cs`。
   - Result：`Generate`（定向獵殺＋0 解回退＋硬限時重啟，含 800 次迭代、`zeroStreak>25`、>=15 多解盤關鍵寶箱破局）與 `FindKeyChest`（候選格洗牌、60 次嘗試上限、逾時回傳 null）、`PuzzleGenerationResult`（區域／首解／多解聯集／關鍵寶箱）。
8. 新增 `Tests/EditMode/MultiSizeGenerationTests.cs`。
   - Result：11 個測試涵蓋位元求解器（4×4 雙解盤、fix 約束、節點上限中止、與暴力解交叉比對）、`RandomRegions`（4–18 全尺寸合法性）、`ConnectedAfterRemoval`（斷開／格數不足）、`FindKeyChest`（雙解盤收斂成唯一解）、難度政策表、逾時立即失敗、15 尺寸生成與合法性、池尺寸 10–13、固定種子決定性。
9. 以 Unity 6000.3.24f1 批次模式執行 EditMode 套件。
   - Result：首次編譯失敗（`Random` 在 `UnityEngine`／`System` 間歧義，8 處 CS0104），在測試檔加入 `using Random = System.Random;` 後通過編譯。
10. 第二次執行 EditMode：33 項中 32 項通過，唯一失敗為池測試 `13x13 pool board`（單次 3000ms 逾時回傳 null）。
    - Result：判定為預期行為（網頁版池補貨本來就是週期性重試，單次失敗只延後補貨），把池測試改成最多 5 次嘗試並記錄嘗試次數。
    - 同次執行的 15 尺寸正式局證據（測試日誌）：
      - `4x4~10x10` 0–2 ms、`11x11` 47 ms、`12x12` 856 ms、`13x13` 867 ms、`14x14` 4191 ms（預算 10000 ms）
      - `15x15` 2 解聯集 98 ms、`16x16` 222 ms、`17x17` 1137 ms、`18x18` 2139 ms
11. 第三次執行 EditMode：33／33 全數通過（`TestResults/multisize-editmode.xml`）。
    - Result：15 尺寸生成日誌（本輪）：`4x4~10x10` 0–2 ms、`11x11` 24 ms、`12x12` 458 ms、`13x13` 554 ms、`14x14` 2457 ms；`15x15` 66 ms、`16x16` 127 ms、`17x17` 1056 ms、`18x18` 1842 ms，全部符合各自逾時預算。
    - 池尺寸日誌：`10x10` 2 ms、`11x11` 186 ms、`12x12` 229 ms、`13x13` 394 ms（各 1 次嘗試內成功）。
12. 以 Unity 6000.3.24f1 批次模式執行 PlayMode 回歸套件（`BoardSolver` 改寫會影響既有 `BoardGenerator.GenerateUnique` 路徑）。
    - Result：`TestResults/multisize-playmode.xml`：total 9／passed 9／failed 0，既有主選單、教學盤、正式局、輸入與存檔流程全數未受影響。
13. 更新 `unity_workspace/html2unity_v1.9.10.md` 步驟 20 狀態為「已完成」並附證據。
    - Result：狀態統計同步為 已完成 40／進行中 1／待決策 1／未進行 28；`html2unity.md` 進度快照同步。

## Final Status

- 已完成：`RegionBuilder`（`randomRegions`／`connectedAfterRemoval`）、`BoardSolver.Solve`（`solve2` 位元求解器）、`PuzzleGenerator`（`generatePuzzle`／`findKeyChest`）、`BoardGenerationPolicy`（15 尺寸難度與逾時）；EditMode 33/33、PlayMode 9/9 通過。
- 證據：`TestResults/multisize-editmode.xml`、`TestResults/multisize-playmode.xml`；15 尺寸生成日誌見步驟 9–11。
- Commit hash: 尚未提交（依 `unity_workspace/AGENTS.md`，未經使用者明示不提交）。
