# worklog_map-gray-box

- 任務：移除探索地圖上紅框圈出的浮動灰框（橫跨整個地圖寬度的半透明圓角灰框，蓋在「碎岩丘陵 7×7」一帶）
- 日期：2026-10-14
- Task ID：map-gray-box

## 步驟紀錄

1. 復現使用者狀態：`localStorage dinodoku-prog={max:7,clear:{4,5,6}}`，本機 `python -m http.server 8321` + 瀏覽器開 `index.html`，同位置確實出現同一個全寬灰框。
2. 逐項排除嫌疑：區塊 fill（全部 `fill-opacity:0` 仍在）、整個 SVG `visibility:hidden` 仍在、`.map-inner` 背景換成純色 `#89b8d8` 仍在 → 灰框不是地圖圖稿（`assets/map.png` 該區域像素也確認乾淨）、不是 SVG 色塊或文字，也不是任何可 hit-test 到的 DOM 元素。
3. 刪除法定位：清空 `#map-nodes`（灰框消失）→ 還原後改刪 `#map::after`（灰框消失）→ 還原 `#map::after` 並給它上紅色半透明背景，確認偽元素實際盒模型：它高度等於 `#map` clientHeight、位於捲動內容頂端並**跟著內容一起捲動**，露出可視區的下緣（3px 淺色內描邊 + 52px 深色內陰影）就是在地圖中段看到的「灰框」。
4. 根因：`#map::after`（`position:absolute; inset:0`）是絕對定位在捲動容器 `#map` 內，會跟內容捲動；設計初衷是地圖外框暗角，但下緣永遠停在內容中段（使用者視窗高度決定），渲染成浮動灰框。
5. 修法：把整條規則從 `#map::after` 搬到不捲動的外層 `.map-wrap::after`（`left:0; right:0; top:15px; bottom:0`，`top:15px` 對齊 `.map-wrap` 的 `padding-top` 避開探索地圖緞帶），光影、圓角、數值不變，永遠貼在可視框邊緣。
6. 本機驗證：重新載入（清掉所有注入測試樣式），三個捲動位置截圖——`scrollTop=0`（龍塔／雲海神殿）、`scrollTop=194`（renderMap 自動置中的碎岩丘陵，即使用者截圖位置）、`scrollTop=356`（地圖底部起源地）——浮動灰框皆消失，暗角與 3px 淺色框貼在可視框邊緣，區塊色塊、標籤、灰階鎖定、呼吸動畫正常。`curl` 確認 `index.html`、`css/style.css`、`js/main.js`、`assets/map.png` 皆 200，且伺服器回傳的 CSS 已含新規則。
7. 清理調查用的暫存檔：`_maptest.html`、`_crop_user.png`、`_crop_bl.png`、`_crop_mid.png`、`_mappng_band.png`、`_mappng_band2.png`。

## 最終狀態

- 狀態：浮動灰框已移除並在三個捲動位置驗證；地圖外框暗角視覺保留，改為固定貼齊可視框。
- 產出：`css/style.css`、本工作日志。
- commit hash：（本 commit）
