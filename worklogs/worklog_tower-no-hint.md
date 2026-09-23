# Worklog：龍塔闖關不提供提示

- 日期：2026-09-23
- 任務 ID：tower-no-hint
- 需求：龍塔闖關遊戲不給提示選項。

## 執行步驟記錄

### 1. 調査提示功能的所有進入點（完成）
- `js/main.js` 中「提示」有兩條路徑：
  1. HUD 的 `#btn-hint`（`js/main.js:2303`）：花 1 顆星願種子，呼叫 `freeHint()` 挑一隻未捕獲恐龍，再 `showHintAt(i)` 在該格顯示 🌿；按鈕狀態由 `updateHintBtn()`（`js/main.js:2263`）統一控制（`newRun`→`finishBoard`、`econRender` 都會呼叫）。
  2. 夥伴技能「心靈感應」`hint1`（`SKILLS` 定義為「免費提示一隻恐龍」，`js/main.js:760` 於 `triggerBuddySkill()` 內）：同樣呼叫 `freeHint()`＋`showHintAt()`。
- 其他技能（`intel` 情報、`reveal` 神視、`time15/time30`、`sweep*`、`luck*`）不是「提示」功能，本次不動。
- 教學關（`G.tutorial`）本來就只把按鈕設為 disabled，本次不影響。
- `TOWER.level` 於 `towerStart()` 設定後才 `newRun()`，因此在 `updateHintBtn()` 內判斷 `TOWER.level` 可正確分辨龍塔與地圖關卡。

### 2. 實作（完成，`node --check` 通過）
- `updateHintBtn()`：`if(TOWER.level){ b.style.display='none'; b.disabled=true; return; }`，其餘維持原邏輯並還原 `b.style.display=''`（龍塔不顯示「提示」按鈕，地圖關卡照舊）。
- `$('btn-hint').onclick`：加入 `|| TOWER.level` 守衛，即使程式化觸發也不會給提示（雙重保險）。
- `triggerBuddySkill()` 的 `hint1` 分支：龍塔中改為 `doBuddyChat('龍塔的考驗要靠自己～在這裡我不能給你提示！'); return;`，不產生提示、不進 `done` 流程。
- `index.html`：版號 1.9.8→1.9.9（`<title>`、2 個 `.ver-badge`、`#foot`、5 個 `?v=`）。CSS 無需修改（以行內 `display` 隱藏）。

### 3. 瀏覽器實測（完成）
本機 `python -m http.server 8126`（`index.html`、`css/style.css`、`js/main.js`、`js/tower.js`、`js/data.js` 皆 HTTP 200；星願種子設為 5）。
- 一般關卡（6×6）：`#btn-hint` 可見、可按，點擊後種子 5→4 並出現 🌿 提示 → 提示功能正常。
- 龍塔關卡（塔 1 層）：`#btn-hint` `display:none`、`offsetParent` 為 null（實際不可見），程式化 `click()` 無效（種子 4→4、無 🌿）；HUD 只剩 清除／重來／放棄／捕捉器（截圖確認，header 顯示 v1.9.9）。
- 夥伴技能「心靈感應」在龍塔：顯示「伴伴：龍塔的考驗要靠自己～在這裡我不能給你提示！」，無 🌿 產生；回到地圖關卡後同一技能恢復正常（顯示「我感應到了！這裡有一隻！」並出現 🌿）。
- 回到地圖關卡：`#btn-hint` 恢復可見（`display=''`、非 disabled）。
- 教學關（4×4 demo）：按鈕仍可見但 disabled、點擊無效（行為與改動前一致）。
- 手機寬度（iframe 390×800／360×640）：390×800 龍塔＝`hintVisible=false`、HUD `[btn-clear,btn-restart,btn-giveup,btn-ball]`、列無溢出；360×640 地圖＝`hintVisible=true`、五顆按鈕皆在視窗內（`#controls` 內部文字擠壓為改動前既有現象，與本次無關）。
- console／`error` 收集器：上述完整流程（地圖提示→龍塔點擊與技能→回地圖）收集結果為空陣列。

### 4. 提交與線上驗證（完成）
- 僅提交 `index.html`、`js/main.js`、本工作日志；工作區另有其他工作階段的未追蹤檔案 `worklogs/worklog_investigate-6x6-generation.md`，不納入本次提交。commit：`0674b7e`，已推送 `origin/main`。
- GitHub Pages 部署後檢查（https://hungmin368.github.io/df/）：頁尾與 `.ver-badge`＝v1.9.9；`js/main.js` 含「龍塔挑戰不提供提示」「龍塔不給提示」「龍塔的考驗要靠自己」等字串。
- 以瀏覽器實測線上版本（種子 5）：龍塔關卡 `#btn-hint` 不可見、程式化點擊無效（種子 5→5）、夥伴「心靈感應」顯示拒絕訊息且無 🌿；回到地圖關卡提示恢復可用（種子 5→4 並出現 🌿）；整段流程 `error` 收集為空。

## 最終狀態
- 交付：龍塔關卡不顯示且無法使用「提示」（含夥伴「心靈感應」技能提示），地圖關卡提示功能不變；版號 1.9.9。
- commit：`0674b7e`（Withhold hints during Dragon Tower challenges）
