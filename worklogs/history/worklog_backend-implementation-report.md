# worklog_backend-implementation-report

- 任務：為「分數驗證、內購等關鍵邏輯移到後端」規劃後端實作方案，先產出自包含 HTML 報告（不直接實作後端）
- 日期：2026-10-13
- Task ID：backend-implementation-report

## 步驟紀錄

1. 需求確認：使用者指示關鍵邏輯（分數驗證、內購）要放後端；本任務只先交付「後端實作 HTML 報告」，不動遊戲程式碼。
2. 現況調研（僅讀取，未改檔）：
   - 全站零網路：grep `fetch(|XMLHttpRequest|sendBeacon|WebSocket|import(|axios`（js/*.js）零匹配 → 目前為純離線靜態 App。
   - 分數機制：過關分數＝剩餘秒數（js/main.js:2381 `Math.max(0, Math.floor(TIMER.left))`）；沙漏總量＝N×30 秒（js/main.js:1359）、每捕獲 +30 秒且上限回初始總量（js/main.js:1375-1377）；累積入 `LV[n].total`；個人總分＝`lvTotal()` 加總（js/main.js:303）；龍塔不計時不計分（js/main.js:1358、2381）；4×4/5×5 為練習盤不計分（js/main.js:2382）。
   - 存檔與經濟：全部 localStorage `dinodoku-*`（js/main.js:945 清單、953 全掃）；ECON=種子/獎勵券/藥水（js/main.js:323）；過關 +1 券（js/main.js:2374）；寶箱獎勵表（js/main.js:2140-2142）；獎勵小遊戲 6 種耗券（index.html:187-202）。
   - 盤面生成：客戶端即時生成、`Math.random` 無種子（js/main.js:102、120、235）；`generatePuzzle` 重試至唯一解（js/main.js:178-255）；預生成池 POOL_DATA 尺寸 10-13（js/main.js:257-283）；龍塔為 tower.js 預生成 2000 關；生成器為純 JS（無 DOM 依賴）→ 可移植至後端。
   - 作弊面：工程模式按鈕「立即過關／種子+100／無限種子」等（index.html:215-251、js/main.js:892-946）；localStorage 可直接編輯。
   - 內購現況：無。上架報告建議首發免費、若要內購再議（appstore_publish_report.html:176）。攻略彈幕目前為本地模擬版、尚未接後端（js/tower_comments.js:1），先前調查已選 Supabase 為首選（dragon_tower_comments_report.html:136-203）。
3. 外部查證（Web，2026-10-13）：
   - Google Play Billing Library 最新 9.1.0（2026-06-18 發布）；2026-08-31 起新上架/更新必須使用 v8 以上（可申請延至 2026-11-01）。來源：developer.android.com release-notes、deprecation-faq。
   - RTDN 一次性商品通知：`ONE_TIME_PRODUCT_PURCHASED`(1)／`ONE_TIME_PRODUCT_CANCELED`(2)＋`VoidedPurchaseNotification`；Pub/Sub 訊息含 `purchaseToken`、`sku`；收到通知後仍須以 purchaseToken 呼叫 Play Developer API 取完整狀態。來源：developer.android.com rtdn-reference。
   - Apple：App Store Server API＋App Store Server Notifications V2、StoreKit 2 交易 JWS 於伺服器端驗證。來源：developer.apple.com appstoreserverapi、validating-receipts-with-the-app-store。
4. 產出報告：`backend_implementation_report.html`（自包含、繁中、沿用既有報告暖色系視覺）。章節：零/結論摘要、一/現況盤點（事實表＋作弊面＋讓驗證可行的兩個特性）、二/設計目標與架構（含身分模型、技術選型）、三/分數驗證（不變量 V1-V9、L1-L3 三層防護能力矩陣、開局/結算流程、事件格式、離線策略、前端改造清單）、四/內購（商品規劃、iOS/Android 整合現況含查證版本、購買發放流程、機密清單、退款政策）、五/API 總表、六/資料庫 DDL（含 RLS 原則）、七/安全與營運、八/分階段路線圖與驗收條件、九/風險對策、十/待你決定事項、附錄 A 程式碼事實索引、附錄 B 名詞對照。修正 1 處錯字標籤（`<code:1260-1264` → `<code>1260-1264`）。
5. 驗證：`python -m http.server 8790` → `curl` 報告與 index.html 均 HTTP 200；瀏覽器實開報告：標題/卡片/表格（15 個）/程式碼區塊（3 個）/流程節點（13 個）渲染正常（截圖確認首頁、第六章 DDL、3.2 防護表）；console 無本頁錯誤（僅殘留他埠 8765 舊 session 訊息）；程式檢查：無破損標籤（`<code:` 殘留＝false）、無未跳脫 `&`（regex 檢查 null）、DDL 的 `&gt;=` 正確顯示為 `>=`、頁尾完整。
6. （2026-10-14）使用者連續三問，先以對話回答並查證現況事實：
   - Q1「7×7 以下離線免費、8×8 以上付費做得到嗎」→ 技術上可做（前端尺寸門檻），但盤面由客戶端 `newBoard()`（js/main.js:1005）與 `REGION_META`（js/main.js:393-396）生成，改 HTML 即可本地繞過；建議定位為誠實解鎖而非防破解牆。
   - Q2「伺服器驗證收據能否防改 HTML 繞過」→ 誠實回答：不能防本地解鎖；伺服器只守得住收據真偽、雲端分數/錢包、UGC。
   - Q3「離線可玩＋開留言才提醒連線可行嗎、如何收費」→ 可行；留言免費、錢收在「完整版解鎖」一次買斷（非消耗型），Web 版免費試玩不接內購。
7. 依 Q3 承諾把具體規格補進報告（新增第十一章「離線核心＋連線留言：混合模式規格」，8 個小節）：11.1 功能分層與網路需求表；11.2 連線偵測與提醒 UI 流程（7 步 flow：先秒開快取→背景探測→靜默同步→非阻斷提示卡→離線存草稿不丟字→online 事件自動重試→離線永不阻擋單機功能之鐵律）；11.3 離線快取規格（`dinodoku-twcache-*`／`-meta-`／`twdraft-`、每關 20 則、72 小時、LRU 30 關、與既有本地鍵遷移）；11.4 留言後端 DDL（`tower_comments`／`comment_likes`／`comment_reports`／`banned_words`／`comment_quota`＋`players.muted`，含每玩家每關 1 則的部分唯一索引）＋5 支 API＋RLS 說明；11.5 UGC 合規清單 C1–C10（含現況差距欄）；11.6 收費模型（免費單機核心／一次買斷完整版／Web 免費試玩／不做廣告訂閱抽獎箱）；11.7 防繞過界線三方案比較（A 全離線＝採此、B 大盤面走伺服器＝不建議、C 種子包混合＝再議）；11.8 P0–P3 工時與驗收條件＋動工前待你決定 5 項。
8. 同步更新報告其他章節：hero meta 加追加日期；零章摘要加第 5 張卡片（第十一章導讀）；附錄 A 事實索引加 5 列（留言上限 js/tower_comments.js:20、339、346-347、298、357；敏感詞與網址過濾 :22-23；本地資料鍵 :12-19；客戶端生成盤面 js/main.js:1005）；附錄 B 加 3 名詞（非消耗型商品、UGC、entitlement）；頁尾日期加追加說明。
9. 自檢修正 3 處：info 區塊結尾多餘 `</p>`；簡體「单机」→「單機」；「价值主张」→「價值主張」。
10. 驗證（2026-10-14）：`python -m http.server 8791` → curl 報告/index/js/tower_comments.js 均 HTTP 200；結構檢查：h2 14 個（含十一）、11.1–11.8 齊全、table 22/22、pre 4/4、code 252/252、div 124/124、`<p>` 9/9、無 `<code:` 殘留、無未跳脫 `&`、無簡體殘留（僅共用字「值」）；瀏覽器實開：第十一章 7 表＋1 DDL＋1 flow＋8 提示卡渲染正常（截圖確認 11.1 表與 11.4 DDL，`&lt;=`／`&gt;=`／`&lt;&gt;` 正確顯示為 `<=`／`>=`／`<>`）、零章 5 張卡片、頁尾含追加說明；console 無本頁（8791）錯誤（僅他埠 8765/8977/8991/8331/8332/8130 歷史訊息）。

## 最終狀態

- 完成：後端實作規劃報告 `backend_implementation_report.html`（分數驗證 L1-L3 設計＋內購驗證流程＋API/Schema/路線圖＋2026-10-14 追加第十一章離線核心＋連線留言混合模式規格），依指示「不直接實作」——未動任何遊戲程式碼。
- 驗證：HTTP 200（報告與 index 皆可存取）；瀏覽器實開渲染正常、無本頁 console 錯誤；HTML 完整性檢查通過（2026-10-13 與 2026-10-14 兩輪）。
- 已改檔：backend_implementation_report.html（新增＋追加第十一章）、worklogs/history/worklog_backend-implementation-report.md（新增，後於本次一併提交）。
- 待你決定：免費/付費尺寸切線、龍塔免費關數、先發後審或先審後發、是否開 Supabase 專案、完整版定價；P0（純前端連線偵測與提示 UI）可立即開工。
- Commit：（hash 待回填）。
