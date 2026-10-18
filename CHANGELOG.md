# 更新日誌 CHANGELOG

本檔自 **v1.9.17** 起建立，之後每次出貨（含上架平台包）皆需同步新增一筆，並與 `index.html` 的 `ver-badge` 版本號一致。
v1.9.17 之前的完整歷史請見 git commit log 與 `worklogs/history/` 的歸檔工作紀錄。

格式：`- [版本] - 日期：摘要（細項）`

---

## [1.9.17] - 2026-10-17

- 部署 139 張「風格A」恐龍圖鑑磚（含批次生成管線與報告），圖鑑全卡面標籤改為只顯示編號。
- 4×4 區域過關故事改以生成影片演出（`assets/story_lv4_720p.mp4`），全屏無旁白短片形式。
- 開場改播 `assets/game.mp4` 全屏影片，再進入 logo 飛入動畫；補上開場靜音時的「開啟聲音」按鈕。
- 修正圖鑑分頁標籤誤顯示目前分頁數量的問題。
- 依 2026-10-14 決策停止產生單檔 `dragonfinder_v*.html` 版本包，遊戲以 `index.html` 多檔案形式出貨。
- 上架前置（本批次）：og/description meta、manifest.webmanifest、PWA 圖標組、service worker 離線快取、`build_dist.py` 出貨包腳本、載入效能最佳化、遊戲內「關於」頁、`js/ads.js` 廣告節點。
