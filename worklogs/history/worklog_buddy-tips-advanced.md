# worklog_buddy-tips-advanced

- 任務：驗證使用者提出的 5 條「顏色計數／相鄰接觸」進階解謎秘訣，修飾後加入隨行夥伴閒聊提示（`BUDDY_TALK`）
- 日期：2026-10-13
- Task ID：buddy-tips-advanced

## 步驟紀錄

1. 遊戲規則研究：本遊戲為「每行／每列／每個顏色區塊恰 1 個隱藏物（恐龍／寶箱／石頭），且隱藏物之間連斜角都不能相鄰」的解謎（js/main.js:440 註解、`buddyAutoExclude` 的同行/同列/周圍八格邏輯 js/main.js:1236-1243、玩法說明「高冷法則」）。閒聊提示資料為 `BUDDY_TALK` 陣列（js/main.js:581-587），其中尾段 7 條為 💡 開頭的策略提示，由 `pickTalk()` 在遊戲中隨機抽用。（跨工作階段重啟後補記）
2. 秘訣驗證：逐條對照規則推演，5 條全部正確——
   - 秘訣 1（N 行含 N+M 色其中 N 色不出行外）：N 行恰有 N 個隱藏物，N 個不出行外的顏色各貢獻 1 個且全在行內，行內名額用滿 → 行內屬於其他 M 色的格子必無隱藏物，可 ✕。
   - 秘訣 2（N 行恰只有 N 色）：行內 N 個隱藏物顏色互異且只有 N 色可用 → 每色各 1 個都在這幾行 → 這些顏色在行外的格子可 ✕。
   - 秘訣 3（某色只剩 2 格）：隱藏物必在其中一格 → 同時貼著（連斜角）這 2 格的格子無論如何都與實際隱藏物相鄰 → 可 ✕。（推廣：2 格不一定要相鄰也成立）
   - 秘訣 4（某色為 L 形 3 格）：同時貼著 3 格的格子＝2×2 的缺口格，無論藏在哪格都相鄰 → 可 ✕。
   - 秘訣 5（某色為直線 3 格）：同時貼著 3 格的格子＝中間格兩側那 2 格 → 可 ✕。
3. 版控盤點（續行階段）：工作樹混有前次工作階段 6 項已驗證但未提交的變更（js/main.js 241 行、index.html 47 行等）＋暫存區已有 38 個 worklogs 檔案移動；依 pending-work-inventory 結論「提交範圍待使用者決定」，本次採手術式提交：只提交本任務的 `BUDDY_TALK` hunk 與本 worklog，不動其他暫存／未提交內容（比照 d502f11／fd999e8 前例，亦不夾帶 index.html 版本號——版本行與其他任務變更混在同一 hunk 無法切割，1.9.10→1.9.14 提升留待使用者決定）。`BUDDY_TALK` 經 grep 確認僅 main.js 定義一處、無重複。
4. 文案修飾並加入 `BUDDY_TALK`（js/main.js:586 尾端追加 5 條，沿用 💡 開頭／單引號逗號分隔／打 ✕ 用語）：
   - 「N 行裡若有 N 種顏色完全沒延伸到行外，這幾行剩下的格子都能打 ✕！（列也適用）」
   - 「N 行裡剛好只有 N 種顏色，這些顏色就各藏一個在這幾行——行外同色的格子都能打 ✕！（列也適用）」
   - 「一種顏色只剩 2 格——無論藏在哪格，同時貼著這 2 格的格子（連斜角）都能打 ✕！」（依驗證結論推廣為不限定相鄰）
   - 「一種顏色是 L 形 3 格，同時貼著這 3 格的格子（L 的缺口）能打 ✕！」
   - 「一種顏色排成直線 3 格，同時貼著這 3 格的格子（中間格的兩側）能打 ✕！」
5. `node --check js/main.js` 通過；grep 確認「進階：」出現 5 次。
6. 瀏覽器實機驗證（`python -m http.server` 8975 新 origin 避快取）：index.html 載入正常（標題 v1.9.14）、console 無錯誤；`BUDDY_TALK` 共 72 條（原 67＋新 5）；`doBuddyChat()` 渲染新提示至 #dlg-text（DOM 內容＝「伴伴：💡 進階：N 行裡若有 N 種顏色…」）並截圖確認伴伴對話卡視覺正常；`curl` 檢查 index.html／js/main.js／js/data.js／js/tower.js／css/style.css 全部 HTTP 200。
7. 手術式提交：從 `git diff js/main.js` 萃取出僅含 `BUDDY_TALK` 行的單一 hunk 製成 patch，以暫存索引（`GIT_INDEX_FILE`）read-tree HEAD → apply --cached → 加入本 worklog → write-tree → commit-tree → update-ref，產生提交 6f90267（僅 js/main.js 1 行＋本 worklog）；提交後 `git reset HEAD -- js/main.js` 對齊真實索引並 `git add` 本 worklog，複核：其他 38 個暫存檔與 241 行未提交變更全部保持原狀未動。
8. 依 AGENTS.md「HTML reports」慣例產出自包含繁中報告 `buddy_tips_report.html`（需求與結論、逐條驗證表、遊戲內最終文案、驗證與版控）；`python -m http.server` 8976 驗證：`curl` HTTP 200、瀏覽器實開標題／章節／表格渲染正常、console 無錯誤（截圖確認）。

## 最終狀態

- 完成：5 條進階排除秘訣（顏色計數×2、共同接觸×3）經規則推演驗證全部正確，修飾為「💡 進階：」格式加入隨行夥伴閒聊提示 `BUDDY_TALK`（js/main.js:586，總數 67→72）。
- 驗證：`node --check` 通過；瀏覽器實機（新 origin :8975）載入正常、console 無錯誤、新提示經 `doBuddyChat()` 渲染正確（DOM＋截圖）；`curl` 五項資源全 200；報告頁（:8976）HTTP 200 且瀏覽器渲染正常。
- 已改檔：js/main.js（BUDDY_TALK 追加 5 條）、worklogs/worklog_buddy-tips-advanced.md（新增，後封存至 history/）、buddy_tips_report.html（新增）
- Commit：6f90267（Add five advanced elimination tips to buddy chat，僅含 main.js 一行變更與本 worklog 兩檔；工作樹中其他暫存／未提交變更未動）；0a9989a（hash 回填）、fc3309b（worklog 封存）
