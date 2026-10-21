# 寶箱圖示改用 Gemini 3D 玩具質感

- 日期：2026-10-21
- Task ID：chest-gemini-art
- 目標：寶箱圖示太醜，改用 Gemini 設計三階寶箱（鐵箱／黃金寶箱／白金寶箱），要求可愛、精緻質感、稀有度清楚。

## 需求

- 以 Gemini 重新設計三階寶箱圖示，風格要可愛、有精緻的 3D 玩具質感。
- 三階稀有度（鐵箱／黃金寶箱／白金寶箱）必須一眼可辨。
- 棋盤格隱藏寶箱、關鍵寶箱與結算寶箱卡片全部同步換圖。

## 步驟記錄

### 1. 盤點現況

- 寶箱原本是 `js/main.js` 的 `chestSvgFor()` 程式繪製 SVG，用於三個地方：
  - 棋盤格挖到的隱藏寶箱 overlay（`.chesthide`）
  - 開局即顯示的關鍵寶箱縮圖（`.chestshow`）
  - 過關結算的寶箱逐一彈開卡片（`chestStripAnimate`）
- 原本三階只靠 SVG 顏色（鐵灰／黃／白）區分，造型完全相同，質感與稀有度都不明顯。

### 2. 建立 Gemini 生成管線

- 新增 `assets/chests/_gen_chests.py`：
  - 金鑰沿用 `assets/dinos_2/bban_samples/_gemini_key2.txt`；風格參考圖為 `assets/dinos_2/DFD-000_伴伴_2star.png`（風格A 的伴伴）。
  - 模型鏈：`gemini-2.5-flash-image` → `gemini-3.1-flash-image` → `gemini-nano-banana-2.1`，前一個失敗才換下一個。
  - 共用 FAMILY 提示詞：單一「閉合」寶箱、略帶三／四分之一視角、矮胖圓潤、厚實金屬護角、圓形中央扣鎖、兩隻短腳、柔和有機緞面光澤與自然磨損，明確排除硬塑膠／vinyl 亮面、角色臉孔與恐龍；純白背景、無陰影無文字、約佔方形畫面 80%。
  - 三階提示詞：
    - iron：暗板岩藍鐵板＋鉚釘、胡桃木側板、樸素黃銅扣鎖、少量青苔汙漬，讀作最普通、最便宜的寶箱。
    - gold：飽和蜂蜜金金屬板＋黃銅飾條、蓋面藤蔓紋、星形琥珀寶石扣鎖、紅棕木側板、細碎金光；明確排除偏白的奶油色／象牙色／米色。
    - plat：白金／白金色金屬＋銀色飾條、側面翼狀紋飾、蓋頂冰藍水晶簇、海藍寶石扣鎖、珍珠鑲嵌與淡冰藍光暈。
  - 家族一致性：gold 以 iron 生成圖為第二參考圖、plat 以 gold 生成圖為第二參考圖，形成 iron → gold → plat 的設計語彙鏈。
  - 產出：`_raw/<tier>_raw.png`（1024×1024 RGB）。

### 3. 生成與修正

- 依序生成 iron、gold、plat 三張 raw。
- 第一版黃金寶箱顏色偏淡（奶油／象牙感），保留為 `_raw/gold_raw_v1.png`；強化提示詞為「RICH SATURATED HONEY-GOLD、NOT pale cream、NOT ivory、NOT beige、amber-shaded crevices」後重新生成，得到飽和的蜂蜜金版本。
- 最終三張 raw 皆為 1024×1024：
  - `iron_raw.png` 890,916 bytes
  - `gold_raw.png` 1,047,026 bytes
  - `plat_raw.png` 1,025,617 bytes

### 4. 去背與切圖

- 新增 `assets/chests/_post_chests.py`：`rembg` 去背 → 以 alpha bbox 裁切 → 最大邊加 6% 留白的方形畫布 → 512×512 LANCZOS master → 256×256 RGBA WebP（quality 92、method 6）。
- 產出與實測：

| 階級 | 遊戲圖 | 大小 | 不透明覆蓋率（512 master） |
| --- | --- | --- | --- |
| 鐵箱 | `assets/chests/iron.webp` | 13,330 bytes | 51.31% |
| 黃金寶箱 | `assets/chests/gold.webp` | 16,536 bytes | 51.31% |
| 白金寶箱 | `assets/chests/plat.webp` | 16,214 bytes | 53.29% |

- 三張皆為 256×256 RGBA 透明背景，符合棋盤格縮圖與結算卡片使用。
- `_raw/`（生成原圖／去背中間圖）與 `_master/`（512 母檔）列入 `.gitignore`，只提交遊戲用 WebP 與兩支管線腳本。

### 5. 遊戲整合

- `js/main.js`：
  - 移除 `chestSvgFor()`，新增 `chestIconFor(tier)`，輸出 `<img class="chest-img t-<tier>" src="assets/chests/<tier>.webp">`；未知階級回落 iron。
  - `renderBoard()` 的隱藏寶箱與關鍵寶箱兩處呼叫改為 `chestIconFor(...)`。
  - `chestStripAnimate()`：卡片加上 `t-<tier>` class，並在獎勵文字上方新增稀有度標籤 `<div class="chest-tier">鐵箱／黃金寶箱／白金寶箱</div>`。
- `css/style.css`：
  - `.chest-img` 基礎樣式（block、contain、不可拖曳）。
  - 三階光暈：鐵箱低調灰影、黃金寶箱暖金光、白金寶箱冰藍光。
  - `.cell .chesthide .chest-img` 88%、`.cell .chestshow .chest-img` 100%，沿用原本的彈出與浮動動畫。
  - 結算卡片加上三階底色漸層、`.chest-ico` 底部徑向光暈、76×76 圖示與 `chestPop` 彈開動畫；`.chest-tier` 標籤以鐵灰／金棕／冰藍三色區分。

### 6. 版本、快取與出貨清單

- `sw.js`：`VERSION` 升至 `v1.9.18`，CORE 內版本查詢字串同步更新，並加入 `assets/chests/iron.webp`、`gold.webp`、`plat.webp` 預快取。
- `index.html`：標題、兩處版本徽章與所有 `?v=` 版本查詢字串升至 `1.9.18`（含「關於」頁版本文字）。
- `build_dist.py`：`SINGLE_ASSETS` 加入三張寶箱 WebP，出貨包會帶到 `dist/assets/chests/`。
- `.gitignore`：忽略寶箱管線中間檔 `assets/chests/_raw/`、`_master/`。
- `CHANGELOG.md`：新增 `[1.9.18]` 條目，記錄寶箱改版、稀有度樣式與快取／出貨清單更新。
- `AGENTS.md`：新增「Treasure chest art」段，記錄寶箱美術方向、階級語言、管線與禁止改回 inline SVG。

### 7. 本機驗證

- `node --check js/main.js` 語法通過。
- `grep chestSvgFor js/main.js` 已無任何引用。
- `python build_dist.py` 於工作區執行成功：201 檔、28.4 MB、資產引用檢查 `[OK]`，三張寶箱 WebP 皆複製到 `dist/assets/chests/`（工作區同時含其他進行中工作如 privacy.html／haptics.js／iOS 圖示，故檔數較大；提交內容本身的出貨驗證見下方）。
- `python -m http.server 8765` 起服務，以下皆 HTTP 200：`index.html`、`css/style.css?v=1.9.18`、`js/main.js?v=1.9.18`、三張寶箱 WebP、`sw.js`。
- 瀏覽器實測：
  - 版本徽章顯示 `v1.9.18`。
  - Service worker 由 `http://127.0.0.1:8765/sw.js` 控制，快取 `df-v1.9.18` 內含三張寶箱圖。
  - 三張寶箱圖實際載入尺寸皆為 256×256。
  - 真實 6×6 盤面可看到鐵箱／黃金寶箱格與右下角關鍵寶箱，透明圖正常疊在盤面色塊與格線上。
  - 過關結算卡片顯示「鐵箱」「黃金寶箱」「白金寶箱」稀有度標籤與對應底色、光暈，彈開動畫正常。
  - 主控台無遊戲程式錯誤（先前紀錄的錯誤皆為測試注入腳本自身造成，非遊戲程式）。
- 驗證用臨時預覽頁 `tmp_chest_preview.html` 已刪除。
- 提交後另以「commit 抽出的暫存副本」（port 8766）驗證提交內容本身：
  - `python build_dist.py`：181 檔、25.1 MB、`[OK]`；`dist/assets/chests/` 三張 WebP 齊全、`dist/js/` 只有原本 5 支腳本（未混入 haptics.js）、`dist/index.html` 有 7 處 `v=1.9.18`。
  - HTTP 200：`index.html`、`css/style.css?v=1.9.18`、`js/main.js?v=1.9.18`、三張寶箱 WebP、`sw.js`。
  - 瀏覽器實測：版本徽章 `v1.9.18`；Service worker 由 `127.0.0.1:8766/sw.js` 控制、快取 `df-v1.9.18` 內含三張寶箱圖；三張圖載入 256×256；以 `renderBoard()` 實際渲染出 `.chesthide`（iron／gold／plat）與 `.chestshow` 關鍵寶箱，挖到的黃金寶箱與帶冰藍光暈的白金關鍵寶箱在盤面上正確顯示；`chestStripAnimate()` 產生的卡片 class／稀有度標籤／圖片皆正確（鐵箱／黃金寶箱／白金寶箱）；教學點擊推進元素 `#tut-tap` 仍在、`haptics.js` 未載入（屬其他未提交工作）；主控台無遊戲程式錯誤。
  - 驗證完成後已關閉 8765／8766 兩個本機伺服器並刪除暫存副本與暫存腳本。

### 8. 提交

- 工作區同時存在其他未完成工作的變更（iOS 上架準備、關於頁精簡、觸覺回饋等），為避免混入，採分離式提交：只把寶箱相關內容寫入 git index，其他工作保留在工作區。
- 分離式提交作法：`sw.js`／`CHANGELOG.md`／`AGENTS.md`／寶箱 WebP／兩支管線腳本／本 worklog 整檔加入；`index.html`／`css/style.css`／`js/main.js`／`.gitignore`／`build_dist.py` 以 `git show HEAD:` 內容為基底做精確替換後 `git hash-object`／`git update-index` 寫入（`index.html` 依原 blob 保留 CRLF 行尾）。staged diff 已逐檔檢查：`index.html` 只有 11 行版本號更新，並以 grep 驗證未混入 haptics／Capacitor／viewport-fit／關於頁精簡／privacy.html、css 未混入 safe-area／dvh、js 未混入 Hap 呼叫、`.gitignore` 未混入 node_modules／dist、`build_dist.py` 未混入 privacy.html／haptics.js。
- 提交前對 staged js blob 跑 `node --check` 通過。
- 交付 commit：`e881e39`（Redesign the three chest tiers with Gemini toy-style art）。

## 最終狀態

- 新增：`assets/chests/iron.webp`、`gold.webp`、`plat.webp`、`_gen_chests.py`、`_post_chests.py`。
- 修改：`js/main.js`、`css/style.css`、`index.html`、`sw.js`、`build_dist.py`、`.gitignore`、`CHANGELOG.md`、`AGENTS.md`。
- 驗證：語法檢查、出貨打包、HTTP 200、Service worker 快取、瀏覽器盤面與結算卡片實測皆通過（工作區與提交內容副本各驗一次）。
- 交付 commit：`e881e39`（Redesign the three chest tiers with Gemini toy-style art）。
