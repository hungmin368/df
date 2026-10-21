# 4×4 示範教學改為點擊推進

- 日期：2026-10-21
- Task ID: tut4-tap-advance

## 需求

4×4 示範教學（`startDemo`）原本每個主步驟固定 sleep 2 秒自動前進；改為由玩家點擊畫面才進行下一步。

## 步驟記錄

### 1. 定位教學引擎

- 找到 `js/main.js` 教學引擎（`startDemo` 4×4 示範／`startGuided` 5×5 引導）。
- 確認 4×4 = `G.tutorial==='demo'`（`js/main.js:1051` 設定），每次進入 4×4 且未完成教學時執行 `startDemo()`。
- 確認示範期間 `G.state==='demo'`，盤面格與按鈕點擊均自動失效（`onCell`/`btn-ball` 都要求 `state==='marking'`），因此「點畫面推進」不會誤觸遊戲操作。
- 待改造點：`startDemo` 內 15 處 `await sleep(D)`（D=2000）為主步驟間隔。

### 2. 實作點擊推進

- `js/main.js`（教學引擎區）：
  - 新增 `waitTap()`：等待玩家點一下畫面；等待時顯示 `#tut-tap` 提示，等到後隱藏。
  - `document` 掛 `pointerdown` 捕獲監聽：僅 `G.tutorial==='demo' && G.state==='demo'` 時生效，點擊解鎖等待者；動畫播放中先點擊會緩衝一次（`tutTapPending`），下一步立即生效。
  - `tutHide()` 補上隱藏 `#tut-tap`，避免跳過教學後提示殘留。
  - `startDemo` 內全部 15 處 `await sleep(D)` 改為 `await waitTap()`；開頭重置點擊緩衝狀態；移除不再使用的 `D` 常數。
  - 步驟內的短間隔維持自動：開場 600ms、秘訣標記間的 900ms、`demoEliminate` 連鎖 ✕ 的 gap（示範動畫節奏）。
- `index.html`：`#dlg-tut` 下方新增 `<div id="tut-tap">👆 點一下畫面繼續</div>`。
- `css/style.css`：`#tut-tap` 預設隱藏，`.show` 時顯示並以透明度脈動提示。

### 3. 本機驗證

- `node --check js/main.js` 語法通過。
- `python -m http.server 8321` 起服務，`index.html`／`js/main.js`／`css/style.css` 皆 HTTP 200。
- 瀏覽器實測（清存檔→跳過序章→進 4×4）：
  - 歡迎訊息停留超過 2.5 秒不自動前進，「點一下畫面繼續」提示有顯示。
  - 逐次點擊畫面推進：區塊×4 → 橫列 → 直欄 → 絕不互相接觸 → 秘訣一 → 秘訣二 → 勇敢先試 → 捕捉器 → 捕獲成功 → 連鎖排除 → 第 2～4 隻丟球，一路到結算畫面；捕捉器 ×7→×3 遞減正確。
  - 動畫中先點擊會被記住、下一步立即推進（緩衝生效）。
  - 示範中途點「跳過教學 ▶▶」：提示隱藏、`tut4` 標記完成、無殘留狀態。
  - 完成教學後再進 4×4：正常 `marking` 模式，不再進示範。
  - 5×5 引導教學回歸測試：`開始！` 按鈕、指定格點擊打 ✕ 正常。
- 主控台無遊戲程式錯誤（僅測試腳本自身的兩個 eval 錯誤）。

## 最終狀態

- 完成並驗證通過，交付 commit：`1843d90`（Advance the 4x4 demo tutorial only when the player taps the screen）。
