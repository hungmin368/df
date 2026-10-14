# 龍塔攻略留言板（含按讚）— 本地模擬版實作

- 日期：2026-10-14
- 任務 ID：tower-strategy-board
- 需求：在現有攻略彈幕之外，新增「攻略留言板」；可給留言按讚（👍 大拇指），**每個玩家在每一局（龍塔每一關）只能給 3 個讚**、**每個玩家在每一局只能留 1 則攻略留言**。
- 前置脈絡：彈幕為本地模擬版（`js/tower_comments.js`，資料存 localStorage；雲端共用版待 Supabase），設計依據 `dragon_tower_comments_report.html`（單一 tower_comments 資料源、讚數欄位、熱門排序）。
- 狀態：進行中

## 步驟記錄

### Step 1：計畫與現況盤點（完成）
- 讀取 `js/tower_comments.js`（彈幕引擎＋本地儲存）、`js/main.js`（newRun／resTowerUI 掛鉤、清存檔掃除）、`index.html`（版本 1.9.15、ov-result 結構、ov-help）、`css/style.css`（dk-* 樣式）。
- 確認後端尚未實作（全站零網路請求），本任務同彈幕採「本地模擬版」：留言與讚僅存本機 localStorage，UI 明示本地測試版。
- 「每一局」對應留言系統的錨定單位＝龍塔每一關（每關 1~2000 固定盤面、全玩家相同），故限制為：**每關 1 則留言、每關 3 個讚**，跨裝置/重試後仍對該關持續生效。
- 留言板與彈幕共用同一留言池 `dinodoku-twcomments-<level>`（雲端版即單表設計），留言板是清單檢視＋互動層。

### Step 2：資料模型與規則設計（完成）
- 留言物件新增欄位：`id`（唯一識別，按讚錨定用）、`lk`（讚數，預設 0）；舊資料讀取時自動補齊並回寫（輕量遷移）。
- 新 localStorage 鍵：
  - `dinodoku-twposted-<level>`：本機玩家在該關已留言的留言 id（每關一則）。
  - `dinodoku-twlikes-<level>`：本機玩家在該關按讚的留言 id 陣列（上限 3；再點一次收回、收回後釋放額度）。
- 規則變更：原「同關 60 秒冷卻」（dinodoku-twlast）被「每關一則」取代，不再寫入；保留單日 10 則上限、敏感詞黑名單、30 字／暱稱 12 字限制。
- 排序：留言板與彈幕佇列改「讚數多→新」熱門排序（對齊報告 4.2 API order=likes.desc,created_at.desc）。
- UI：留言板為獨立 overlay（z-index 高於 ov-result），入口＝遊戲中 controls「📋 留言板」鈕（龍塔限定）＋結果畫面「📋 攻略留言板」鈕（取代原結果畫面輸入盒，改開留言板）。彈幕「💬」鈕改名「💬 彈幕」以資區別，功能不變。
- 本地模擬版限制說明：本機留言池只有自己裝置的留言，故按讚對象（含自己的留言）皆可按，規則（3 讚／1 則）照常生效；雲端版上線後可再加「不可按自己的留言」限制。

### Step 3：實作 js/tower_comments.js（完成）
- 資料層：新增 `getList()` 正規化（補 `id`／`lk`、剔除損壞項、有異動才回寫）、`hotSort()`（讚多→新）、`getLikes()`、`findCm()`、`fmtTime()`。
- 留言板：`buildBoard()` 建立 overlay（`#ov-dkboard`，z-index 60 蓋過 ov-result）、`openBoard()`／`closeBoard()`、`renderBoard()`（標題列顯示「龍塔第 N 關 · 每關限 1 則留言 · 讚已用 x/3」、清單熱門排序、空狀態搶頭香文案、已留言時輸入列換成提示）、`cmNode()` 單則留言（暱稱＋時間＋內容＋👍 讚數鈕，已讚亮綠）、`toggleLike()`（按讚／再點收回，第 4 個讚被擋並以夥伴對話提示）、`paintLike()`／`paintSub()` 單點更新不重排。
- 送出規則改寫：移除同關 60 秒冷卻（dinodoku-twlast 不再寫入），改為「每關一則」（`dinodoku-twposted-<level>`）；保留單日 10 則、黑名單、30 字／12 字限制；新留言帶 `id`＋`lk:0`；板開啟中送出後即時重繪。
- 入口：遊戲中 controls 新增「📋 留言板」鈕（緊鄰「💬 彈幕」，龍塔限定顯示；💬 鈕由「攻略」更名「彈幕」以資區別，功能不變）；結果畫面「💬 攻略留言」按鈕改為「📋 攻略留言板」，點擊開啟留言板（原本的內嵌輸入盒移除，改由留言板內輸入列負責）。
- 彈幕佇列 `loadQueue()` 改熱門排序；空關引導句更新為「還沒有攻略，搶頭香！在留言板或下方輸入你的攻略」。
- `sync()` 換關時自動關閉留言板；匯出 `window.TWDANMAKU.openBoard` 供驗證用。
- `node --check` 通過；全 repo 無 `dk-resultbox`／`dk-row` 殘留引用。

### Step 4：整合 css／index.html／main.js（完成）
- `css/style.css`：移除 `.dk-resultbox` 系列（原結果畫面輸入盒樣式），新增留言板樣式（overlay z-index 60、關閉鈕、清單 max-height 38vh、留言卡、👍 按鈕與已讚亮綠、輸入列、手機 720px 清單 32vh）。
- `index.html`：版本號 1.9.15→1.9.16（標題＋2 badge＋2 css＋4 js 共 9 處）；ov-help 玩法說明新增「📋 龍塔攻略留言」一行（每關 1 則、3 讚、再點一次收回、本地測試版）。
- `js/main.js`：工程模式「清存檔」掃除清單加入 `dinodoku-twlikes-*`／`dinodoku-twposted-*`（並保留掃除舊鍵 dinodoku-twlast），confirm 文案「攻略彈幕」→「攻略留言」；`node --check` 通過。

### Step 5：本機驗證（完成，http://localhost:8765 + 自動化瀏覽器）
- 資產 HTTP 狀態：index.html／js/tower_comments.js／js/main.js／css/style.css 全 200。
- 進入龍塔第 1 關（工程模式跳層）：
  - controls 出現「💬 彈幕」與「📋 留言板」兩鈕；一般（非龍塔）模式兩鈕與上下彈帶全隱藏、`TWDANMAKU.openBoard()` 無作用。
  - 預種 3 則留言（2 則帶 id/lk、1 則舊格式）：留言板開啟後清單依 讚多→新 排序（5→2→0），舊格式留言自動補上 id 與 lk=0 並回寫（遷移成功）；時間顯示「今天 HH:MM」與「M/D」正確。
  - 按讚：三則依序 +1（5→6、2→3、0→1）、按鈕亮綠、子標題「讚已用 3/3」、`dinodoku-twlikes-1` 存 3 筆。
  - 第 4 個讚被擋：伴伴提示「這關的 3 個讚都用完了」、計數與額度不變。
  - 收回讚：計數減回（1→0）、額度釋放（3→2），收回後可再把讚按到別則（2→3）。
  - 從留言板輸入列送出攻略：入庫（帶 id、lk:0、30 字內）、輸入列轉為「✓ 這關你已經留過攻略」、`dinodoku-twposted-1` 寫入、單日計數 +1、暱稱自動帶入記憶值。
  - 同關第二次留言（底部彈幕輸入列）：被擋「這關你已經留過攻略了（每關限 1 則）」，未入庫。
  - 防灌水／安全：黑名單詞（垃圾遊戲）與 URL 留言皆被擋；`<img onerror>` 標籤以純文字渲染（textContent，無 XSS）、30 字截斷生效。
- 過關結果畫面：出現「📋 攻略留言板」鈕（一般模式隱藏）；點擊後留言板以 z-index 60 疊在結果視窗之上，讚數／已留言狀態正確，✕ 或點擊背景可關閉返回結果畫面。
- 每關獨立：第 2 關留言板為空狀態（搶頭香文案）、讚額度 0/3、可留言；跳新關時 `sync()` 自動關閉留言板。
- 跨重載持久：重整頁面後重進第 1 關，已留言提示與 3/3 讚數維持。
- 彈幕回歸：💬 開關 off/on 正常（隱藏雙帶／存 "0"、"1"）；重播取樣 transform 1218px → 96.9px（右→左飛行正常）；空關引導句為新文案。
- 工程模式「清存檔」：confirm 覆寫後點擊，twcomments-*／twlikes-*／twposted-*／twname／twday／danmaku-on 全數清空。
- 驗證期間發現並修復 1 個 bug：`.dk-brow{display:flex}` 覆蓋 `hidden` 屬性（作者樣式優先於 UA 樣式），已留言時輸入列仍顯示——補 `.dk-brow[hidden],.dk-bposted[hidden]{display:none}` 修正，複驉 display:none 生效。
- 另一手機最佳化：controls 兩顆攻略按鈕文字改包 span，≤360px 螢幕只顯示圖示，避免 6 顆按鈕在極窄螢幕擠壓。
- console：本頁載入零錯誤（清單中僅其他埠舊 session 殘留訊息）。
- 已知環境限制：自動化瀏覽器 rAF 約 1.3fps，彈幕飄動無法目視，改以 transform 數值取樣驗證位移方向正確；真實瀏覽器不受影響（同前次彈幕驗證結論）。

## 最終狀態
- 狀態：✅ 完成（本地模擬版；「給其他人按讚」的跨玩家共享與「不可按自己的留言」限制，待雲端版（Supabase）上線後接續）
- 檔案變更：js/tower_comments.js（留言板＋讚＋每關一則）、css/style.css（留言板樣式、移除舊結果盒樣式、[hidden] 修正、極窄螢幕按鈕）、index.html（版本 1.9.16、ov-help 新增說明）、js/main.js（清存檔掃除新鍵與文案）、worklogs/worklog_tower-strategy-board.md（本日誌，後封存至 history/）。
- 另依工作日誌慣例，將已完成的前案 worklog_tower-danmaku-local.md 一併移至 worklogs/history/。
- 驗證：node --check 通過；http.server 200；自動化瀏覽器全項通過（見 Step 5）。
- 提交：未提交（使用者未指示 commit/push；工作樹另有多項先前任務之未提交變更，提交範圍待使用者決定）。


