# 工作日誌：方案A第1話彩色漫畫試刊（comic_pilot）

- 任務：用戶選定方案 A《彩虹羅盤與失落的探險隊》，先製作「第 1 話・沙灘上的第一片彩虹」彩色漫畫試刊一頁（6 格），驗證 AI 生成彩色漫畫的可行性與畫風一致性。
- 日期：2026-10-22
- 狀態：已完成（試刊頁交付 commit `5c4004d`；待用戶確認後再決定後續話數與是否導入遊戲）

## 步驟記錄

1. 盤點生成管線（完成）
   - 沿用 repo 既有 Gemini 圖像管線：key 位於 `working_db/generated_assets/dinos_2/bban_samples/_gemini_key2.txt`（與 chests 管線同一把）。
   - 參照圖：`game_db/assets/dinos_2/DFD-000_伴伴_1star.png`（伴伴嬰幼體，第1話時間點）、`game_db/assets/dinos/9.webp`（薩爾塔龍寶寶）；壓平白底後以 inline_data 附於每次請求。
   - 模型清單沿用：gemini-2.5-flash-image → 3.1-flash-image → nano-banana-2.1，逐一 fallback。

2. 設計第 1 話 6 格分鏡（完成，內嵌於生成腳本）
   - P1 金沙灘開場：主角與伴伴走向擱淺探險隊補給箱（旁白框）。
   - P2 伴伴嗅出沙中彩虹碎片一角（對白：嗅到了！亮晶晶的味道！）。
   - P3 薩爾塔龍寶寶把碎片當項鍊、兩人傻眼（對白×2）。
   - P4 主角沙上畫圈推理「最氣派的沙堡」（對白）。
   - P5 三人同挖、寶寶把碎片讓出（對白：分你一半！）。
   - P6 手捧碎片特寫＋旁白「永遠，把恐龍當朋友」（章末鉤子）。
   - 主角設定：10 歲探險家小孩（卡其探險帽／米色背心／橘T／綠背包），各格以相同英文描述維持一致。
   - 生成約束：畫面內禁止文字與對話泡（文字一律後製，避免 AI 中文字亂碼）。

3. 生成 6 格分格圖（完成）
   - 腳本 `working_db/generated_assets/comics/_gen_comic_propA_ch01.py`。
   - 修正一次路徑層級錯誤（key 與參照圖路徑）後重跑。
   - 6 格全部生成成功（`_raw/propA_ch01_p1..p6.png`，約 1184×864），目視檢查：角色（小孩／伴伴／薩爾塔龍寶寶）跨格一致、構圖符合分鏡。
   - 已知瑕疵：P3 模型自畫了一個空對話泡（違反「畫面內禁止對話泡」指示）。

4. 合成漫畫頁（完成）
   - 腳本 `_compose_comic_propA_ch01.py`：2×3 分格、深藍標題列、PIL 圓角對話泡（尾指說話者）、旁白框、頁尾；繁中使用系統字型 msjhbd.ttc／msjh.ttc。
   - 修掉三個合成問題：① P3 空對話泡以相鄰晴空貼圖蓋掉（PATCHES，先量測白點實際範圍 x0.512–0.583／y0.125–0.229 再精準覆蓋）；② 對白說話者更正——P3 拿碎片的是薩爾塔龍寶寶不是伴伴；③ 末格 caption 鍵值 6 超出 idx 範圍（0–5）改成 5，隊規旁白才畫得出來。
   - 產出：`working_db/generated_assets/comics/propA_ch01_page1.png`（1826×2236）。

5. 驗證與交付（完成）
   - 以 Read 檢視最終成品頁：6 格完整、對話泡位置與尾尖對準說話者、P3 無殘留白點（程式掃描 near-white=0）、標題列／旁白框／頁尾正常。
   - `.gitignore` 增加 `working_db/generated_assets/comics/_raw/`（沿用 chests 管線慣例：原始生成圖留在本地）。
   - commit＋push：腳本 ×2、成品頁 PNG、工作日誌、gitignore 規則。

