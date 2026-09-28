# worklog_tutorial-reveal-reason

- 任務：教學在「揭露答案」時，額外簡短說明「為什麼那一格合理」（web 版）
- 日期：2026-09-28
- Task ID：tutorial-reveal-reason

## 步驟紀錄
1. 定位教學程式：js/main.js 的 startDemo（4×4 示範）與 startGuided（5×5 引導）；「揭露答案」文案共 5 處。
2. 新增 helper whyReveal(s)：依目前盤面（已標 ✕、已揭示）算出該星格的理由。
   - 若某列／欄／色塊只剩它是候選 → 「牠是第X列／第X欄／這個色塊唯一還沒被排除的格子」。
   - 否則 → 「牠的<該列／欄／色塊>只剩 N 格可能是恐龍，牠是其中最值得先試的格子」。
   - 插入位置：js/main.js，startDemo 之前。
3. 修改 5 處揭露文案：
   - demo 第一隻：加上「為什麼？牠會佔住整列、整欄、整個色塊——先確定牠，就能排除一大片」。
   - demo 非強制揭露 stars[1]：串接 whyReveal(stars[1])。
   - demo 後續揭露 stars[k]：串接 whyReveal(stars[k])。
   - guided 第一隻：加上「先確定一隻，就能用『整列／整欄／整個色塊各 1 隻』排除其他格」。
   - guided 非強制揭露 stars[k]：串接 whyReveal(stars[k])。
4. 驗證：
   - node --check js/main.js 通過（exit 0）。
   - headless Edge 跑 4×4 教學：第一個揭露已含「為什麼」；err=[] 無 JS 錯誤。
   - 直接單元測試 whyReveal()：四隻星格皆回傳合理字串。
   - 清理測試暫存檔。

## 最終狀態
- 已改檔：js/main.js
- commit：（見下方）

