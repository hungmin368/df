# 龍塔攻略彈幕 — 本地模擬版實作

- 日期：2026-10-13
- 任務：實作龍塔攻略彈幕「本地模擬版」（資料存 localStorage，留言僅本機可見），對應 `dragon_tower_comments_report.html` 第九節 #6~#11、#13、#14。
- 設計依據：報告第八節（頂/底條帶、單向右→左、可開關、短句 30 字、龍塔預設開）。
- 狀態：進行中

## 步驟記錄

### Step 1：計畫與檔案盤點
- 新增檔案：`js/tower_comments.js`（彈幕引擎＋本地儲存，自建 DOM，不依賴載入順序）。
- 修改檔案：`index.html`（script 引入＋版本號 1.9.14→1.9.15）、`css/style.css`（彈幕樣式）、`js/main.js`（3 處鉤子：newRun 同步、resTowerUI 結果畫面入口、工程模式清存檔掃除新鍵）、`build_single_file.mjs`（內嵌新 js）。
- localStorage 鍵：`dinodoku-twcomments-<level>`（留言陣列）、`dinodoku-twname`（暱稱記憶）、`dinodoku-danmaku-on`（開關）、`dinodoku-twlast`（60 秒冷卻）、`dinodoku-twday`（單日上限），全部納入「清存檔」掃除。
- 規則：30 字上限、暱稱 12 字、同關 60 秒冷卻、單日 10 則、敏感詞黑名單、每關最多存 50 則；留言只存本機（UI 明示「本地測試版·僅存本機」），不造假資料。

### Step 2：撰寫 js/tower_comments.js（完成）
- IIFE 暴露 `window.TWDANMAKU={sync,onResult}`；自建 DOM（頂/底彈帶插入 #main、💬 開關鈕插入 #controls 首位、結果畫面輸入盒插入 #ov-result modal）。
- 掛鉤採 main.js 既有覆寫模式（同 winRound）：載入時包裝 `newRun`（每次新局同步 `sync(TOWER.level)`）與 `resTowerUI`（龍塔結果畫面顯示留言入口），main.js 幾乎零侵入。
- 播放：WAAPI `element.animate` 純 transform 右→左 10 秒、每帶 2 軌、軌道依「頭部間距」釋放、250ms 幫浦排程、冷門關播本地引導句（非假資料）。
- 送出：textContent 插入（防 XSS）、驗證長度→冷卻→單日額度→黑名單→存 localStorage→樂觀播放＋夥伴聊天回饋；無留言時 hide。
- `node --check` 語法通過。

### Step 3：整合四檔（完成）
- `index.html`：版本號 8 處 1.9.14→1.9.15；main.js 之後新增 `<script src="js/tower_comments.js?v=1.9.15">`。
- `css/style.css`：附加彈幕樣式（條帶/彈幕 pill/輸入列/結果盒/手機 720px 調整）。
- `js/main.js`：僅動「清存檔」——confirm 文案加「攻略彈幕」，並掃除 dinodoku-twcomments-*／twname／danmaku-on／twlast／twday（dev-reset 的 wipeAllRecords 本就掃全部 dinodoku-*，無需改）。
- `build_single_file.mjs`：讀取 tower_comments.js、加入 sanity check、新增 script 內嵌 replace 規則。

### Step 4：瀏覽器完整驗證（完成，http://localhost:8765）
- 驗證過程發現並修復 2 個問題：
  1. **條帶寬度塌縮**：`#main` 為 flex column + align-items:center，空條帶被壓成 2px；`css/style.css` 的 `.dk-band` 加 `align-self:stretch` 修復（實測寬 1220px）。
  2. **WAAPI 動畫凍結**：自動化瀏覽器中 `element.animate()` playState 雖為 running 但 currentTime 停在 0；將移動改寫為 **rAF + delta-time 純 transform 更新**（`ensureLoop`/`tick`/`flying[]`，stopPlay 取消 rAF），幀率無關、真實瀏覽器行為不變。
- 功能驗證全數通過：
  - 💬 開關：off → 上下條帶 hidden＋按鈕 off 樣式＋`dinodoku-danmaku-on`="0"；on → 恢復＋"1"。
  - 一般關卡隔離：dev 跳一般第 1 局後 `TOWER.level=0` → 條帶與 💬 按鈕全隱藏、無殘留彈幕。（註：dev-jump 僅接受 4~18，第一次填 1 無效屬測試操作失誤，非程式問題）
  - 重進龍塔第 1 關：庫存 4 則留言依序重播（上帶 2＋下帶 2，符合每帶 2 軌）。
  - 送出：入庫、樂觀播放、按鈕「已送出 ✓」1.5 秒、暱稱「小龍」記憶、每日計數遞增、夥伴聊天回饋文案。
  - 同關 60 秒冷卻：年齡 22 秒時送出被擋。
  - 黑名單（垃圾遊戲）、URL、單日 10 則上限：三則測試留言全數被擋（留言數維持 7、計數停在 10）。
  - 結算畫面：💬 攻略留言按鈕（龍塔過關時顯示）→ 展開輸入盒＋「本地測試版」提示 → 送出入庫成功。
  - 工程模式清存檔：confirm 覆寫為 true 後點擊，dinodoku-twname／twcomments-1／twday／danmaku-on 全數清空。
- 已知環境限制：此自動化瀏覽器 rAF 約 1.3fps（2366ms 僅 3 幀），畫面飄動無法以錄製方式目視確認；移動方向（x 遞減）與 delta-time 數學已逐幀驗證正確，真實瀏覽器不受影響。
- console 檢查：僅一筆注入測試腳本自身的 null 錯誤（時序產物，重跑即正常），遊戲程式碼零錯誤。

### Step 5：單檔打包驗證（完成）
- `node build_single_file.mjs` → `dragonfinder_v1.9.15.html`（29.5 MB / 30,950,796 chars）產出成功。
- 抽查內嵌：`TWDANMAKU`×3、`dk-band`×5、`dinodoku-twcomments-`×3 皆存在；`tower_comments.js` 外部 script 標籤與 `src="js/` 引用數 = 0（sanity check 亦通過）。該檔為 gitignore 對象，僅供發布。

## 最終狀態
- 狀態：✅ 完成（本地模擬版；雲端共用版待使用者提供 Supabase 帳號後接續報告第九節 #1~#5、#12）
- 本機驗證：http.server + 自動化瀏覽器全項通過；單檔打包通過。
- 提交：未提交（使用者未要求 commit/push；待指示後再提交推送）。

