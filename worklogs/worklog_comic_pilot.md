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
    - commit＋push 至 main；交付 commit：`8ae154c`。
    - 暫存清理：z_*.png 除錯裁圖與 P1 兩版棄圖已刪（_raw 仍 gitignore；r1 備份留 _raw/_v5r1_backup/）。


## 第 10 輪：恐龍臉型體型跨格一致性（用戶回饋：「恐龍的臉型體型還是不連貫」）

39. 根因再診斷＋機制探測（進行中）
    - 審視 v5.1：量化 LOCK 固定了顏色/斑點/角刺數量，但「頭身比、臉型」仍漂移——
      P1/P5 的龍 A 偏寫實修長吻部，P2/P4/P6 偏 Q 版大頭；薩爾塔頸長比 P3/P4 vs P5/P6 仍不同。
      判定純文字鎖定已到極限，改用「參考圖驅動生成」。
    - 盤點可用模型：Gemini 仍 402 無額度；SophNet catalog 探測確認支援
      `Wan2.6-Edit`（Wan 同族，理論上保油畫風）、`Qwen-Image`（T2I）、`Qwen-Image-Edit`。
      Edit 模型請求形態：`input.images=[公開URL]`＋裸 input（帶 parameters 會 500/20031）。
    - 參考圖 URL（已驗證 HTTP 200）：伴伴 2star 遊戲官方圖、薩爾塔龍寶寶 9.webp（GitHub Pages）。
    - 探測腳本 `_probe_r10_p2.py`：同一 P2 場景跑三候選——
      ① Wan2.6-Edit＋[伴伴,薩爾塔] 雙參考；② Qwen-Image T2I＋量化 LOCK；③ Qwen-Image＋參考圖。
    - 結果：待探測腳本執行完畢後判定。

40. 用戶改道（第 11 輪：v6 攝影寫真）＋SophNet 參考圖探測結論（完成）
    - 探測結果：`Wan2.6-Edit`/`Qwen-Image-Edit`/`Edit-2509` 皆 20030（未佈署，catalog 已變）；
      `Qwen-Image` T2I 可用但雙參考圖建立逾時（伺服器抓 github.io 圖慢）、
      單參考圖可建；其輸出偏 3D 卡通渲染且會自創第三角色，非油畫。
    - 用戶指示：改用 Gemini、風格改「變體 photo：攝影寫真」（85mm 人像鏡、真實男孩、
      恐龍＝收藏級玩具立於真實沙灘；沿用 _gen_kid_style_variants.py photo 文案），重作 6 格。
    - 新腳本 `_gen_comic_propA_ch01_v6_photo_gemini.py`：photo 文案＋第 9 輪 canonical LOCK
      （深紫斑點等量化特徵）＋伴伴2star/薩爾塔9.webp 參考圖每格內嵌；
      P1 完成後縮圖作第三張連鎖參考餵 P2–P6 強化同男孩同龍。
    - P2 探針：待結果判定 Gemini 額度是否恢復（此前 402）。
    - P2 探針結果：Gemini 額度已恢復（gemini-2.5-flash-image 直出，2.2MB）；畫面與用戶附件範例一致
      （真實男孩＋紫玩具龍嗅彩虹六邊形碎片）。

41. v6 六格生成＋一致性修正（完成）
    - P1/P3/P4/P5/P6 依序生成（全部 gemini-2.5-flash-image 首發命中）；P2–P6 內嵌第三張參考＝P1 縮圖。
    - 逐格目視：龍A六格一致（紫身、雙金角、粉橙翼、深紫斑、奶油肚）；男孩同臉同裝。
    - 問題①：龍B（薩爾塔）LOCK 描述與參考圖（9.webp 灰藍捲尾）不合模——P3/P4 長頸+誤加蝠翼、
      P5 回到捲尾造型 → 修正 LOCK（石板藍長頸、橙刺、粉耳、明確 NO wings/horns）重跑 P3/P4/P5。
    - 問題②：P3 重跑仍帶蝠翼 → 再重跑一次移除，三格龍B統一為無翼長頸。
    - 問題③：P1 初版構圖偏滿版，横幅裁切把男孩頭與龍A下半身切掉 → prompt 加「人物置垂直中帶」
      約束重跑 P1。
    - 成本：本輪共 10 次生成（6＋P3/P4/P5 修正＋P3 二次＋P1 構圖）≈ NT$10 內。

42. v6 組版＋驗收＋報告（完成）
    - 合成器新增 v6 prefix：BUBBLES_BY_PREFIX/CAPTIONS_BY_PREFIX 依新構圖逐格校準（每格註解臉區座標）；
      cover_crop 加 vy 參數，v6 P1 裁切帶上移 vy=0.40 保住帽頂。
    - 組版第一版：P1 旁白牌壓男孩帽（新構圖男孩居中）→ 牌移到左上空 x0.05-0.42；
      P5 泡寬不足致驚嘆號孤行 → 寬度改 x0.34。重組後整頁目視：六格氣泡（含尾尖）零臉部重疊。
    - 報告 `_build_v6_report.py` → `working_db/reports/comic_v6_photo_report.html`（867KB 自足內嵌）：
      v5.1↔v6 整頁 before/after、六格分格圖、特徵對照表、氣泡避臉表；本地伺服器＋瀏覽器截圖驗證通過。
    - commit＋push 至 main；交付 commit：`e68e7dc`。

43. 第 12 輪：用戶結構性回饋與解法立項（完成）
    - 用戶回饋：「跨格不一致、角色臉部被切，重複繪圖同樣問題仍在」——指出逐格 T2I 重抽
      必然再犯，要求先給解決方法。
    - 根因分析：① T2I 每格重新詮釋角色，文字鎖定無法像素級一致；
      ② 版面格位長寬比極端（P4 約 4.5:1）對 4:3 出圖強制 cover 裁切，臉部必被切。
    - 提出三方案：A 角色定裝＋去背合成（同一張定裝照裁切複用，構圖權回到 PIL，
      結構上保證一致且不切臉）／B 整頁單圖生成＋補字／C 漫畫 LoRA 微調。
      建議 A；用戶批准，指示給實施計畫。
    - 計畫四階段：① 角色定裝（審核制）② 背景板 ③ PIL 合成＋接觸影 ④ 整頁驗收＋報告。
    - 用戶硬性關卡：「角色定裝要先給我審核，我說可以才可以進行下一步」。

44. 第 12 輪 Phase 1 定裝生成（部分完成，待用戶審核）
    - 新腳本 `_gen_masters_v7.py`：男孩/龍A/龍B 白棚定裝（鎖定文案＋「與參考圖1同一角色」
      連鎖），姿態版以站姿為參考連鎖生成；已出：boy_stand、da_stand、db_stand。
    - da_stand 目視：紫玩具龍（金雙角、粉橙翼、奶油肚、金爪）一致，唯鼻尖多一根小角
      （與鎖定文案「雙角」不符）→ 已附註請用戶裁決保留/重出。
    - 用戶回饋：「男孩臉型我不喜歡，多作幾個給我選，要智慧勇氣有主角光環感」
      → boy_stand 否決；新腳本 `_gen_boy_variants_v7.py` 同裝四款候選：
      boy_v1 聰明參謀型 / boy_v2 無畏勇者型 / boy_v3 溫柔主角型 / boy_v4 靈動調皮型，
      全部 gemini-2.5-flash-image 直出（2:3 白棚）。
    - 交付審核對照頁 `_review_boy_variants.html`（四款並列＋氣質說明）。
    - 待辦：用戶選定 boy_vN 後，須把 `_gen_masters_v7.py` 男孩連鎖參考從 boy_stand 改指
      選定版，再生成 boy_crouch/boy_kneel/boy_side；龍A 三姿態、龍B 倚靠版連鎖生成；
      `_cut_masters_v7.py`（rembg 去背→裁 bbox→RGBA）尚未執行；全員定裝須再次送審。
    - 續：不依賴男孩人選的龍類定裝先補完——`_gen_masters_v7.py da_sniff da_cheer da_sit db_lean`
      （argv 名單過濾，避開男孩鏈）四張全部 gemini-2.5-flash-image 直出。
    - 目視：龍A三姿態與錨點一致（紫身深紫斑、雙金角＋額心小錐、粉橙翼、奶油肚、金爪）；
      小錐偏差連鎖遺傳到三姿態（併入用戶裁決項目）；龍B db_lean 石板藍長頸前彎、橙刺、
      粉耳、奶油肚、無翼，與 db_stand 一致。
    - 建立送審頁 `_review_masters_v7.html`（四區：男孩四選一／龍A四姿態／龍B兩姿態／否決對照），
      去背剪材以 `_cut_masters_v7.py`（rembg→bbox→RGBA）批次凍結，供整批送審。
    - 用戶審核回饋：「恐龍太橡膠感了」——定裝呈現軟膠/霧面質感，偏離收藏玩具亮面硬膠目標。
    - 處置：`_gen_masters_v7.py` 新增 MATERIAL 鎖定（PREMIUM COLLECTIBLE DESIGNER VINYL、
      HARD HIGH-GLOSS CLEARCOAT、銳利高光＋長條柔箱反射、關節細縫；明確 NOT rubber/matte/
      satin/squishy），DB_LOCK 去除 satin 字眼；刪除舊龍類六張（原始＋剪材），
      重出 da_stand/da_sniff/da_cheer/da_sit/db_stand/db_lean，錨點先行、姿態連鎖沿用。
    - 註記：早前 `_cut_masters_v7.py` 批次在 db_stand 剪材前中斷（未寫入即結束），
      無殘留檔案；舊剪材已隨刪除清乾淨。男孩四款剪材已完成且不受影響。
    - 用戶附圖指示：「用這圖片試做主角定裝，我再決定要不要取代原本的小朋友主角」
      ——附圖為成年探險家（橄欖綠夾克、背包＋睡袋卷、手持野外日誌，神廟遺跡背景）。
    - 處置：參考圖存至 `_raw/_masters/_refs/man_ref.png`；新腳本 `_gen_man_masters_v7.py`
      以附圖為錨點參考生成 man_stand，蹲／跪／側身捧物三姿態連鎖（與男孩組同款分工，
      供直接對位替換）；真人寫真鎖定（85mm 雜誌級），非玩具材質。
    - 待辦：完成後與男孩四款並列送審，由用戶二選一主角。
    - man 四張直出（gemini-2.5-flash-image）。目視：man_stand/man_crouch/man_side 與附圖
      高保真（髮型、鬍渣、橄欖綠夾克、背包睡袋卷＋地圖筒＋繩圈、腰帶羅盤）；
      白底殘留仿浮水印字樣（TigerYang/192.168...，位於背景區，去背可去除，待驗證）。
    - 問題：man_kneel 初版違背白棚約束，地面畫成沙地（rembg 會連沙保留）
      → prompt 強化「地面同為白棚、NO sand/dirt/scenery」重出。
    - 去背 man_stand/man_crouch/man_side 執行中。
    - 用戶再次回饋：「恐龍太玩具感了」——亮面硬膠仍屬玩具範疇；指示先做幾個不同皮膚質感的
      同一動作恐龍，確定皮膚後再定裝動作圖。
    - 處置：新腳本 `_gen_skin_variants_v7.py`——以亮面版 da_stand 為造型/姿態參考，
      真實生物渲染（明確 NO plastic/vinyl/seams），四質感候選：da_skin_v1 爬蟲鱗片
      （乾燥顆粒鱗）、da_skin_v2 絨毛（幼獸短絨）、da_skin_v3 濕亮兩棲（濕皮水珠）、
      da_skin_v4 細絨羽毛（絨羽覆體）。選定後同款文字重出 da/db 全套定裝動作。
    - 併行：成年探險家 man 四姿態定裝已直出（man_kneel 白棚重出完成），去背進行中。
    - 用戶附「變體 gamecg：3A 遊戲 CG」參考圖（Pixar 級 CG 鱗片恐龍＋男孩海灘構圖），
      指示「用這恐龍皮膚試一張圖」。
    - 處置：參考圖存 `_refs/gamecg_ref.png`；`_trial_gamecg_skin.py` 單張試驗
      （男孩蹲下＋紫鱗龍嗅彩虹碎片、3A CG/PBR/統一晨光），gemini-2.5-flash-image 直出
      → `_raw/_trials/gamecg_skin_trial1.png`（4:3, 2.5MB）。目視：符合參考風格
      （細緻顆粒鱗片、金角漸層翼、男孩與龍共用暖光）。
    - 含義：皮膚質感四候選（da_skin_v1–v4）就此由用戶參考圖取代；若核准，
      定裝全套（男孩/龍A/龍B）改以 3A-CG 風格重出，方法A（定裝＋去背合成）不變。
    - 準備（不依賴用戶裁決）：送審頁升級第 3 版——併入成年探險家四姿態（去背完成）、
      3A-CG 試驗圖待核准區、皮膚質感歷程對照；決策清單改為兩項（CG 皮膚核准與主角二選一）。
    - 預寫 `_gen_masters_cg_v7.py`：3A-CG 版定裝產線（PROTAGONIST=boy/man 一鍵切換、
      BOY_VIBE 對應 A-1..A-4 氣質；龍A 參考 gamecg_ref、龍B 借 db_stand 造型），
      用戶一核准即可全速重出全套 CG 定裝。
    - 狀態：等候用戶回覆兩項裁決；未核准前不生成、不進背景/合成（遵循審核關卡）。
    - 用戶裁決（兩項）：① 3A-CG 皮膚核准，恐龍定裝須參考遊戲中「伴伴」圖；② 主角＝成年探險家。
    - 伴伴特徵確認（game_db/assets/dinos_2/DFD-000_伴伴_2star.png）：亮紫身深紫斑、金琥珀大眼、
      雙金角＋鼻尖金角、頸背尾金錐刺一排、粉紅大內耳、翼膜粉橙漸層帶斑、奶油肚與下顎、
      金爪、笑露小白牙粉舌、細緻鱗紋、Q 版比例。複製至 `_refs/banban_ref.png`。
    - `_gen_masters_cg_v7.py` 定案：PROTAGONIST="man"、DA_CG 重寫為伴伴特徵（鼻尖金角列為正典）、
      龍A錨參考改 banban_ref；全速重出 cg_da×4 / cg_db×2 / cg_man×4 共 10 張。
    - CG 十張直出。目視驗收：cg_da 四姿態全部忠於伴伴設計（細鱗、金雙角＋鼻角、漸層翼、
      奶油肚、Q 版比例）✓；cg_man 四姿態裝備/臉型連鎖一致 ✓
      （cg_man_kneel 手下一小塊土，去背時留意）。
    - 問題：cg_db 兩張被舊亮面膠參考圖帶回「塑膠玩具感＋關節縫線」，且 db_lean 頸部
      未俯低 → 修正：參考改 cg_da_stand（僅借 CG 質感）、DB_CG 加反玩具條款、
      db_lean 姿態文字強制「頸下彎至膝高」；重出中。
    - cg_db 重出驗收：cg_db_stand / cg_db_lean 改參考 cg_da_stand ＋ 反玩具條款後直出 OK，
      頸部已下彎、CG 細鱗質感統一 ✓。十張 CG 定裝全部到齊。
    - 去背：`_cut_masters_v7.py` 完成全部 10 張（cg_da×4、cg_db×2、cg_man×4），
      `_raw/_masters/` 已齊（lean 751×931、stand 763×980 等）。
24. 全篇漫畫分鏡腳本報告（完成，2026-10-23）
    - 用戶指示：「將故事由序章到終章的每一個漫畫劇情詳細寫出來並帶有對話，登場的角色
      也都要說明，每一篇漫畫大約5張漫畫（每張6格），漫畫格可以像電影分鏡，做成一個html報告」。
    - 結構定案：方案A 骨架 × 成年主角雷恩；9 篇（序章＋七篇＋終章）× 5 頁 × 6 格＝270 格；
      15 遊戲章節併入 7 中篇（平原+草原+丘陵／森林+沼澤／峽谷+雪嶺／遺跡+神殿／巔峰+龍穴／王陵+海宮）。
    - 產出 `working_db/reports/comic_full_storyboard_report.html`（單檔、繁中）：
      分鏡標記圖例、全篇總覽表（碎片進度 0→15/15）、目錄、角色圖鑑
      （雷恩/伴伴/薩爾塔附 CG 去背定裝圖；格雷/雷鐸文字卡）、篇章嘉賓速查表、
      每格「鏡位＋畫面＋對話/旁白」、每篇末鉤子、附錄（隊規三條出處、名場面 9 則、
      視覺母題與羅盤三拍子儀式、Method A 落地銜接說明）。
    - 第一篇沿用試閱章定案對白（嗅嗅/撿到/先發現/最氣派沙堡/挖到了/分你一半/隊規第一條）。
    - 驗證：python 結構檢查（270 panel、9 issue、9 hook、3 圖引用、閉合標籤）✓；
      本地 http.server 200；瀏覽器開啟無本頁 console 錯誤，
      3 張角色圖全部載入（naturalWidth>0）✓；抽檢第六篇與文末附錄截圖排版正確 ✓。
- 交付：commit `2707df7`（報告＋工作日誌＋CG 定裝／去背管線腳本），已推送 main。

## 待辦（下一階段）
- 角色定裝審核（使用者硬性關卡）：更新 `_review_masters_v7.html` 為 v4 版，展示 10 張 CG 定裝（雷恩×4、伴伴×4、薩爾塔龍×2）供審核；獲准後才進入背景生成與去背合成（第二～四階段）。
- 送審頁更新為第 4 版：`_review_masters_v7.html` 展示 10 張定稿 CG 定裝（雷恩×4、伴伴×4、薩爾塔龍×2，已去背），標注定案依據（3A-CG 皮膚＋成年探險家）與待裁決關卡說明。
  驗證：HTTP 200；瀏覽器載入十張圖全部成功（naturalWidth>0）✓；截圖排版正確 ✓。
- Phase 2 前置準備（不觸發生成，待命裝核准）：新寫 `_gen_bgs_v7.py`——第 1 話 4 張 4:3 空景背景（bg_beach_wide 日出沙灘大遠景含補給箱／bg_sand_close 沙地近景／bg_sandcastle 氣派沙堡／bg_sunset_glow 夕陽逆光），3A-CG 風格鎖、鏈式參考維持色調、無角色無文字；`py_compile` 通過。使用者回覆「可以」後才執行。
- Phase 3 前置準備（不執行合成，待命裝核准）：新寫 `_compose_v7.py`——方法A 合成器，2×3 直排版 1826×2236；每格 cover_crop 背景後依 PANELS 規格貼去背定裝（縮放/翻轉/底部錨定/腳底軟陰影），P3 薩爾塔項鍊光點、P4 沙上圓圈、P6 掌心碎片光以程式繪製；對話泡沿用 v5/v6 圓角/爆裂泡（位置為預估值，首跑後依實圖校準，硬規則：泡與尾不蓋臉）；P1 旁白、P6 隊規銘牌；`py_compile` 通過。
- 交叉引用檢查：`_compose_v7.py` 引用的 9 張定裝（cg_da_sit 為備用未引用）全部存在於 `_raw/_masters/`；合成器引用的 4 張背景名與 `_gen_bgs_v7.py` 產出名完全一致，無缺漏無歧異。
- 合成器加 `--check` 乾跑模式（不合成，只驗證 PANELS 引用資產）：實跑結果——定裝/字型無缺漏、背景 4 張正確列出待 Phase 2 產出，exit 0；`py_compile` 通過。

## 全角色定裝（流水號制，2026-10-23 使用者新指令）
- 指令：所有登場角色都要做定裝圖，動作須參考劇情；每角色 6–20 張；全部編入 _review_masters_v7.html；每張帶流水號，之後用流水號指認重做。
- 名冊（依全篇分鏡腳本報告）：核心班底 5 角色（雷恩/伴伴/薩爾塔龍/格雷/雷鐸）＋篇章嘉賓 19（小三角龍、三角龍媽媽、無齒翼龍媽媽、似鴯鶓龍三兄弟、腫頭龍、樹息龍、小美頜龍、棘龍、掘龍、食肉牛龍警長、艾伯塔龍、竊蛋龍盜團、風神翼龍三姊妹、超帝王龍、霸王龍、棘龍王、敦煌龍商隊、海霸龍、蛇頸龍）。
- 產線：`_gen_cast_v7.py`（核心班底 42 流水號，既有 10 張編 001–010，新動作 011–042，已全數生成成功）；`_gen_guests_v7.py`（嘉賓 043–156 分 A/B/C 批，每隻 6 張、物種特徵文字鎖定＋3A-CG 質感）；流水號→檔案對照 `_cast_manifest.json`；送審頁改由 `_make_master_review.py` 依 manifest 自動產生（第 5 版）。
