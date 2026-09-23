# dinodoku_claw_v1.6.1 — 多檔案專案

由單檔 `dinodoku_claw_v1.6.0.html` 自動拆分而成（內容與行為不變，僅把內嵌資產外置）。

## 目錄結構

```
index.html          頁面結構（含 <link> 與 <script> 引用）
css/
  fonts.css         內嵌字型 @font-face（指向 assets/fonts/）
  style.css         主樣式（游標圖指向 assets/cursor.png）
js/
  data.js           恐龍資料 POKEMON / LEGENDS（139 隻，圖片路徑指向 assets/dinos/）
  main.js           遊戲主程式（其餘全部邏輯）
assets/
  fonts/*.woff2     2 個內嵌字型（Huninn / Iansui）
  dinos/*.webp      139 張恐龍圖（以 id 命名）
  cursor.png        捕捉模式游標
```

## 開啟方式

直接以瀏覽器開啟 `index.html`（file:// 即可）。因是本地相對路徑，
若瀏覽器限制，可用任意靜態伺服器：`python3 -m http.server` 後開 `http://localhost:8000/`。

## 本版變更（相對 v1.6.0_web）

- **移除「24h 遊戲密碼鎖」**：開檔直接進主選單，不再需要密碼 6688；
  一併移除鎖定畫面（`#ov-lock`）、其樣式、相關程式（`evalLock`/`lockTry`/…）與開發面板的「解 24h 鎖」按鈕。

## 對照

- 原單檔：`../dinodoku_claw_v1.6.0.html`
- 差別：字型／圖片／游標改為外部檔案；CSS／JS 分檔；其餘不變。
- 拆分工具：`../_split_multifile.py`
