# 更新日誌 CHANGELOG

本檔自 **v1.9.17** 起建立，之後每次出貨（含上架平台包）皆需同步新增一筆，並與 `index.html` 的 `ver-badge` 版本號一致。
v1.9.17 之前的完整歷史請見 git commit log。

格式：`- [版本] - 日期：摘要（細項）`

---

## [Unreleased] - 2026-10-22

- 專案目錄重構：遊戲本體集中到 `game_db/`（維持原有子目錄與相對連結），任務產物集中到 `working_db/`（reports、generated_assets、store、builds、docs、archive）。
- 根目錄 `index.html` 改為 GitHub Pages 導向頁，轉往 `game_db/`。
- Capacitor `webDir` 改指向 `game_db`；`build_dist.py` 改以 `game_db` 為來源輸出到 `working_db/builds/dist/`。
- 報告輸出路徑改為 `working_db/reports/`，生成腳本與文件路徑同步更新。

## [1.9.18] - 2026-10-21

- 寶箱改版：以 Gemini 重新設計鐵箱、黃金寶箱、白金寶箱三階圖示，換上可愛精緻的 3D 玩具質感透明圖，並用金屬色、金光與冰晶光暈讓稀有度一眼可辨。
- 棋盤格隱藏寶箱、關鍵寶箱與結算寶箱卡片同步改用新圖示；結算卡片加上對應稀有度的底色與光暈。
- 寶箱圖示納入 service worker 預快取與 `build_dist.py` 出貨清單。

## [1.9.17] - 2026-10-17

- 部署 139 張「風格A」恐龍圖鑑磚（含批次生成管線與報告），圖鑑全卡面標籤改為只顯示編號。
- 4×4 區域過關故事改以生成影片演出（`assets/story_lv4_720p.mp4`），全屏無旁白短片形式。
- 開場改播 `assets/game.mp4` 全屏影片，再進入 logo 飛入動畫；補上開場靜音時的「開啟聲音」按鈕。
- 修正圖鑑分頁標籤誤顯示目前分頁數量的問題。
- 依 2026-10-14 決策停止產生單檔 `dragonfinder_v*.html` 版本包，遊戲以 `index.html` 多檔案形式出貨。
- 上架前置（本批次）：og/description meta、manifest.webmanifest、PWA 圖標組、service worker 離線快取、`build_dist.py` 出貨包腳本、載入效能最佳化、遊戲內「關於」頁、`js/ads.js` 廣告節點。
