# worklog_map-remove-tints

- 任務：探索地圖的區域淺色色塊（辨識用）全部拿掉，可進入區域靠名字顏色辨識即可
- 日期：2026-10-14
- Task ID：map-remove-tints

## 步驟紀錄

1. 定位色塊來源：`js/main.js` `renderMap()` 以 `fill="'+geo.col+'"` 替每個區塊 path 上色（龍塔地標用 `tg.col`）；`css/style.css` 以 `.mreg.new/.clear/.lock path` 的 `fill-opacity` 與 `mregPulse`／`towerPulse` 動畫控制深淺。點擊互動為 svg 層 pointerup：先 `closest('g.mreg')`（依賴 path hit area），落空時以 `regionAt()` 射線法兜底，故 path 需保留但改為透明。`geo.col` 僅 `renderMap()` 兩處使用，可一併移除。

## 最終狀態

（待驗證後填寫）
