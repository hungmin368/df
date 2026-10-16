# Worklog：以 R2V 版重新生成開場片（single）

- 日期：2026-10-16
- 任務：用已轉為 R2V 的 `_gen_sophnet_intro_video.py`（固定 `_intro_bban_ref.jpg` 參考圖）重新生成開場片 single 剪輯，要求畫面無穿幫、登場主角模型與參考圖一致不可變。
- 背景：舊 `assets/intro_bban_hide_720p.mp4` 為 t2v 版生成，角色外觀無參考圖鎖定；本任務以 R2V 重生成替換（舊版已入 git 歷史可回退）。

## 步驟記錄

1. 確認輸出目標：grep 全庫，`intro_bban_hide_720p.mp4` 的引用均在 `bban_intro_video_delivery_report.html`／`bban_intro_video_prompts_report.html`（報告頁），遊戲 index.html 未直接嵌入；single 剪輯即本腳本交付成品，確定覆蓋重生成。
2. 背景執行 `python _gen_sophnet_intro_video.py single`（R2V＋REFBIND＋固定參考圖；日誌 `_gen_intro_r2v_single_run.log`）。
   結果：第一次背景呼叫異常——log 0 bytes、無任何輸出即退出（未送出任務、無成本消耗）；改以前景重跑成功：task_id `2LXHmUf1xzeSosFRbAEkQV`，輪詢回傳 `task_type: "R2V"`，16 次輪詢後 succeeded，下載覆蓋 `assets/intro_bban_hide_720p.mp4`（新 4,658,232 B；舊 t2v 版 3,812,306 B 已在 git 歷史）。
3. 逐幀驗證：抽約 10 幀掃描穿幫（道具憑空出現/消失、肢體異常、臉部崩壞、亂碼文字）＋角色一致性（紫紅鱗、奶油白肚、金橘分節雙角、背脊金刺、粉紅翼膜、金黃琥珀眼）。
   結果：PASS。抽 5%~95% 共 10 幀（`C:/tmp/fs_check/regen_f01..f10.jpg`）：節拍完整依序為搜尋（f01-f02）→ 蹤影邊緣現身（f03）→ 被發現全貌（f04）→ 噴嚏蓄力與噴出（f05-f06）→ 噴飛蕨葉後心虛笑（f07）→ 撿網（f08）→ 舉網英雄姿勢＋比讚（f09-f10）；捕蟲網連續（地面 f04-f07 → 撿起 f08 → 手持 f09-f10）；蕨葉噴飛前後合理；四肢＋雙翼數量正常、臉部無崩壞、無亂碼文字；金橘分節雙角、背脊／尾脊金刺、粉紅翼膜、金黃琥珀眼、奶油白肚與 `_intro_bban_ref.jpg` 一致，全片同一角色模型無漂移。右下角「Happy Horse」浮水印為平台固定蓋章（非穿幫）。

## 最終狀態

- 狀態：✅ 完成——R2V 版 single 開場片重生成並通過逐幀驗證（無穿幫、角色模型一致）；交付 commit hash 待回填。
- 產出：`assets/intro_bban_hide_720p.mp4`（R2V 重生成版，4,658,232 B／123 幀 @24fps／1280×720）。
- 成本：1 次 720P×5s 生成 ≈ ¥4.5（第一次背景空跑未送出任務、無消耗）。
