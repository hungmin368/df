# Worklog：遊戲開場動畫（伴伴孵化・擬真森林）

- 日期：2026-10-16
- 任務 ID：intro-video

## 需求

使用者提供兩張 SophNet videogenerator 截圖（ellm_ key 的 `/videogenerator/task` + Wan2.2-T2V-A14B 範例；aigc_ key 的定價表 + `/videogenerator/generate` + happyhorse-1.0-t2v 範例），要求參考並製作遊戲開場動畫：**擬真、真實森林場景、主角撿到未孵化的蛋、捧在手上、蛋漸漸碎裂、伴伴嬰兒龍探出**。

## 需求變更（使用者，2026-10-16）

改為設計「**有趣搞笑、符合恐龍快找玩法、必須帶有伴伴、電影真實場景**」的開場影片提示詞。原「蛋孵→探頭」劇情由「捉迷藏快找」喜劇取代；並修正先前提示詞把伴伴寫成「翠綠色」的錯誤（2★ 定稿為紫紅色）。

## 步驟記錄

1. 建立任務計畫（key/端點確認 → 免費探針 → 腳本 → 生成輪詢 → 驗證報告）。
2. 讀取 `assets/dinos_2/bban_samples/_sophnet_key.txt`（前次任務留存的 86 字元 secret）。
3. 免費探針兩端點：
   - `/videogenerator/task` + Wan2.2-T2V-A14B：空 content 與空文字皆回 `20033 视频生成任务创建失败` → 此模型目前不可用（不花錢再試）。
   - `/videogenerator/generate` + happyhorse-1.0-t2v：空 content 回 `10012 ILLEGAL_REQUEST_PARAMETERS`（需要 prompt）→ **認證通過、模型可部署**，確認綠燈。
   - 定價（截圖）：720P ¥0.9/秒；5 秒 ≈ ¥4.5。
4. 檢查本機工具：無 ffmpeg，但 Python `cv2`/`imageio` 可用（影格抽取驗證用）；既有影片放在 `assets/` 根目錄（如 `game.mp4`），新作跟進此慣例。
5. 撰寫 `assets/dinos_2/bban_samples/_gen_sophnet_intro_video.py`：POST generate → result.task_id → 每 5 秒輪詢 GET {BASE}/{task_id}（上限 20 分鐘）→ 遞迴掃描回應中的影片 URL → curl 下載到 `assets/intro_bban_hatch_720p.mp4`。提示詞依 AGENTS.md 風格A 註冊表鎖定伴伴特徵（翠綠身體、金黃琥珀眼、奶油白肚），敘事四拍：森林光影→探險者捧起花紋蛋→蛋殼漸裂→嬰兒伴伴探頭眨眼。
6. 送出生成任務並輪詢——**本階段期間完成**（14:18 落地）：`assets/intro_bban_hatch_720p.mp4`（1280×720・24fps・123 幀・5.12 秒・2.7MB）；同日以 `_check_intro_frames.py` 抽 8 幀目視驗證通過，產出 `intro_animation_report.html`（規格／驗收對照／影格弧／原始提示詞／探針紀錄／已知限制：平台浮水印、寫實比例非 Q 版）。

7. 【第二階段】盤點遊戲玩法與設定：讀 `index.html` 玩法說明（分區藏隱藏物、✕ 排除標記、捕捉器、6×6 起沙漏計時、過關＝剩餘秒數、伴伴為 No.000 隨行夥伴）、`js/main.js` 序章「熄滅的第一盞星」與伴伴主線章節（最後一盞星燈的守護者、星願貝殼、額上星紋）、伴伴 2★ 圖（紫紅 #AF48DB／深紫斑點 #7818C0／金橘角爪 #E9901D／金琥珀眼 #F7A007／乳白腹 #F8EBEF／粉紅翼膜 #CD305C）。
8. 查出舊提示詞瑕疵：`_gen_sophnet_intro_video.py` 將伴伴寫成「翠綠色小恐龍」，與 2★ 定稿圖（紫紅色小龍）不符 → 本階段修正，並在提示詞中加入固定「角色規格卡」避免再飄移。
9. 設計新提示詞：「藏不住的伴伴」捉迷藏喜劇——單鏡萬用版（找→破功→捕捉器）＋三幕分鏡版（幕1 找／幕2 破功／幕3 捕捉器＋LOGO 留白），中英雙版＋負向詞＋技術參數＋後製建議（沿用 game.mp4 的「AI 文字必亂碼 → 後製疊 game_logo.png」教訓）。

10. 產出 `bban_intro_video_prompts_report.html`（10 節：概念與四項決策／玩法對照表／伴伴電影版規格卡＋色票／單鏡萬用版中英／三幕分鏡中英／備選笑點／負向詞中英／技術參數與成本／後製與音效建議／使用方式；提示詞框附一鍵複製）。
11. 同步改寫 `assets/dinos_2/bban_samples/_gen_sophnet_intro_video.py`：提示詞改為 `SHOTS`（single/1/2/3）＋argv 選擇＋動態輸出檔名（`assets/intro_bban_hide*_720p.mp4`），頭部註解加入角色規格卡與「翠綠色→紫紅色」修正說明。
12. 驗證：`python -m py_compile` 通過；模組匯入測試（不發任何付費請求）確認 SHOTS 四鍵齊全；`python -m http.server 8899` + curl 報告 200（25,762 bytes）；瀏覽器實際開啟報告，目視排版、色票、表格與複製鈕（自動化環境無剪貼簿權限時，按鈕正確退化為「請按 Ctrl+C」並自動選取文字）。

## Final status

- Status: In progress（提示詞設計完成；影片生成待執行）
- Commit hash: n/a
