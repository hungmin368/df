# Worklog：遊戲 logo 去背（背景全透）

- 日期：2026-10-15
- 任務 ID：logo-background-removal
- 需求：將現行 logo 的白底去除、背景全透明。來源 `assets/game_logo_1.jpg`（1264×843 白底），目標覆蓋 `assets/dinos_2/game_logo.png`（路徑不變，引用零修改）。

## 步驟記錄

1. 去背完成（方法：連通域洪水填充 + 羽化 + 去白邊）：
   - 候選背景＝三通道皆 >235 的像素（54.36%）；以 scipy.ndimage.label 做連通域分析，僅將「與圖片邊界相連」者（54.28%）設為透明——主體內部淺色細節（眼白/高光等 890px、0.084%）自動保留，不受誤傷。
   - 邊緣羽化 0.7px；半透邊帶做白底去污染（依 alpha 反推主體色），殘白僅 1.5%。
   - 洋紅底合成目視：邊緣乾淨、無白邊、木牌/龍/蛋殼/葉子完整。
2. 覆蓋與數據驗證（通過）：
   - `tmp_logo/logo_nobg.png` 覆蓋 `assets/dinos_2/game_logo.png`；`file` 確認 `RGBA 1264x843`。
   - 與舊透明版（git `0ac5551~1`）的 alpha 幾何 IoU=0.9954（剪影幾乎完全一致）；新透明區 54.28% vs 舊 54.53%。
   - 角落/四邊中點 alpha=0 全透；主體採樣點 alpha=255 不透明。
3. 瀏覽器與 HTTP 驗證（全部通過）：
   - HTTP：`/`、`/assets/dinos_2/game_logo.png`（`200 image/png`）、`/css/style.css`、`/js/main.js`、`/js/data.js` 全部 200。
   - 主選單：`#menu-logo img` natural 1264×843、渲染 186×73.38，與 CSS 盒子一致；白卡片感消失，drop-shadow 回到貼合主體輪廓。
   - 開場 splash：重建 splash 截圖確認 logo 直接浮於漸層背景上（不再為白卡片）；實際 reload 驗證 fly 動畫後正常進入主選單。
   - 控制台：本頁 JS 錯誤 0。
   - 驗證後已關閉 http server。
4. （進行中）worklog、commit、push、歸檔。

## 最終狀態

- 狀態：完成
- Commit：（pending）
