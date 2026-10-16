# 圖片生成工具指揮力評估（image-gen-tools-survey）

- Date: 2026-10-15
- Task ID: image-gen-tools-survey

## 需求

使用者要求重新評估我在本環境可指揮（含付費）的圖片生成工具，並說明各工具特色，作為後續恐龍圖批量生成的選型依據。

## Step-by-step record

1. 金鑰掃描：環境變數（LEONARDO／OPENAI／STABILITY／REPLICATE／FAL／HF／IDEOGRAM／RECRAFT／BFL／GEMINI 等 19 個常見名稱）全部不存在；無 `.env`／`.netrc`；金鑰內容一律不輸出。Result: 目前唯二憑據 = 本機 Gemini 金鑰檔（`_gemini_key.txt`，前輪已驗）與無需金鑰的 pollinations。
2. Gemini 複驗：以金鑰打 `GET /v1beta/models` → HTTP 200，帳號可見 6 個圖像模型（gemini-2.5-flash-image、gemini-3-pro-image(-preview)、gemini-3.1-flash-image(-preview)、gemini-3.1-flash-lite-image）。圖像生成仍被免費層 limit=0 計費牆擋住（前輪 8 模型全 429 的結論不變），開通 Google Cloud 計費即可解鎖。Result: 差一步即可用，參考圖生圖為其最大特色。
3. pollinations 實測：flux 256×256 測試圖 HTTP 200、18 KB、2.7 秒；但 `/models` 端點回傳僅 `["sana"]` 不可靠（flux 實測仍可用）。Result: 免費保底通道持續有效。
4. Leonardo 狀態：受控瀏覽器造訪 `app.leonardo.ai/library` 仍導向 `/auth/login`（Cloudflare turnstile 驗證運作中）→ 網頁操作路徑維持「待使用者在受控瀏覽器登入」；API 路徑維持「待付費 API 方案金鑰」。Result: 兩條路皆就緒待鑰／登入。
5. 報告產出：`image_gen_tools_report.html`（repo root，自包含、繁體中文），含總覽表（工具×可否指揮×啟用條件×參考費用×恐龍批量適合度）＋9 個工具特色詳述＋建議順序（Gemini 開通計費 → Leonardo 登入/API → OpenAI/fal → pollinations 保底 → 本機 ComfyUI 長遠）＋本機狀態快照。Result: 交付完成。
6. 驗證：`python -m http.server 8767` 起服，`curl` 報告 HTTP 200（13,396 bytes），內容探針（pollinations/Gemini/Leonardo/gpt-image-1/ComfyUI/Midjourney/總覽表/建議順序）全部命中；伺服器已停止、端口已釋放。Result: 驗證通過。
7. 未產生任何付費調用；金鑰檔維持未追蹤。既有管線腳本（`_gen_gemini_test.py`、`_gen_leonardo.py`、`_gen_ai.py` 等）保持原樣未動。

## Final status

- Status: Complete — 工具指揮力評估報告已交付（image_gen_tools_report.html），金鑰掃描與 pollinations/Gemini/Leonardo 三端點實測完成；後續待使用者選定啟用路徑
- Commit hash: a4f6286
