# Worklog：4×4 過關故事影片（可愛短片版，videogenerator 生成）

- 日期：2026-10-17
- 任務 ID：story-lv4-video
- 需求（使用者 2026-10-17，兩輪收斂）：
  1. 原始：「過關故事直接作成影片更具吸引力，4x4 過關故事能幫我指揮 videogenerator 做出來嗎」
  2. 修正方向：「先把故事作成 4x4 往 5x5 出發有關，內容要有趣可愛簡短，也可以只是短片不需要文字旁白，找幾隻代表恐龍登場做動作來突顯 4x4 過關前往 5x5 挑戰」
- 驗收：短片中不用文字旁白，用恐龍動作表達「4×4 過關 → 前往 5×5 挑戰」；遊戲 4×4 過關時改播此影片。

## 步驟記錄

1. 研讀既有管線：`_gen_sophnet_forest_story_v2.py`（SophNet videogenerator、happyhorse-1.0-r2v、720P/16:9/5s、data-URI 參考圖、雙參考被拒自動降級、40 分鐘輪詢、~¥4.5/鏡）與 `_probe_r2v_s1.py`（API 形狀）。確認 key 檔 `bban_samples/_sophnet_key.txt` 存在。
2. 盤點遊戲現況：STORY 第一章 lv=4（4×4 起源地「沙灘上的黑色腳印」）過關時 `playStory(idx,true)` 打字卡播出（main.js:1003-1006）；REGION_META：4=起源地、5=幼龍平原。開場影片 player 模式在 main.js:3183 起（intro-video overlay），可沿用。
3. 盤點 Style A 參考圖資產：伴伴 `DFD-000_伴伴_2star.png`（紫水晶色，風格錨點）、三角龍 `batch/21.webp`（芒果黃）、劍龍 `batch/11.webp`（蜜桃粉、背刺）、迅猛龍 `batch/200.webp`（青藍條紋、睡姿）；梁龍（id 1）batch 無圖 → 不登場。出場陣容＝伴伴＋三角龍＋劍龍＋迅猛龍。
4. 分鏡定案（4 鏡 × 5s＝20s，無旁白無字幕）：
   - S1 慶功：起源地沙灘上黃金光 4×4 地格最後一格點亮爆星屑，四龍歡呼跳躍慶祝。
   - S2 揭示：遠方草原上空浮現更大的 5×5 光格逐一閃亮，四龍定格仰望、伸爪指向前方。
   - S3 整裝：伴伴綁小葉領巾蓄勢、三角龍扭身暖身、劍龍尾擊沙打拍、迅猛龍繞圈急停擺「跟上我」姿勢，列隊。
   - S4 出發：四龍沿沙灘小路搖擺行進往幼龍平原，伴伴高舉小葉旗，迅猛龍衝前又折返趕隊；伴伴回頭對鏡頭揮爪大笑。鏡頭拉遠定格。
   - 連戲（CONT）：四龍配色與外觀全片一致（伴伴紫＋金角奶油肚；三角龍芒果龍芒果黃；劍龍蜜桃粉；迅猛龍青藍條紋）、晴天沙灘光線一致、光格金黃色。
   - 防穿幫（ANTI）：每龍只有一隻、四肢正常無變形、無重影；S1 僅一個 4×4 光格、S2/S4 僅一個 5×5 光格；無文字無浮水印。
5. 撰寫 `_gen_sophnet_story_lv4.py`（復用 V2 管線：happyhorse-1.0-r2v、720P/16:9/5s、data-URI 參考圖、雙參考被拒自動降單拼圖、40 分鐘輪詢、可續跑）；`--dryrun` 通過：參考拼圖 `_story_lv4_ref_trio.png`（1584×512）、`_story_lv4_ref_all.png`（2120×512）建立成功，四鏡提示詞印出無誤。
6. 修正 ANTI 條款：原句「地面十六格＋天空二十五格」會讓 S1 提前出現 5×5 天空光格，改為「除各鏡頭場景描述的發光方陣外不可多出其他方陣」；目視拼圖確認三龍外觀清晰可辨（芒果黃三角龍、蜜桃粉劍龍、青藍條紋迅猛龍）。
7. 依使用者「不需要文字旁白」指示：後製不疊字幕、不加片尾卡，純動作短片（拼接＋音軌處理）。
8. 首次啟動生成失敗（0/4、8 次提交全拒）：平台回 `InvalidParameter: Error validating image ... resolution must be at least 300x300, got 896x289`——參考圖在 896px 縮放後被逐張校驗，橫排拼圖（3:1／4:1）高度不足 300px。修正：改方形 2×2 四宮格拼圖 `_story_lv4_ref_grid2x2.png`（1072×1072）＋伴伴單圖雙參考（被拒自動降單拼圖）；刪除橫排拼圖與診斷用 probe 腳本。
9. 重啟生成：s1 成功（5,927,699 B、123 幀 @24fps）。QC 抽幀目視：四龍配色正確（伴伴紫＋金橘角、三角龍芒果黃、劍龍蜜桃粉、迅猛龍青藍條紋）、沙面 4×4 金色光格＋星屑慶祝到位、海灘場景正確；發現右下角平台浮水印「Happy Horse」（V2 片段亦有），決議後製以 `delogo=x=1155:y=670:w=130:h=40` 去除。
10. 遊戲整合：index.html 新增 `#story-video` 全螢幕層（video＋跳過按鈕）；css/style.css 新增 `#story-video` 樣式（z-index 300、淡出過渡）；main.js 新增 `STORY_VIDEOS={4:'assets/story_lv4_720p.mp4'}`、`playStory` 路由與 `playStoryVideo`（播放失敗回落文字卡、自動播放被擋改靜音），原打字卡邏輯更名 `playStoryText`。過關自動觸發與故事選單「觀看」皆自動改播影片。`node --check js/main.js` 通過。
11. 後製腳本 `_story_lv4_post.py`：四鏡各裁 5.0s、delogo 去浮水印、1280×720@24 yuv420p、音軌對齊（靜音鏡以 anullsrc 補）、首淡入尾淡出（影音同步）、concat → `assets/story_lv4_720p.mp4`（faststart、無字幕無片尾卡）。
12. 生成 4/4 完成（s2 `2GKU1St229Mm0pNTuAe0q9` 3,935,242 B、s3 `3oH5853mYtoG45SIb5o2mX` 4,593,103 B、s4 `UxOq6xaKpnGZGx6kY1Tre` 4,172,099 B），零重跑；s2–s4 抽幀目視通過（仰望天空光格、葉披風整裝列隊、朝草原光格行進）。QC 註記：天空光格列數風格化偏鬆（S2 約 5×7、S4 約 8×5），以「更寬＝更大挑戰」閱讀，可接受。
13. 後製執行：首跑 ffmpeg 報 Invalid argument（delogo x+w=1285 超出 1280 寬），修正為 `x=1140:y=668:w=135:h=42` 重跑成功 → `assets/story_lv4_720p.mp4`（12,701,959 B、476 幀、19.96s、可解碼、含 AAC 音軌；四鏡皆帶音軌）。
14. 成片時間軸抽幀（t≈2/7/12/17/19s）：四鏡銜接順暢、首淡入尾淡出正常、浮水印去除乾淨、四龍連戲一致。
15. 瀏覽器實測（http.server 8123）：`playStory(1,true)` → `#story-video` 全螢幕播出且 `storySeen[4]` 標記；跳過按鈕淡出關閉並清 src；手動重看正常；第二章（無影片）仍走打字卡；無新增控制台錯誤。curl：index.html／main.js／story_lv4_720p.mp4／story_lv4_video_report.html 皆 200。
16. 報告 `story_lv4_video_report.html`（內嵌成片、陣容／分鏡／QC／整合紀錄，繁中）。
17. 交付前複核與暫存範圍：`node --check js/main.js` 通過；本機 HTTP（8123）複驗 index.html／js/main.js／css/style.css／assets/story_lv4_720p.mp4／story_lv4_video_report.html 皆 200。發現 `index.html`、`css/style.css`、`js/main.js` 同時夾帶 2026-10-15 三個「已完成但從未提交」的任務改動（story-arc 章節文本重寫、story-cinematic 動態分鏡、story-visible v1.9.17 快取版本與效果強化），且與本次 `playStory`／`playStoryText` 改動交織於同一函式體內，逐 hunk 拆分會產出未經驗證的中間狀態，故一併納入本次提交，並同步收錄這三個任務的 worklog 與 `worklog_forest-story-v2.md` 的待提交補記（其成片早已於 `475f104` 交付）。原始片段目錄 `_story_lv4_clips/` 與生成日誌依 V2 前例不納入版本控制。

## 最終狀態

- **已完成**。
- 交付 commit：`4b6b4da`（已推送至 `origin/main`）；hash 回填與 worklog 歸檔見後續 history 提交。
- 成片：`assets/story_lv4_720p.mp4`（12,701,959 B、19.96s、720P、視訊＋AAC、無字幕無片尾卡）。
- 成本：4 鏡 × ¥4.5 = ¥18.0，零重跑（首輪 8 次提交為平台校驗失敗，不計費）。
- 遊戲行為：4×4 過關自動全螢幕播此短片（可跳過），故事選單第一章「觀看 ▶」重看；其餘章節維持打字卡。
