# Worklog：龍塔直接進入＋地圖進度門檻

- 日期：2026-09-23
- 任務 ID：tower-direct-entry
- 需求：
  1. 點龍塔地標直接進入下一個可挑戰關卡，不彈出尺寸/樓層選擇視窗。
  2. 不能跳關卡：從第 1 層逐層挑戰上去。
  3. 地圖 6×6 過關才開放龍塔。
  4. 地圖 N×N 過關後，龍塔內才解鎖 N×N 區段，以此類推。

## 執行步驟記錄

### 1. 調查現有實作（完成）
- 既有龍塔（commit fa6bd07）：點地標開 ov-tower 彈窗（8 尺寸分頁＋關卡格），towerStart(L) 只擋 L>max+1（可重玩舊層）。
- 地圖進度：PROG.max（isUnlocked/progUnlock，winRound 內 progUnlock(G.N+1)）；有 LV 戰績遷移邏輯。
- 發現問題：舊版龍塔過關也會執行 progUnlock（塔內 6×6 過關會解鎖地圖 7×7），地圖進度會被塔汙染。

### 2. 實作（完成，node --check 通過）
- js/main.js：
  - PROG 新增 clear{}（地圖尺寸→1，只由地圖過關寫入）；舊存檔依 LV 戰績遷移推斷 clear（有戰績＝該尺寸已通關）。
  - 新增 towerGate()：地圖已通關的最大尺寸（6~13），為龍塔開放門檻。
  - winRound：progUnlock 與 PROG.clear 只在非塔過關時執行（龍塔不再推進地圖進度）；lvRec 計分維持不變。
  - renderMap 龍塔地標：gate<6 顯示鎖定樣式（.mtower.lock）與「🔒 地圖 6×6 過關後開放」；開放後依狀態顯示已通關層數／下一區段待地圖通過。
  - 刪除 ov-tower 彈窗整套（openTower/renderTowerTabs/renderTowerGrid/towerTab/tower-close），改為 towerEnter()：gate<6 拒絕＋夥伴提示；否則直接 towerStart(max+1) 進入下一層；next 屬性尺寸大於 gate 時拒絕＋提示。
  - towerStart 保留 L>max+1 拒絕（不可跳關）。
  - res-next（塔）：過關往上一層前先檢查 towerGate，被封印則回主選單＋夥伴提示；全通關另給賀詞。
  - res-menu（塔）：不再回選關彈窗，改回主選單並重置 TOWER.level。
  - 地圖點擊/鍵盤（Enter/Space）龍塔地標統一走 towerEnter()。
- index.html：移除 ov-tower overlay 區塊。
- css/style.css：移除 #tower-tabs/#tower-grid/.tlv*/towerNext（.dtab 與圖鑑共用，保留）；.mtower.lock 停用脈動動畫。
- 驗證：node --check js/main.js 通過。

### 3. 併同龍塔第二版規格重排驗證與提交（完成）
- 本任務變更（PROG.clear／towerGate／towerEnter／ov-tower 移除）與「龍塔尺寸盤數更正（第二版規格，總計 2000）」在同一次提交一併驗證，詳見 `worklog_dragon-tower.md` 第 6、7 節。
- 本機 HTTP 全資產 200；瀏覽器實測：封印（clear={} 點地標不進關卡）→ clear[6]=1 開塔進第 1 層 → 完整實玩過關與 res-next 往上一層 → 第 10→11、600→601、1200→1201 的 gate 封印與解封 → 第 2000 層全塔完成台詞 → 地圖區域維持即時生成，全數通過。

## 最終狀態
- 交付：js/main.js（地圖進度 clear{}／towerGate／towerEnter／winRound 不汙染地圖進度／res-next、res-menu 調整）、index.html（移除 ov-tower）、css/style.css（.mtower.lock）、本工作日志。
- 驗證：node --check 通過；合併 dragon-tower 第二版規格於瀏覽器逐項實測通過（見上節）。
- Commit：本任務變更與 dragon-tower 第二版規格重排同一提交 `1cd74db`（Renumber the Dragon Tower and enter it directly from the map）。
