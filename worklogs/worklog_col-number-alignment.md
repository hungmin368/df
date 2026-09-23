# Column Number Alignment Fix

- Date: 2026-09-23
- Task ID: col-number-alignment
- Task: 棋盤上方欄位數字（1–13）相對下方欄位逐步偏右（手機、電腦皆會）

## Steps

1. 診斷：index.html 中 `#colcounts`（欄位數字列）直接放在 `#board-scroll` 內，寬度＝整個捲動容器；而棋盤 `#board` 在 `#mid` 內與 `#rowcounts`（22px）並排，寬度＝容器 − 27px（22px＋間距 5px）。兩者同為 `repeat(N,1fr)`，但數字列每欄比棋盤欄寬 27/N px，導致第 1 欄約 +1px、第 13 欄約 +26px 的線性右偏。瀏覽器量測證實（N=13）：offsets=[1,3,5,…,26]，ccWidth=476 / boardWidth=449。
2. 嘗試單純 CSS 補丁 `#colcounts{padding-right:27px}` 後量測歸零，但發現棋盤內容超出容器（橫向捲動，如手機上的 18×18）時棋盤會撐到 min-content 寬、與數字列寬度脫鉤，該情境仍不對齊，故改結構式修正。
3. index.html：新增 `#board-col` 容器，將 `#colcounts` 與 `#board` 包在同一 flex 直排容器內（兩者皆為 stretch 子元素，寬度永遠一致，正常與溢位捲動兩種情境皆對齊）。
4. style.css：新增 `#board-col{flex:1;display:flex;flex-direction:column;gap:5px}`；`#board` 移除 `flex:1`（在直排 flex 下會變垂直拉伸）；`#colcounts` 移除 `margin-bottom:5px`（改由父容器 gap 提供間距）。
5. index.html：資產快取版本號 v=1.9.4 → v=1.9.5（第 8、9、340、341 行共 4 處），確保玩家瀏覽器取得新 CSS。
6. 本地驗證（HTTP）：`python -m http.server 8137 --bind 127.0.0.1` 起服務，curl 檢查 `/index.html` 回 200，線上 style.css 含 `#board-col`、index.html 含新結構。
7. 瀏覽器實測（無快取問題，直接載入 v=1.9.5）：以 getBoundingClientRect 量測每欄數字中心與第 0 列對應格中心之偏移——桌面 N=13/10/6 與 340px 窄容器（模擬手機）N=13/6 全部為 0；窄容器 N=18（棋盤 504px 觸發橫向捲動）亦全部為 0。點格子標記 ✕、欄列計數更新正常，無應用程式主控台錯誤。
8. 複驗（上傳前）：`python -m http.server 8123 --bind 127.0.0.1` 起服務，curl 確認 index/css/js（v=1.9.5）皆 200 且線上內容含 #board-col×2、board-col、buddyTag 等新版標記；瀏覽器以 openLevel(4) 與 openLevel(13) 量測欄位偏移皆全 0；340px 窄容器觸發橫向捲動（hasHScroll）時 #board-col 與 #board 同寬、偏移仍全 0；重新載入無新主控台錯誤。驗證後已關閉服務。

## Verification

- 通過：所有測試尺寸（6/10/13/18）×（桌面/窄容器）欄位數字偏移皆為 0px；瀏覽器互動正常；HTTP 資產 200 且為新版內容。

## Status

- Pending commit（完成驗證後回填 commit hash）
