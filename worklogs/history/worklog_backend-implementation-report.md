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

## 最終狀態

- 完成：後端實作規劃報告 `backend_implementation_report.html`（分數驗證 L1-L3 設計＋內購驗證流程＋API/Schema/路線圖），依指示「不直接實作」——未動任何遊戲程式碼。
- 驗證：HTTP 200（報告與 index 皆可存取）；瀏覽器實開渲染正常、無本頁 console 錯誤；HTML 完整性檢查通過。
- 已改檔：backend_implementation_report.html（新增）、worklogs/worklog_backend-implementation-report.md（新增，後封存至 history/）。
- Commit：未提交（本任務僅交付報告；工作樹另有大量既有未提交／已暫存變更，提交範圍待使用者決定）。
