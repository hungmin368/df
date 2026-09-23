# Mobile Play Layout Fix

- Date: 2026-09-23
- Task ID: mobile-play-layout
- Task: 手機闖關畫面按鈕浮起遮盤 / HUD 切邊 / 棋盤超高

## Steps

1. 診斷：#controls sticky（style.css:230）在手機視窗高度不足時被拉起蓋住棋盤；按鈕換行多排；棋盤未扣除周圍 UI 高度。
2. style.css：sticky 改為僅桌機（min-width:900px and min-height:640px）啟用；新增 max-width:720px 區塊（壓縮 header/HUD/狀態列、按鈕單排、#board-area 依 --boardw 縮放、隱藏 #foot）。
3. main.js：新增 fitMobileBoard() 以實測 header/狀態列/按鈕列/伴伴列高度設定 --boardw；掛載於 ResizeObserver sync、renderBoard、window resize。
4. index.html：快取版本 v=1.9.3 → v=1.9.4（第 8、9、338、339 行共 4 處）。
5. 本地驗證（HTTP）：`python -m http.server 8123 --bind 127.0.0.1` 起服務，curl 檢查 `/`、`/css/style.css?v=1.9.4`、`/css/fonts.css?v=1.9.4`、`/js/data.js?v=1.9.4`、`/js/main.js?v=1.9.4`、`/docs/cmd_example.html`、`/docs/task-delivery-guide.html`、`/worklogs/worklog_mobile-play-layout.md` 皆回 200；grep 線上內容確認 v=1.9.4×4、fitMobileBoard×4、max-width:720px 存在；驗證後已關閉服務。
6. 瀏覽器實測：載入頁面無應用程式錯誤；點「起源地」開局，4×4 棋盤 16 格正常渲染；桌機視窗（1264×835）下 `--boardw` 留空、`#controls` 維持 sticky；以 innerWidth 覆寫模擬 390px 手機視窗呼叫 fitMobileBoard()，`--boardw` 設為 366px（390×0.94）且重複呼叫數值穩定，回到 >720px 時正確移除；點格子互動（標記 ✕／捕捉器捕獲／新夥伴對話框）與 localStorage 進度保存皆正常；重新載入後主選單渲染正常。

## Verification

- 通過：所有頁面與資產 HTTP 200 且線上內容含新版版本號與新程式碼；瀏覽器開局、互動、手機/桌機兩分支的 fitMobileBoard 行為與重載皆正常，無應用程式主控台錯誤。

## Status

- Final：任務變更與工作日誌已提交（bd8cd4f），本地 HTTP 與瀏覽器驗證通過，commit hash 回填於後續提交（慣例同 61c4eb4）。
