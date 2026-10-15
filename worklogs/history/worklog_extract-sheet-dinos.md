# 規格表五龍去背摳圖（extract-sheet-dinos）

- Date: 2026-10-15
- Task ID: extract-sheet-dinos

## 需求

使用者提供一張 1024×1024 規格表（`attachments/.../image.png`），內含 5 隻恐龍與其名稱標籤（小盜龍_Microraptor_001_1星、迅猛龍_Velociraptor_041_2星、劍龍_Stegosaurus_081_3星、雷克斯暴龍_Tyrannosaurus Rex_121_4星、阿根廷龍_Argentinosaurus_161_1星），要求逐隻摳出成獨立透明背景圖片作為 dragon finder 的恐龍圖片，並以圖上名字作為檔名。

## Step-by-step record

1. Surveyed 資源慣例：`assets/dinos/` 為遊戲用編號 webp（200×200，js/data.js 以 `assets/dinos/<id>.webp` 引用）；`assets/dinos_2/` 存放具名 PNG（如 `DFD-000_伴伴_1star.png`）。Result: 新圖存放 `assets/dinos_2/`、以圖上標籤命名最符合既有慣例。
2. 分析原圖：1024×1024 RGB **無 alpha**，棋盤格背景為烘焙像素（白 255 / 灰 233），恐龍帶柔和投影，標籤為黑字（底部兩張標籤為白字）。Result: 無法直接裁切，需去背；標籤必須排除。
3. 背景分類規則：中性色（max−min<12）且 min≥140 → 背景（同時吸收灰階投影），其餘為前景。Result: 恐龍邊緣的混色 AA 像素保留為前景，去背邊緣乾淨。
4. 首次嘗試：closing(iter=2) + 全域连通块 ≥1500 → 失敗兩處：(a) T-Rex 腳底與底部白字標籤僅隔 1–2px，closing 把整行白字併入暴龍；(b) 劍龍標籤「劍」字筆畫與 T-Rex 頭冠 AA 黏連（8-连通）。Result: 不可全域 closing，需按恐龍個別處理。
5. 嘗試逐區域矩形隔離 + 面積閾值：矩形仍包含相鄰恐龍碎片（劍龍背板尖端落入小盜龍/迅猛龍矩形、劍龍腳尖落入 T-Rex 矩形）。Result: 矩形方案問題同樣棘手，放棄。
6. 關鍵發現：不做 closing 時，**每隻恐龍自然就是單一连通块**（44k–106k px），所有文字筆畫與雜訊均 <250px（最大文字塊 2197px 為底部整行白字，位於任何恐龍框外）。Result: 最終演算法確定——保留 ≥250px 连通块即恰好 5 隻恐龍。
7. 補洞策略：對每隻恐龍 `binary_fill_holes` 補回牙齒/眼白（內部洞），並加入「外來前景」偵測：洞內若含其他连通块的前景像素（文字筆畫橋接形成的假洞）則不補。Result: 程式化驗證 T-Rex 案例 foreign=0（該處實為前景黏連而非洞），規則保留作為安全網。
8. T-Rex 頭冠手術切除：「劍」字左偏旁筆畫（全圖 x413–424, y543–557）以 AA 黏在頭冠尖上，對 T-Rex mask 施加切除矩形 x≥405 & y≤560。Result: 文字筆畫全數移除，頭冠僅損尖端正上方約 3px，目視確認冠尖完整。
9. 輸出：RGB 取自原圖、alpha=mask + GaussianBlur(0.8) 羽化，外留 6px 邊距，存為 `assets/dinos_2/<標籤>.png`（5 張：360×356、491×370、418×319、468×463、559×585）。「Tyrannosaurus Rex」中的空格依網頁資源慣例改為底線（`Tyrannosaurus_Rex`）。Result: 5 張透明背景 PNG 完成。
10. 目檢：5 張圖合成於洋紅底色逐一檢視——羽毛間隙（小盜龍）、牙齒眼白（T-Rex、劍龍）、背板與尾刺（劍龍）、尾羽（迅猛龍）、腿間縫隙（阿根廷龍）均正確保留；阿根廷龍腹下暗色區域經與原圖比對確認為原畫後腿陰影，非殘影。Result: 摳圖品質通過。
11. HTTP 驗證：`python -m http.server 8767` 起服後以 URL-encoded 請求 5 張圖 → 全部 200（185–376 KB）；伺服器已停止、端口已釋放。Result: 通路驗證通過。
12. 未動 `index.html`/`js/data.js`/`css/style.css`/`assets/dinos/`：新圖尚未登錄進遊戲資料（ID 001/041/081/121/161 的歸屬、抽卡池、進化鏈為後續整合決策）。工具腳本 `assets/dinos_2/_extract_sheet5.py` 保留可重跑。

## Final status

- Status: Complete — 5 張具名透明背景恐龍圖已交付至 `assets/dinos_2/` 並通過目檢與 HTTP 驗證；data.js 登錄待使用者決定
- Commit hash: Pending
