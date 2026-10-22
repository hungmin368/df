# 工作日誌：方案A第1話彩色漫畫試刊（comic_pilot）

- 任務：用戶選定方案 A《彩虹羅盤與失落的探險隊》，先製作「第 1 話・沙灘上的第一片彩虹」彩色漫畫試刊一頁（6 格），驗證 AI 生成彩色漫畫的可行性與畫風一致性。
- 日期：2026-10-22
- 狀態：v3 正式版已交付（commit `62c75ba`；寫實背景＋3D 立體感，正式模型 gemini-2.5-flash-image）；
  三模型比較報告與 v3 預覽見 `working_db/reports/comic_model_compare_report.html`（圖片已內嵌）；
  待用戶驗收後再決定後續話數與是否導入遊戲（v1 commit `5c4004d`、v2 commit `31b9e6c` 為舊版留存）

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

## 第 2 輪：用戶回饋修正（v2）

6. 用戶三項新要求（完成）
   - 漫畫中的恐龍角色與伴伴必須跟遊戲的角色圖片一致。
   - 畫風改為日本少年漫畫風格。
   - 不必用方正格子，可用誇張格子與跨格強化劇情。

7. 角色一致性根因與修正（完成）
   - v1 不一致根因：生成描述寫「cream satin body／blue-grey」，文字描述蓋過參照圖實際外觀——遊戲中伴伴實為紫色寶寶龍（金角、粉紫翅膜、琥珀眼、奶油肚）、`dinos/9.webp` 薩爾塔寶寶實為石板灰＋螺旋捲尾。
   - v2 改用 `DFD-000_伴伴_2star.png`（無蛋殼立姿）＋`9.webp` 作為內容參照，並加入 CHARACTER LOCK 嚴格指令（顏色、花紋、比例、臉部一律照參照圖，僅姿勢表情可變）。

8. 少年漫畫風 6 格重生成（完成）
   - 新腳本 `_gen_comic_propA_ch01_v2.py`：STYLE 改為 full-color shonen manga（粗墨線、速度線、cel-shading）；各格指定寬高比（P1/P4＝21:9、P3/P5＝16:9、P2/P6＝3:2），fallback 16:9→4:3→無。
   - P6 重生成兩次：①補齊三角色入鏡＋伴伴紫色鎖定；②碎片形狀修正（六角水晶碎片，非圓形羅盤）與翅膜顏色（粉紫，非橘）。
   - P1 模型自畫黑框且框內有亮色速線穿越，原閾值 bbox 法失效；合成時改逐邊掃描（整行／列 >50% 像素偏暗即視為框）成功裁除。

9. 動態版面合成（完成）
   - 新腳本 `_compose_comic_propA_ch01_v2.py`（畫布 1826×2236）：斜切標題帶＋紅色試刊徽章；P1 全寬橫幅；P2 逆時針斜格；P3 平行四邊形格（左緣斜切）；P4 全幅出血跨格＝震驚高潮；P5 順時針斜格；P6 右、下雙出血格＝結尾。
   - 斜格以旋轉＋多邊形 mask 裁形，粗黑框沿斜邊描線；對話泡改少年風（圓角粗框尖尾泡＋鋸齒爆裂泡）；P6 隊規用金框銘牌。
   - 產出 `propA_ch01_page1_v2.png`（1826×2236）。

10. v2 驗證（完成）
   - 角色比對：伴伴（紫身、金角、粉紫翅膜、琥珀眼、奶油肚、金爪）與薩爾塔寶寶（石板灰、螺旋捲尾、金刺、粉內耳）皆與遊戲圖一致；小孩造型跨格一致。
   - 版面檢查：P1 黑框已除、標題帶副標完整、各泡尾尖指向說話者、P6 銘牌可讀、出血格無破版。
   - commit＋push：v2 腳本 ×2、成品頁 PNG、工作日誌。

## 第 3 輪：同提示詞三模型比較（用戶要求「用同樣提示詞使用gemini生成，我想比較一下」）

11. 生成／合成腳本參數化（完成）
    - `_gen_comic_propA_ch01_v2.py` 增加 CLI：`--model`（單模型，停用 fallback 鏈）、`--prefix`（輸出檔名前綴，預設 v2）、位置參數選格。
    - `_compose_comic_propA_ch01_v2.py` 增加 `--prefix`（讀取哪組底圖）與 `--suffix`（輸出頁名後綴）；回歸測試預設參數輸出與已交付 v2 頁一致。

12. gemini-3.1-flash-image（m31）生成 6 格（完成）
    - `--model gemini-3.1-flash-image --prefix v2_m31`，6/6 格一次達標指定長寬比。
    - 目視檢查：角色忠誠度好、畫面乾淨偏賽璐璐動畫；場景缺失——P2 變沙漠、P4 變叢林遺跡；P3 多畫一隻旁觀伴伴；P5 水晶插在遠處沙丘。

13. gemini-nano-banana-2.1（mnb）生成 6 格（完成）
    - `--model gemini-nano-banana-2.1 --prefix v2_mnb`，6/6 格一次達標指定長寬比。
    - 目視檢查：色彩最濃郁、角色互動最有戲、墨線偏西方卡通；P2 多一隻薩爾塔且場景偏乾草原、P3 多伴伴、P4 背景變森林；P5/P6 全對且收尾最華麗。

14. 兩頁組版＋比較報告（完成）
    - `--prefix v2_m31 --suffix _m31`、`--prefix v2_mnb --suffix _mnb` 各合成整頁（1826×2236），共用同一套氣泡／標題／銘牌排版；目視檢查兩頁氣泡尾尖與說話者對位正常。
    - 報告 `working_db/reports/comic_model_compare_report.html`：三版完整頁並列、P1–P6 逐格三聯圖＋單格筆記、綜合評分表、結論（建議維持 2.5-flash；mnb 為氣氛格備援；m31 場景遵循最弱）。
    - HTTP 驗證：localhost 開啟報告，21 張圖 0 張破圖，表格／結論區渲染正常。

15. 提交推送（完成）
    - commit：參數化腳本 ×2、兩頁新成品 PNG、比較報告 HTML、工作日誌；push 至 main。

## 第 4 輪：比較報告圖片修復（用戶回報「html裡面看不到圖片」）

16. 根因診斷（完成）
    - 報告以相對路徑引用 `../generated_assets/comics/_raw/` 的 18 張分格圖，但 `_raw/` 在 `.gitignore`（第 46 行）——GitHub Pages 上全數 404；僅 3 張整頁 PNG 有入 git。
    - 用戶端看不到圖片即此因（本機 http 驗證時 `_raw/` 存在所以當時沒抓到）。

17. 報告改為單檔自足（完成）
    - 新腳本 `_inline_comic_report_images.py`：21 張圖（3 整頁 860px／18 分格 760px 寬）轉 JPEG q85 後以 base64 data URI 內嵌；`<a href="_raw/…">` 18 條失效連結解除（整頁 PNG 已入 git，保留點擊開原圖）。
    - 報告同時補註：2.5-flash 已確認為正式製作模型、新方向為寫實背景＋3D 立體感；頁尾註明圖片已內嵌、原始檔位置。

18. 驗證（完成）
    - localhost 開啟：21/21 張皆 data URI、0 破圖、0 殘留 _raw 連結；檔案 3.7 MB，逐節渲染正常。

## 第 5 輪：正式模型確認＋v3 風格升級（用戶指示：維持 2.5-flash、背景寫實、整體 3D 立體感）

19. 生成腳本升級 v3（完成）
    - STYLE 改為「3D CG 動畫電影劇照感」：角色粗墨線＋3D 玩具體積光影、背景 PHOTO-REALISTIC
      （真實沙粒貝殼／透明海水反光／體積光）、投射陰影＋AO＋大氣透視＋景深；分鏡與角色鎖定不變。

20. gemini-2.5-flash-image 生成 v3 六格（完成）
    - `--model gemini-2.5-flash-image --prefix v3`，6/6 一次達標指定長寬比；六格場景與出場角色數全對（6/6）。
    - 翅膜顏色查核：首輪 P1/P2/P4/P6 翅膜偏橘紅，一度以「絕不橘色」LOCK 重跑四格；重跑後與遊戲原圖
      `DFD-000_伴伴_2star.png` 逐像素比對，確認原圖翅膜本身就是「粉紫→暖橘」漸層＋紫點——
      v3 渲染反而更忠實，LOCK 措辭改回忠實漸層描述（移除自相矛盾的禁橘令）。

21. v3 組版＋氣泡 per-prefix 覆寫（完成）
    - 組版腳本新增 `BUBBLES_BY_PREFIX`：v3-P4 新構圖（薩爾塔左／男孩中／伴伴右）兩顆氣泡重新對位
      （尾尖不再指錯說話者、男孩臉不再被泡泡蓋住）；v3-P5 尾尖由沙堡改指男孩。
    - 產出 `propA_ch01_page1_v2_v3.png`（1826×2236）；逐格目視：P1–P6 氣泡尾尖全部指向正確說話者。
    - 已知小瑕疵（可接受）：P1 補給箱彩虹漆較淡、P4 男孩高舉的右手被上緣裁切、P4 上方模型自畫白色
      驚嘆泡泡與爆裂泡相鄰。

22. 比較報告新增第六節「正式版 v3 預覽」（完成）
    - v3 整頁內嵌＋翅膜核對備註；重跑 inliner 後 22/22 圖 0 破圖（4.0 MB）。

23. 提交推送（完成）
    - commit：生成／組版腳本更新、v3 成品頁、報告更新、工作日誌；push 至 main（`62c75ba`＋`341d65a`）。

## 第 6 輪：寫實真人男孩試產（用戶要求先看單格效果）

24. 混搭風格指令撰寫＋生成（完成，成果遭用戶否決）
    - 用戶問「人類角色能更寫實像真人嗎」，評估可行後先試產 P2/P4 兩格。
    - `_gen_comic_propA_ch01_v2.py`：KID 改為 PHOTO-REALISTIC 真人男孩（真實膚質／髮絲／人體比例）；
      STYLE 改為 hybrid live-action/3D-CG 混搭（真人實拍男孩＋3D 玩具恐龍，背景維持寫實）。
      恐龍 CHARACTER LOCK 不變。
    - 首跑 `--model gemini-2.5-flash-image --prefix v4 2 4` 遇 HTTP 402（預付額度耗盡）；用戶儲值後
      重跑成功，產出 `propA_ch01_v4_p2.png`／`propA_ch01_v4_p4.png`（各 ~2.6 MB）。
    - **用戶看過後否決**：「這版人類角色真實版太差我不喜歡」——v4 混搭寫實路線不採用，v4 分鏡圖
      保留於 `_raw/`（gitignored）僅作紀錄；生產線維持 v3。

## 第 7 輪：四種寫實人類風格變體（改用 SophNet ImageGenerator）

25. 變體測試計畫（完成）
    - 用戶指示：生成「幾個不同的真實人類模型」供挑選，且 Gemini 額度再次耗盡 → 改走 SophNet
      ImageGenerator（repo 自家筆記 `working_db/docs/Imagegen_usage.md`）。
    - 設計四種真人渲染流派，同一格 P2 分鏡對照：film 電影實拍／photo 攝影寫真／gamecg 3A 遊戲
      CG／paint 寫實油畫插畫。恐龍維持 CHARACTER LOCK（爬蟲臉條款＋反擬人負向詞，但不含「人臉」
      以免誤傷畫面中真正的真人男孩）。
    - 先建 Gemini 版 `_gen_kid_style_variants.py`（同四變體），再建 SophNet 版
      `_gen_kidstyle_sophnet.py`（任務端點非同步、參考圖餵公網 URL）。

26. SophNet 模型可用性探針（完成，2026-10-22）
    - 舊同步路由 `/image-edit` 全模型 20204（路由已死）→ 生圖與編輯一律走任務端點
      `POST .../imagegenerator/task`＋輪詢 `GET .../task/{id}`。
    - `Qwen-Image-Edit`／`Z-Image-Turbo-Edit` 帶 images → 20030（不在型錄；空 input 的 10012 只是
      名稱預檢，不能證明已部署）。qwen-image 系與 Z-Image-Turbo → 20011 未部署。
    - 依官方文件補測：**`Wan2.6-T2I` 可用**（純文生圖，task 建立成功）；**`Qwen-Image-Edit-2509`**
      為編輯模型（空 input 回 10012「必須傳入至少 1 張參考圖片」）。
    - 誤建兩個空 prompt 探針任務（`2O1ncf...`／`2DWoP...`），輪詢確認皆已伺服器端失敗
      （20037 空 input），無垃圾產出；探針成本 ≤ 約 ¥0.5，如實記錄。
    - `_gen_kidstyle_sophnet.py` MODELS 定為 `[Qwen-Image-Edit-2509(帶參考圖), Wan2.6-T2I(純文字)]`，
      純文字模式改用無參考圖字樣的 DRAGON_DESC（跨後端提示詞需改寫，Imagegen_usage.md 教訓 8）。

27. 首跑除錯與模型策略調整（完成）
    - 首跑兩個坑：① Edit-2509 帶 `parameters`（size/seed/watermark）create 回 HTTP 500
      `20031 图片生成任务创建失败`——編輯模型不吃參數，裸 input 才建立成功；② create 回應實為
      `{"output":{"taskId","taskStatus"}}`（非文件舊版的 `result` 包裝），腳本原以
      `created.get("result")` 判成功 → 已建立的任務被誤判失敗、還會續建重複任務燒錢 → 立即
      taskkill 停跑（當機 kill 前有一次 in-flight create，可能多一張 ~¥0.25 的孤兒任務，
      無法回收 ID，如實記錄）。
    - 修補：新增 `find_task_id()`（相容 output/result 包裝）、成功即 break、poll 改讀
      `st["output"]`＋`extract_url(st)`、網路例外全捕（URLError/TimeoutError/OSError）＋
      create 180 秒逾時＋2 輪重試、以 `python -u` 跑即時看進度。
    - 用任務 ID 直接輪詢救回被誤棄的 film 任務（`4SwI60F93brmduBLTEB2fl` SUCCEEDED）→
      `kidstyle_film_p2_sophnet_edit2509.png`（1.7 MB）。目視：分鏡要素全中（男孩蹲看／紫龍嗅
      彩虹水晶／海灘），但 **Edit-2509 把「100% 實拍」指令整個無視，輸出統一 3D 卡通風**——
      恐龍鎖定成功（參考圖生效）但人類寫實化失敗。
    - 策略調整：改讓純文生圖 `Wan2.6-T2I` 優先（風格彈性大）。先以 photo 變體探針：
      task 建立一次成功、約 1 分鐘 SUCCEEDED 下載（2.5 MB）。目視：男孩有明顯攝影感
      （奶油散景／真實陰影／膚質細節），恐龍文字鎖定奏效（紫身紫點／金角金爪／橘漸層翅膜
      全對，僅年齡偏小 5–7 歲 vs 指定 10 歲）。→ 以 Wan 補齊 film/gamecg/paint，
      四變體同後端公平對照；Edit-2509 版 film 保留為報告對照卡。

28. 四變體全數完成（完成）
    - Wan2.6-T2I 依序跑完 film／gamecg／paint（各 1 次建立、約 1 分鐘 SUCCEEDED 下載，
      2.2–2.5 MB）；連同 photo 共四張，後端一致。
    - 目視結論：四變體風格有明確差異且恐龍設計四張全部一致命中（紫身紫點／金角金爪／
      粉紫→暖橘漸層翅膜＋紫點／粉內耳／奶油肚）。人類寫實度：photo 最有照片感（散景／真實
      陰影／膚質）、paint 忠實油畫筆觸、gamecg 為 Pixar 級 CG、film 偏動畫電影感（非真底片實拍，
      如實呈報）。

29. 選擇報告建置＋驗證（完成）
    - `_build_kidstyle_report.py` → `working_db/reports/kid_style_variants_report.html`
      （自足單檔 0.9 MB、6 張圖 base64 內嵌：v4 否決對照＋Edit-2509 後端對照＋四變體，
      描述含「意圖 vs 實測觀察」如實對照）。
    - 驗證：`python -m http.server 8000` + 瀏覽器實測——6/6 圖載入（naturalWidth>0）、
      6 個區塊齊全、深色主題可讀；curl 200（860 KB）。主控台錯誤均為其他頁面殘留，與本報告無關。

30. 提交推送（完成）
    - commit：`_gen_kidstyle_sophnet.py`（修正版）、`_gen_kid_style_variants.py`（Gemini 備援版）、
      `_build_kidstyle_report.py`、報告 HTML、工作日誌；push 至 main（`5cb72c9`）。
    - 成本如實申報：本輪 SophNet 花費≈探針空任務 2（伺服器端失敗，≤¥0.5）＋film Edit-2509
      1 張（已救回）＋疑似孤兒任務 1（kill 前在途，~¥0.25）＋Wan2.6-T2I 4 張（~¥1–2）≈
      總計 ~¥2–3。四變體成品因 `_raw/` gitignore 僅內嵌於報告中交付。

## 第 8 輪：v5 寫實油畫風整頁（用戶選定 paint 變體）

31. v5 生成腳本設計（完成）
    - 用戶指示：選用變體 paint（寫實油畫插畫），重跑全部六格並組版整頁，且
      **對話框不可重疊在角色臉上**。
    - 新建 `_gen_comic_propA_ch01_v5_paint_sophnet.py`：分鏡沿用 v3 六格；STYLE 換油畫風
      （男孩與場景油畫筆觸、兩龍 3D 玩具光澤跳出）；伴伴＋薩爾塔改文字鎖定（Edit 模型會毀
      油畫風，不當後端；四變體測試已證 Wan 文字鎖定可靠）；`parameters.size` 先帶
      ratio 對應尺寸（21:9→1792*768、16:9→1664*936、3:2→1536*1024），被拒再降級裸 input。
    - P1 單格先跑：size 參數被接受（實際輸出 1792×768，Wan 與 Edit-2509 行為不同），
      目視：油畫風到位、彩虹漆補給箱＋紫光、伴伴鎖定全對（紫點／金角漸層翅膜／粉耳／奶油肚）。

32. v5 六格生成（完成）
    - 背景依序跑完 P2–P6（size 參數全數被接受，實際輸出即指定長寬比）；逐格目視要素＋雙龍鎖定
      ＋油畫風落實。
    - 首輪 P4/P5/P6 一次到位（P4 男孩 jaw-drop＋薩爾塔戴項鍊＋速度線；P5 畫計畫圖＋雙龍火焰鬥志；
      P6 六角碎片高舉＋彩虹夕陽）。
    - 首輪 P2/P3 出現多餘角色（Wan 愛加戲）：P2 薩爾塔串場＋畫成圓羅盤；P3 伴伴入鏡＋薩爾塔
      被畫成短頸。→ 提示詞加固：P2「ONLY the boy and Dragon A appear…no other characters」＋
      碎片改「HEXAGONAL crystal shard, NOT a round compass dial」；P3「ONLY Dragon B appears,
      completely alone」＋「long slender neck stretched UPWARD」。
    - 重跑 P2/P3 一次成功：P2 只剩男孩＋伴伴、碎片為彩虹切面晶體；P3 薩爾塔單獨站浮木舉碎片、
      長頸高抬、螺旋尾貼臀。六格 6/6 通過目視驗收（鎖定全命中、油畫風一致）。
    - 成本：重跑 2 格 ≈ ¥1（Wan2.6-T2I 每格約 ¥0.5）。

33. v5 組版＋氣泡避臉校準（完成）
    - 先逐格量測臉部座標（P2 男孩右上/伴伴大頭中央；P3 薩爾塔頭在上半；P4 三張臉橫排；
      P5 三張臉橫跨上方；P6 三人全身、三張臉佔滿上半至中段），於組版腳本新增
      `BUBBLES_BY_PREFIX["v5"]` 全格覆寫＋`CAPTIONS_BY_PREFIX`（v5-P6 銘牌從 y0.80 下移到
      y0.62，否則會蓋住男孩與薩爾塔的臉）。
    - 校準原則：泡身只壓天空／翅膀／腳／沙地，尾巴尖端指向說話者（額頭／嘴），路徑繞開其他
      角色的臉。P6「耶——挖到了！」改由躍空的伴伴發聲（尾徑最乾淨且構圖上牠就是歡呼者），
      「分你一半！」為男孩。
    - 產出 `propA_ch01_page1_v2_v5.png`（1826×2236）；整頁目視：六格對話泡＋銘牌＋旁白
      全部不壓任何角色臉，尾尖全部指向正確說話者。

34. v5 驗證＋提交推送（完成）
    - 整頁目視驗收通過（對話框零臉部重疊）；`_raw/` 維持 gitignore，成品頁入 git。
    - commit＋push 至 main；交付 commit：`7236005`。

## 第 9 輪：角色體型特徵跨格一致性修正（用戶回饋：「登場角色的體型特徵外貌要固定，我看到在不同格有差異」）

35. 跨格特徵審計（完成）
    - 逐格比對三角色特徵（P1–P6 全數目視），偏差清單：
      ① 薩爾塔體態漂移最嚴重：P3 中長頸雙足直立站浮木 → P4 長頸雙足 → P5 短頸俯身近似四足
        → P6 短頸大頭四足；頭身比逐格不同。
      ② 伴伴翅膜斑點色：P1/P2/P4 為深紫點（與遊戲原圖 `DFD-000_伴伴_2star.png` 一致），
        P5 變亮桃紅點、P6 偏洋紅——LOCK 原文「magenta spots」措辭造成漂移。
      ③ 男孩年齡感：P2 偏幼（5–8 歲感），P4/P5/P6 接近 10 歲；臉型隨表情浮動。
      ④ 伴伴與男孩的角數量、背刺、耳朵、螺旋尾、服裝等其他特徵各格皆穩定。
    - canonical 基準（重跑對齊目標）：薩爾塔＝P4 的優雅長頸（頸長≈軀幹長、小頭），
      站姿依分鏡可變但頸長與頭身比固定；伴伴翅膜＝深紫圓點；男孩＝10 歲、同臉同裝。
    - 根因：LOCK 為質性描述（"long-necked"、"magenta spots"），Wan 對質性詞的數值詮釋逐格浮動。

36. 加固 LOCK 並重跑六格（完成）
    - LOCK 升級為量化 CHARACTER SHEET：伴伴＝亮紫身體＋深紫圓斑（never pink/red）、
      恰好一對金黃段節角＋單列金錐刺、桃紅→橙翅膜、粉內耳、奶油肚；薩爾塔＝頸長恰好＝軀幹長、
      頭寬＝1/4 軀寬、單列金黃刺、粉耳、螺旋尾尖貼臀；男孩＝明確 10 歲（不更小）＋逐件服裝清單。
      LOCK 移至提示詞末尾（recency 加權）；全格固定 seed=7（被拒自動降級 size+seed→size→裸 input）。
    - 6 格全數重跑成功（Wan 約 NT$0.5/格）；逐格目視驗證：三角色特徵跨格一致。
    - 兩格二次修正：P1 多生成薩爾塔（違反 ONLY TWO 指令）→ 補「no sauropod, no Dragon B」
      重跑成功；P5 沙堡消失（台詞失去對象）→ 補「must be clearly visible, not omitted」重跑成功。
    - P1 尺寸參數三度遭 20011 拒（降級方形）：第四度把構圖指令改為「全元素在下中段帶、
      上 1/3 純天空」→ 成功取得 1792×768 真寬幅（旁白牌淨空的前提）。

37. 重組版整頁並驗證氣泡避臉（完成）
    - BUBBLES_BY_PREFIX v5 依新構圖重校：P2 泡貼右上、尾落伴伴眉心雙眼間；P3 泡右側、尾指下頜；
      P4「喂——」爆裂泡壞男孩下半身、直尾入口下方；P5 泡左下蓋腿蓋沙、尾短直上指男孩嘴；
      P6 雙泡尾分指躍空伴伴嘴與男孩嘴。
    - CAPTIONS_BY_PREFIX v5 新增 P1 覆寫：旁白牌移置中央上空（x0.32–0.54 純天空帶），
      不再切男孩帽冠（v3 組版不受影響）。
    - 組版 bug 修復：paste_tilted 的旋轉畫布以紙色填充，右上角溢出蓋住 P1 左下角
      （男孩小腿與補給箱左下角被白角遮住）→ P1 改為 P2/P3 之後才貼（兩格無重疊）。
    - 整頁目視驗收：六格對話框（含尾尖）零臉部重疊；男孩全身、補給箱完整。

38. 一致性報告＋工作日誌＋提交推送（完成）
    - before/after 報告：`working_db/reports/comic_v5_consistency_report.html`
      （base64 內嵌自足單檔 2.9MB；含整頁與 P1–P6 逐格對照、特徵鎖定對照表、避臉驗證表；
      本地伺服器＋瀏覽器截圖驗證渲染正常）。
    - 成本：本輪共生成 10 格（6＋P1/P5 修正＋P1 構圖兩試）≈ NT$5；
      20011 NO_AVAILABLE_DEPLOYMENT 為佈署未配置錯誤，應未計費。
    - commit＋push 至 main；交付 commit hash 於推送後補記。
    - 暫存清理：z_*.png 除錯裁圖與 P1 兩版棄圖已刪（_raw 仍 gitignore；r1 備份留 _raw/_v5r1_backup/）。

