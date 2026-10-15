# Worklog: fix-game-video-sign

- 任務：修改 `assets/game.mp4` 結尾。原結尾為木牌上出現亂碼標題（CUNGHY WORESS）。
- 日期：2026-10-15
- 任務 ID：fix-game-video-sign

## 需求演變

1. 原始需求：修改影片內容（問句），先評估可行性。
2. 第一版方向：把亂碼標題蓋成「恐龍快找」Logo（疊加在木牌上）。過程中發現 Logo 透明縫隙會漏出原文字殘影、色階遮罩會誤判場景中的龍角與木牌邊緣。
3. **使用者變更需求（2026-10-15）**：「把木板出現畫面拿掉，把 game_logo 放大成影片大小（logo 比例要維持），再如之前，慢慢縮到遊戲首頁左上方」。改為移除整段木牌場景，以 Logo 縮放動畫取代。

## 最終做法（依變更後需求）

- 影片規格：768x768、24fps、158 幀（約 6.58 秒），H.264 + AAC（音軌完整保留）。
- 第 0–109 幀：保持原畫面（蛋孵化 → 小恐龍 → 叢林）。
- 第 110–157 幀：移除木牌場景，改用第 104 幀（乾淨的叢林小恐龍特寫）作為凍結背景，疊加 Logo 動畫：
  - Logo 以滿版置中出現（高 768px，寬依原始比例 1264:843 約 1152px，完整覆蓋畫面），前 4 幀做淡入。
  - 以 smoothstep 緩動在 48 幀（2 秒）內縮小並移向左上方。
  - 終點尺寸 160px 高、左上角留邊 28px，模擬遊戲首頁左上角 Logo（`#menu-logo` 寬 186px 的視覺比例）。
- 音訊：用 imageio-ffmpeg 提供的 ffmpeg，將原始音軌直接複製併入新檔。

## 步驟記錄

1. 確認影片資訊：768x768、24fps、158 幀，含 AAC 音軌；環境無系統 ffmpeg，有 OpenCV 5.0.0；以 `pip install imageio-ffmpeg` 取得 ffmpeg 7.1（含 libx264，可保留音軌）。原始檔備份到 repo 外 `C:/tmp/game_orig_backup.mp4`。
2. 抽幀分析內容：0–106 蛋/小恐龍；107–109 小恐龍奔跑（轉場模糊）；110 起木牌亂碼標題縮放入場；117–157 靜止招牌＋光點。
3. 依變更後需求重製結尾：寫 `tmp_scan/render_final.py`，OpenCV 逐幀解碼，0–109 原樣輸出，110–157 以第 104 幀為背景疊加 Logo 縮放動畫（smoothstep、滿版→160px、置中→左上角 28px、4 幀淡入），BGR rawvideo 經 pipe 送 ffmpeg 編 H.264 (CRF 18) 並 `-c:a copy` 併入原始音軌。
4. 渲染完成：158 幀全部寫入，ffmpeg 正常結束。驗證 metadata：768x768、24fps、158 幀、6.58 秒，H.264 影像 + AAC 音訊（32kHz stereo）。
5. 抽 keyframes 目視驗證：104（原畫面不變）、110（Logo 淡入滿版）、118/126/135/145（縮小過程）、157（終點：Logo 在左上角，比例正確無變形，無木牌無亂碼）。
6. 以新檔替換 `assets/game.mp4`（2.4MB）。
7. HTTP 驗證：`python3 -m http.server 8899` 後 `curl` 檢查，`/assets/game.mp4` 200（Content-Type: video/mp4，Content-Length 2,444,781），`index.html` 200。
8. 清理暫存：`tmp_scan/` 全部刪除。

## 結果狀態

- 驗證全部通過（metadata、keyframes 目視、HTTP 200）。
- 提交：<commit-hash>
