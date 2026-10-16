# Worklog：intro 影片生成器改為 R2V 版

- 日期：2026-10-16
- 任務：把 `assets/dinos_2/bban_samples/_gen_sophnet_intro_video.py` 從 `happyhorse-1.0-t2v` 改為 `happyhorse-1.0-r2v`（固定角色參考圖），並實跑驗證角色一致性。
- 動機：t2v 每次分段呼叫都重新「發明」伴伴，導致各分段角色長相不一致；森林故事管線已用 r2v + 固定參考圖驗證過此解法。

## 步驟記錄

1. 從已交付的 `assets/intro_bban_hide_720p.mp4`（123 幀 @24fps）抽出四個候選參考幀（p30/p50/p68/p85）到 `C:/tmp/fs_check/` 逐一目視評估。
   結果：p30 被蕨葉遮擋、p85 為站姿張嘴；p50 與 p68 為清晰全身三四分視角，選定 p68。
2. 裁切 p68 去掉右下角「Happy Horse」平台浮水印並框出伴伴主體（crop box 250,205,935,712 → 685×507），目視確認無浮水印殘留。
   結果：存為 `assets/dinos_2/bban_samples/_intro_bban_ref.jpg`（94,810 B）。裁掉浮水印是為了避免浮水印文字被 r2v 帶進新影片。
3. 改寫 `_gen_sophnet_intro_video.py`：
   - `MODEL` 改為 `happyhorse-1.0-r2v`；新增 `REF = HERE / "_intro_bban_ref.jpg"`。
   - 新增 `REFBIND` 身份綁定句（參考圖即伴伴本尊，花色／體型／五官不得更換），前置到每個 shot 提示詞。
   - 新增 `data_uri()`（≤768px、JPEG q86 base64），與森林故事管線同形狀。
   - `main()` 的 content 改為 `[text(REFBIND+shot)] + [image_url(role=reference_image)]`。
   結果：`python -m py_compile` 通過；匯入模組實跑 `data_uri(REF)` 得到 109,407 字元 data URI，前綴 `data:image/jpeg;base64,` 正確。
4. 實跑驗證：`python _gen_sophnet_intro_video.py 2`（輸出 `assets/intro_bban_hide_s2_720p.mp4`，不覆蓋已交付的 single 成片）。
   結果：submit 成功，task_id `1F9SylbIkgVCf3MSDhXkn5`，輪詢回傳 `task_type: "R2V"` 確認走參考圖通道；14 次輪詢後 succeeded，下載 3,897,444 B（123 幀 @24fps、1280×720）。
   抽 25%/55%/85% 三幀目視驗證：a 幀＝躲蕨葉後對鏡頭比「噓」、b 幀＝噴嚏後側身僵住、c 幀＝心虛燦爛笑（小尖牙＋粉紅舌）搔頭，與 shot 2 分鏡吻合；三幀的紫紅鱗、奶油白肚、金橘分節雙角、背脊金刺、粉紅翼膜、金黃琥珀眼皆與 `_intro_bban_ref.jpg` 一致 → 角色一致性 PASS。
   備註：成片右下角仍有平台浮水印「Happy Horse」，為端點固定蓋章行為（與參考圖無關，參考圖本身已裁除）。

## 最終狀態

- 狀態：✅ 完成——腳本已改為 `happyhorse-1.0-r2v`＋固定參考圖，實跑 shot 2 驗證角色一致性 PASS；交付 commit hash 待回填。
- 產出：`_gen_sophnet_intro_video.py`（R2V 版）、`_intro_bban_ref.jpg`（去浮水印參考圖）、`assets/intro_bban_hide_s2_720p.mp4`（驗證片）。
- 成本：1 次 720P×5s 生成 ≈ ¥4.5。
- 後續：其餘 shot（single/1/3）日後重跑時自動繼承同一參考圖，分段角色一致性問題從管線層面解除。
