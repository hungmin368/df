# worklog_intro_video_opening

- 任務：以 `assets/game.mp4` 做進入遊戲的開場畫面（影片播畢／跳過後接既有 logo 飛入 splash → 主選單）
- 日期：2026-10-16
- Task ID：intro-video-opening

## 步驟紀錄

1. 盤點現況：開場流程為 `#splash` 滿版 logo（0.5s 停留＋680ms 飛入 `#menu-logo`）→ 首次啟動播序章故事（`introStoryOnce`，保險計時 9s）。`assets/game.mp4` 已存在（2,444,781 B）。
2. 影片規格偵測（ffprobe 不可用，改以 Node 解析 MP4 box、cv2 抽幀目視）：768×768 方形、24fps、158 幀、6.58s、含 AAC 音軌（handler: soun）。內容：恐龍蛋孵化 → 伴伴破蛋登場 → 結尾帶出遊戲 LOGO（左上）。抽幀用暫存 PNG 已刪除。
3. 實作（未更動版本號 v1.9.17，避免與其他 session 未提交的版本號修改產生 hunk 重疊）：
   - `index.html`：`<body>` 加 `intro-video-on` class；`#splash` 前新增 `#intro-video` 層（`<video id="intro-vid">` ＋ `#intro-skip` 跳過鈕 ＋ `#intro-sound` 開聲音鈕，預設隱藏）；`noscript` 樣式同步隱藏 `#intro-video`。
   - `css/style.css`：檔尾新增 `#intro-video` 樣式（z-index 400、森林色系漸層底、影片 768 方形 `object-fit:contain` 完整保留構圖與結尾 LOGO、`.iv-out` 淡出、`body.intro-video-on #splash{display:none}`）。
   - `js/main.js`：splash IIFE 改名為 `startSplash()`（行為不變，開頭呼叫 `armIntroSafety()`）；原頂層 `setTimeout(introStoryOnce, 9000)` 改為 `armIntroSafety()`（影片播完才起算，避免序章故事蓋在影片上）；新增開場影片 IIFE：嘗試含聲音自動播放 → 被擋則靜音重播並顯示「🔇 開啟聲音」鈕 → 連靜音都被擋則直接進遊戲；`ended`／`error`／跳過鈕／14s 保險計時 → 淡出移除影片層 → `startSplash()`。
4. 本機 HTTP 驗證（`python -m http.server 8123`，curl：index/game.mp4/main.js 全 200）＋瀏覽器（SophCode controlled browser）逐項驗證：
   - 影片自動播放：`readyState 4`、`currentTime` 前進、本環境允許含聲音自動播放（`muted:false`），畫面截圖確認方形構圖完整（蛋孵化 → 伴伴 → LOGO 收尾）。
   - 播畢路徑：`ended` → `#intro-video` 移除、`body` class 清除 → splash logo 飛入 → 主選單開啟。
   - 跳過鈕：點擊 `#intro-skip` → 同上，立即進主選單。
   - 首次啟動：清空 localStorage 重載 → 影片 → splash → 自動播出序章「熄滅的第一盞星」，`dinodoku-story={"intro":1}` 正確寫入。
   - 開聲音鈕：顯示後點擊 → `muted:false`、`volume:0.85`、按鈕隱藏。
   - 降級路徑：將影片 `src` 換成不存在檔並 `load()` → `error` → 直接進主選單，不卡開場。
   - 回歸：從選單開 4×4 局，盤面 16 格正常渲染、可遊玩。
   - console：無遊戲錯誤（唯一一筆 `el.click is not a function` 來自測試工具點擊 SVG 的方式，與遊戲碼無關）。
   - 未竟事項：真實瀏覽器對「含聲音自動播放被拒」的分支（本環境不擋）僅能以程式碼審查與開聲音鈕行為間接驗證；實機 iOS Safari 未測。
5. 提交策略：工作區含其他 session 的未提交修改（index.html／main.js／style.css 的故事 v2 UI、AGENTS.md、.gitignore 等），沿用「僅暫存本任務路徑」慣例——三個共用檔以「HEAD 內容＋僅本次改動」重建 blob 後 `update-index` 暫存，另正常加入 `assets/game.mp4` 與本 worklog，確保不掃入他人未提交工作。

## 最終狀態

- **已完成**。
- 交付 commit：`aa4bc3e`（已推送至 `origin/main`）。
- 改動：`index.html`（＋`#intro-video` 層與 body class）、`css/style.css`（＋開場影片樣式）、`js/main.js`（`startSplash()` 化＋影片控制 IIFE＋`armIntroSafety()`）、`worklogs/worklog_intro_video_opening.md`。
- `assets/game.mp4` 先前已入庫（2,444,781 B、768×768、6.58s、含音訊），本次直接引用。
- 驗收：影片自動播放、跳過、播畢接 logo 飛入、首次啟動序章、開聲音鈕、影片載入失敗降級、4×4 開局回歸，全數通過；console 無遊戲錯誤。
- 提交隔離：其他 session 的未提交修改（故事 v2 UI、AGENTS.md、.gitignore 等）未納入本 commit，仍保留於工作區。
- 已知限制：真實瀏覽器擋「含聲音自動播放」的分支（→ 靜音播放＋開聲音鈕）以程式碼審查與按鈕行為驗證，未在實機 iOS Safari 測試。
