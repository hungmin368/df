# 恐龍快找 DragonFinder

在彩色領地中推理隱藏物的位置，用捕捉器找出恐龍——收集 139 隻恐龍圖鑑、解鎖區域故事、挑戰 2000 層龍塔的恐龍解謎遊戲。

## 目錄結構

```
index.html                  GitHub Pages 入口，僅重新導向到 game_db/
game_db/                    遊戲本體（唯一出貨內容）
  index.html                遊戲頁面（含 <link> / <script> 引用）
  privacy.html              隱私政策
  manifest.webmanifest      PWA manifest
  sw.js                     Service worker（相對 game_db/ 快取）
  css/
    fonts.css               內嵌字型 @font-face
    style.css               主樣式
  js/
    data.js                 恐龍資料 DINOS / LEGENDS（139 隻）
    main.js                 遊戲主程式
    tower.js                龍塔邏輯
    tower_comments.js       龍塔留言
    ads.js                  廣告節點
    haptics.js              震動回饋
  assets/                   遊戲實際載入的圖片、影片、字型、圖示
working_db/                 任務產物（不直接出貨）
  reports/                  HTML 報告
  generated_assets/         生成素材與管線（dinos_2/、chests/、videos/、icons/、images/）
  store/                    App Store 截圖與上架素材
  builds/                   選擇性建置輸出（dist/）
  docs/                     設計與參考文件
  archive/                  備份與退役腳本
tools/                      維護腳本（build_dist.py、build_ios_icons.py、shoot_ios_screenshots.py）
ios/                        Capacitor iOS 專案
worklogs/                   未完成任務的工作紀錄（完成後刪除）
```

## 開啟方式

- 直接以瀏覽器開啟 `game_db/index.html`（file:// 即可）。
- 或在專案根目錄啟動靜態伺服器：`python3 -m http.server`，開 `http://localhost:8000/game_db/`。
- GitHub Pages 根網址 `/df/` 會由根目錄 `index.html` 導向 `/df/game_db/`。

## 建置與 iOS

- `npm run build`：將 `game_db/` 完整複製到 `working_db/builds/dist/`，並核對執行期引用。
- `npm run sync`：`npx cap sync ios`（Capacitor `webDir` 直接指向 `game_db`）。
- iOS 圖示／啟動畫面：`python tools/build_ios_icons.py`（輸出到 `working_db/generated_assets/icons/`）。

## 開發慣例

- 遊戲功能修改一律在 `game_db/` 內進行；新產生但遊戲未直接使用的檔案先放進 `working_db/` 對應分類，使用者指示放入遊戲後才移到 `game_db/`。
- 玩家進度存在瀏覽器 `localStorage` 的 `dinodoku-*`。
- 報告一律輸出到 `working_db/reports/`。
- 詳細規範見 `AGENTS.md`；版本紀錄見 `CHANGELOG.md`。
