# Worklog：以「恐龍快找」新 logo 覆蓋舊 logo（保留原路徑）

- 日期：2026-10-15
- 任務 ID：replace-logo-dinodoku
- 需求：比較 `assets/dinos_2/game_logo.png`（相揪尋龍版）與 `assets/game_logo_1.jpg`（恐龍快找版）顯示尺寸是否一致；一致則以 `game_logo_1.jpg` 內容覆蓋 `assets/dinos_2/game_logo.png`（路徑不變，引用零修改）。

## 步驟記錄

1. 尺寸比較與寫死尺寸檢查（完成）：
   - 舊圖 `game_logo.png`：1536×1024 RGBA，長寬比 1.500000；54.53% 像素全透明（logo 主體外圍透明，透出 body 淺色漸層背景）。
   - 新圖 `game_logo_1.jpg`：1264×843 RGB（白底），長寬比 1.499407；54.04% 接近純白，分佈與舊圖透明區幾何一致。
   - 長寬比差異 0.0395%（顯示尺寸一致，差異不可辨）；兩圖構圖相同，新圖＝透明處填白＋標題改「恐龍快找」。
   - 寫死尺寸檢查：`js/main.js:3143` fly() 以 `naturalWidth/naturalHeight` 動態讀取；CSS `#menu-logo`（186×73.38px、手機 150×59.20px）與 `#splash img` 高度皆為固定值；全 repo 無 1536/1024 硬編碼（僅歷史報告 HTML 提及）。引用路徑不變即零程式修改。
   - 結論：顯示尺寸一致，可覆蓋。已知差異：新圖無 alpha，drop-shadow（`#menu-logo img`、`#splash img` 的 filter）將改以整個矩形外緣計算，而非舊圖的 logo 主體輪廓；白底（#FFF）與 body 底色（#fffdf9→#f4ecdb）幾乎無差。留待瀏覽器截圖驗證確認可接受。
2. 覆蓋完成：以 PIL 將 `assets/game_logo_1.jpg`（1264×843 RGB）轉存為真實 PNG 覆蓋 `assets/dinos_2/game_logo.png`（953KB）。`file` 確認輸出為 `PNG image data, 1264 x 843, 8-bit/color RGB`。路徑不變，`index.html`（splash 第16行、menu-logo 第71行）與 `build_single_file.mjs` 引用全部繼續有效，零程式修改。
3. 本機驗證（全部通過）：
   - HTTP：`python -m http.server 8931` 起服務，`/`、`/index.html`、`/assets/dinos_2/game_logo.png`（`200 image/png`）、`/css/style.css`、`/js/main.js`、`/js/data.js` 全部 200。
   - 瀏覽器（127.0.0.1:8931）：主選單 `#menu-logo img` 實測 natural 1264×843、渲染 186×73.38 @ (357,19)——與 CSS 盒子完全一致，顯示尺寸無變化；新「恐龍快找」logo 正常顯示。
   - 開場 splash：重建 splash 元素截圖確認新 logo 於開場滿版顯示正常（截圖時恰逢淡入動畫首幀，複測 opacity=1 後正常）；實際重新載入兩次，splash 皆於 fly 動畫後正常收尾進入主選單，無卡 splash。
   - 控制台：本頁 JS 錯誤 0（僅有一筆來自舊 `localhost:8123` origin 的歷史錯誤，與本次無關）。
   - 已知視覺差異：新圖為白底（JPG 無 alpha），在開場漸層背景上呈白卡片感；主選單因容器底色接近白色，目視無差異。若要完全貼合舊效果需去背素材（非本次範圍）。
   - 驗證後已關閉 http server。
4. （進行中）worklog 歸檔、commit、push。

## 最終狀態

- 狀態：進行中
