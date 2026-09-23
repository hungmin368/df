# 主選單版面合理化（紅框1/2/3）

- 日期：2026-09-23
- 任務 ID：menu-layout-compact
- 需求來源：使用者附圖三處紅框標註
  - 紅框1：主選單頂列（logo＋圖鑑完成度橫幅）等比例縮小，讓出高度給地圖
  - 紅框2：隨行夥伴對話框——恐龍名字移到圖片上方置中、星星移到圖片下方、盡可能縮小對話框高度；進入方格遊戲的對話框一併處理
  - 紅框3：底部選單「玩法說明」改「玩法」，並縮小選單讓出高度給地圖
- 備註：依使用者要求，完成後不上傳（不 commit、不 push）

## 步驟記錄

### 步驟 1：紅框1——縮小主選單頂列（css/style.css）
- 結果：`#menu-logo img` 最大寬度 240px→186px（等比例縮小，logo 為 451×178 約 2.53:1，高度約省 22px）；`#dex-banner` padding 9px 12px→6px 10px、圓角 16→14、間距 8→7；`.db-book` 28→22px、`.db-num` 21→17px（含 `.db-num span`）、`.db-label` 10.5→9.5px、`.ld-pct` 14→12px；`.menu-top` gap 12→10px、margin-bottom 12→8px。手機版（≤620px）logo 180→150px。
- 驗證：待本機檢查（步驟 5）。

### 步驟 2：紅框2——對話框重排並縮小高度
- index.html：`#dlg` 內新增 `#dlg-side` 欄位（`#dlg-name`→`#dlg-ava`→新增 `#dlg-stars` 垂直排列），`#dlg-name` 自 `#dlg-main` 移除。
- js/main.js `renderBuddy()`：名字 `textContent` 寫入 `#dlg-name`、星級寫入 `#dlg-stars`；無夥伴時清空 `#dlg-stars`。遊戲中對話框為同一 `#dlg` 元素（syncDlg 在 body/選單間搬移），一併生效。
- css/style.css：`#dlg` padding 9/12/8→7/10/7；頭像 74→60、圖 64→50、陰影縮小；`#dlg-text` min-height 44→23px；`#dlg-name` 改側欄置中＋省略號；新增 `#dlg-stars`（10.5px 金色）。手機版（≤480px）頭像 48、圖 38、文字 min-height 21px。
- 驗證：待本機檢查（步驟 5）。

### 步驟 3：紅框3——底部選單改「玩法」並縮小
- index.html：`#menu-help` 按鈕文字「玩法說明」→「玩法」。
- css/style.css：`.menu-nav` margin 14→10、padding 9/6/10→6/4/6、gap 8→6、圓角 16→14；`.mnav` padding 9/2/7→6/1/5、圓角 12→10、gap 3→2；`.mnav-ic` 26→22px、`.mnav-tx` 13→12px。手機版（≤620px）`.mnav` padding→5/1/4、圖示 22→19px、文字 11→10.5px、`.menu-nav` padding→5/3/5、上距 10→8。
- 驗證：待本機檢查（步驟 4）。

### 步驟 4：本機驗證（python3 -m http.server 8321）
- `curl` 檢查 index.html／css/style.css／js/main.js 皆 200。
- 桌面版（約 1264px）：主選單三處正確（logo 縮小、對話框名字在上星星在下、「玩法」按鈕）；以 `openLevel(4)` 進入 4×4 關卡，遊戲中對話框同樣名字置上／星星置下，高度 111px（舊版約 118px+），棋盤與按鈕區正常，`--dlgh` ResizeObserver 正常同步。
- 手機版（tmp_mobile_test.html 內嵌 390×800 與 360×640 iframe）：主選單三處正確，地圖區域明顯變高；手機版對話框頭像 48px、版面緊湊；長出沒提示文字造成的高度屬內容換行（原有行為），與本次最小高度調整無關。
- Console：遊戲頁面（127.0.0.1:8321）無任何錯誤訊息。
- 結果：通過。

### 步驟 5：「退出遊戲」→「退出」（index.html）
- `#menu-exit` 按鈕文字改為「退出」。驗證：待步驟 8。

### 步驟 6：對話框再縮高——聊天文字縮一級＋名字併入聊天訊息
- index.html：移除 `#dlg-side` 內的 `#dlg-name`（名字移入聊天訊息），側欄剩頭像＋星星。
- js/main.js：新增 `buddyTag()` 產生「<b>伴伴：</b>」前綴（無隨行夥伴時回傳空字串）；`renderBuddy` 初始問候、`doBuddyChat`、`tutShow`（教學文字）一律加前綴；移除 `#dlg-name` 寫入。
- css/style.css：聊天文字 14→13px、最小高度 23→21px（手機 13→12.5px、21→20px）；刪除 `#dlg-name` 樣式；頭像上方留白移除（margin-top→0）。側欄高度由 ~94px 降為 ~77px（手機 ~63px）。
- 驗證：待步驟 8。

### 步驟 7：頂列靠上邊界＋版號貼蛋殼邊
- css/style.css：`#ov-menu` padding 20/20→6px/12px；`#ov-menu .modal`（桌面）height calc(100vh - 40px)→calc(100vh - 18px)、padding-top 26→12px；手機版 `#ov-menu` 上 padding 6→4px、modal 上 padding 14→8px、高度改 calc(100dvh - 10px)。
- `#menu-logo` flex:1→flex:none，容器貼合 logo 圖片寬度，`.ver-badge`（right:-4px bottom:-2px）落在 logo 圖右下角蛋殼邊，不再被拉向圖鑑橫幅。

### 步驟 8：本機驗證（python3 -m http.server 8321）
- `curl` 檢查 index.html／css/style.css／js/main.js 皆 200 且為新版內容。
- 桌面版主選單：「退出」按鈕正確；對話框顯示「<b>伴伴：</b>準備好了！我們一起出發吧！」（名字前綴、星星在圖片下方、無上方名字列）；頂列明顯貼近上邊界；版號 v1.9.3 緊貼 logo 右下角蛋殼邊。
- 遊戲中（openLevel 4×4）：對話框高度 95px（調整前 111px），側欄 77px；聊天與教學文字均以「伴伴：」開頭（tutShow／tutHide 實測）；`--dlgh` 同步正常。
- 手機版（390×800、360×640 iframe）：四項調整皆正確，地圖區域持續受益。
- Console：遊戲頁面（127.0.0.1:8321）無錯誤訊息。
- 結果：通過。

### 步驟 9：複驗（上傳前，python -m http.server 8123）
- curl 確認 index／css／js（v=1.9.5）皆 200；瀏覽器複驗：logo max-width 186px、「玩法」「退出」按鈕正確、`#dlg-name` 已移除、`#dlg-stars` 顯示星級、聊天文字含「<b>伴伴：</b>」前綴、對話框高度 95px；遊戲中（openLevel 4）對話框同步搬移且帶前綴；重新載入無新主控台錯誤。驗證後已關閉服務。
- 結果：通過。

## 最終狀態
- 紅框1/2/3 與後續四項調整（退出按鈕、對話框再縮高、頂列靠邊、版號定位）全部完成，並通過本機桌面／手機／遊戲中驗證，console 無錯誤。
- 依 AGENTS.md 慣例：本工作日誌連同 col-number-alignment 任務變更一併提交（兩任務變更交錯於相同檔案），commit hash 回填於後續提交。
- commit hash：Pending（完成驗證後回填）
