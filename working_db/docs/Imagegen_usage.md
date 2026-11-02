# ImageGen 使用筆記（本機實戰驗證版）

> 整理日期：2026-10-16 ｜ 內容來源：實際呼叫成功 + 官方 API 文件
> 本文件是「怎麼用」的速查記憶；情境報告見 `working_db/reports/styleA_spec_report.html` 與 `working_db/reports/styleA_phase2_report.html`，過程記錄見 git commit log。

本機可用兩條 AI 圖片生成管線，各自獨立：

| 管線 | 端點 | 金鑰 | 狀態 |
|---|---|---|---|
| **SophNet ImageGenerator** | `https://www.sophnet.com/api/open-apis/projects/easyllms/...` | 檔案 `working_db/generated_assets/dinos_2/bban_samples/_sophnet_key.txt`（86 字元 secret） | ✅ 已實測跑通（任務端點 qwen-image 純文字生圖；`/image-edit` Z-Image-Turbo 編輯） |
| **Gemini（雙參考配方）** | `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent` | 環境變數 `GEMINI_API_KEY` | ✅ 已實測跑通（多次） |

兩條管線共用同一套後製鍊與風格A 提示詞模板（見第 4、5 節）。

---

## 1. SophNet ImageGenerator（新工具，本次實戰打通）

### 1.1 金鑰陷阱（最大坑）
- 主控台金鑰**列表頁只顯示 `id`（22 字元），那不是可呼叫的 secret**；貼上它只會得到 `20012 APIKEY_ERROR`。
- 可呼叫的完整 secret 為 **86 字元**，**只在建立當下顯示一次**（keySetting 文件明確「請妥善保存」）。
- 現成可用金鑰已存於 `working_db/generated_assets/dinos_2/bban_samples/_sophnet_key.txt`（已 gitignore），覆寫即換。

### 1.2 認證
- `Authorization: Bearer <金鑰檔案全文，含前綴、不換行>`
- 文件另有舊式 query `?apikey=`，實測不被接受 → 一律用 Bearer。

### 1.3 兩個端點、兩種回應格式（路由規則：用途決定端點）
**純文字生圖 → 任務端點（非同步）**——`/image-edit` 不吃純文字（prompt-only 一律回 `10012`）：
- 建立：`POST {BASE}/imagegenerator/task`，body `{"model":"...","input":{"prompt":"...","negative_prompt":"..."},"parameters":{"size":"1328*1328","seed":231,"watermark":false}}`
- create 回 `{"output":{"taskId","taskStatus":"PENDING"}}`；查詢 `GET {BASE}/imagegenerator/task/{taskId}`，每 5 秒輪詢；SUCCEEDED 後結果在 **`output.results[]`**（每項 `{url, width, height, content_type}`，OSS 預簽名，下載別拖太久）

**圖片編輯（需參考圖）→ 同步端點**：
- `POST {BASE}/image-edit`，body 必帶 `input.images: ["http://..."]`（公網 URL 直餵，GitHub Pages percent-encoded 中文檔名實測 OK）
- 結果在 **`output.choices[0].message.content[0].image`**（URL 字串）

### 1.4 模型可用性（會浮動，每次使用前重新探針）
- 2026-10-16 上午：qwen 系全不可用（任務端點 `20011`、`/image-edit` 上 `20037`）；`Z-Image-Turbo` 唯一可用（`/image-edit` 編輯，約 ¥0.25/張，但傾向重設 prompt、不保留參考圖風格）
- 2026-10-16 下午：**`qwen-image` 任務端點可用**（1328×1328、seed/watermark 照收、約 30–60 秒 SUCCEEDED）；`Qwen-Image-Plus` 仍 `20011` 未部署
- 大小寫變體部署不同步（`qwen-image` 可用≠`Qwen-Image` 可用），同模型隔天也可能變 → 每次花錢前先探針

### 1.5 錯誤碼速查（實測對照）
| code | message | 含義 |
|---|---|---|
| 10012 | ILLEGAL_REQUEST_PARAMETERS | 參數不合法（**能收到它＝認證已過**） |
| 10022 | USER_BAD_BEARER_TOKEN | Bearer token 壞掉 |
| 10025 | USER_LOGIN_REQUIRED | 沒帶 / 帶錯金鑰 |
| 20011 | NO_AVAILABLE_DEPLOYMENT | 模型未部署／無可用實例 |
| 20012 | APIKEY_ERROR | 金鑰無效（拿到 22 字元 id 時就是它） |
| 20037 | 图像生成失败 | 模型生成本身失敗 |
| 20204 | 资源不存在 | 路由不存在 |

### 1.6 免費探針（花錢前先驗證金鑰與模型）
`curl -X POST "$BASE/image-edit" -H "Authorization: Bearer $(cat _sophnet_key.txt)" -H "Content-Type: application/json" -d '{"model":"<模型>","input":{}}'`
- 回 `10012` → 認證通過、模型已部署，可放心送正式 prompt
- 回 `20012` → 金鑰問題；回 `20011` → 這模型現在不能跑
- **判讀陷阱**：prompt-only（缺 `images`）也回 `10012`，與空 input 同訊號 → `/image-edit` 探針通過只證明「認證＋已部署」，**不能證明生圖模式可用**；任務端點是否真可跑需短 prompt create 一次（會計費 ~¥0.25，棄單也燒錢）

### 1.7 現成腳本
- 任務端點版：`working_db/generated_assets/dinos_2/bban_samples/_gen_sophnet_styleA_stegosaurus.py`（已跑通流程，含兩種回應格式解析）
- 記得腳本要設 `User-Agent: Mozilla/5.0`（沒帶會 422）；輸出中文時 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` 避開 Windows cp950 炸掉

---

## 2. Gemini 雙參考配方（本機主力，穩定可用）

- 端點：`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=$GEMINI_API_KEY`
- 模型階梯：`gemini-2.5-flash-image` → `gemini-3-pro-image`（或更新）；額度見 https://ai.google.dev/gemini-api/docs/rate-limits?hl=zh-tw
- 配方（AGENTS.md 認證）：
  - IMAGE 1 = **風格參考**：`game_db/assets/dinos_2/DFD-000_伴伴_2star.png` 壓白底、縮 ≤1024px → base64 `inline_data`
  - IMAGE 2 = **物種解剖參考**：該恐龍還原圖
  - prompt 明確分工：「IMAGE 1 只取風格質感…IMAGE 2 只取解剖特徵」
- 現成腳本：`working_db/generated_assets/dinos_2/bban_samples/_gen_gemini_styleA_stegosaurus.py`（含 `as_ref()` 壓白底 + base64 封裝）

---

## 3. 兩條管線比較

| | SophNet | Gemini |
|---|---|---|
| 優點 | 便宜（約 ¥0.25/張）、有 key 檔即跑、任務端點支援負向詞/seed | 品質穩、真懂雙參考（風格A 還原度高）、模型新 |
| 缺點 | 模型部署浮動；純文字模式無視白底指令、擬人先驗強；`/image-edit` 編輯會放大擬人；需自管金鑰 | 有每日免費額度上限、風格一致性靠配方 |
| 何時用 | 便宜備援／實驗線（出圖前先套第 9 節清單校正提示詞） | 要品質、走風格A 正式資產 |

---

## 4. 共用後製鍊（成品規格）

raw → **rembg 去背** → alpha-bbox 裁剪 → 方形畫布（水平置中、底部留 4% 邊距＝底部貼齊）→ 512×512 LANCZOS → RGBA PNG + WebP(q90)

驗收基準（劍龍實測）：
- 尺寸 512×512 RGBA、白底殘留 ≤0.03%（劍龍 0.02–0.03%）
- WebP(q90) 約 51KB、底部貼齊
- 現成腳本：`working_db/generated_assets/dinos_2/bban_samples/_post_styleA_stegosaurus.py`（Gemini 與 SophNet 共用）

---

## 5. 風格A 提示詞模板

正向（英文，結構：風格基底 + 該物種解剖 + 物種主色 + 共用家族特徵 + 體態/動作 + weathering + 背景）：核心句
`Cute chibi 3D toy-style render of a baby <SPECIES>, soft organic satin skin sheen ... big round golden-amber eyes with white specular highlights, cheerful open smile showing tiny white fangs and a pink tongue, creamy white belly. <SPECIES 主色>. <物種解剖：角/骨板/頭冠/背帆…>. Bright yellow-orange segmented horns/spikes/claws ... Natural weathering: subtle dirt smudges, small mud patches, tiny grass or leaf fragments ... Plain pure white studio background ... No text, no watermark.`

負向（中文固定清單，壓塑膠感）：
`塑膠感, 硬塑料光澤, 乙烯基玩具感, 強反光, 模糊, 低解析度, 變形, 多餘的肢體, 多隻動物, 文字, 數字, 浮水印, 簽名, 邊框, 背景雜物`

家族特徵（每隻都要）：金黃琥珀眼＋白高光、露小尖牙與粉舌的笑容、奶油白肚、黃橙角/爪/棘、weathering 髒污隨星級遞增。
物種識別：各物種給「一看就認得出」的專屬主色（劍龍＝青金石藍、牛龍＝緋紅）。
細長體型物種（腕龍、鐮刀龍、魚龍等）需「收攏體態」：尾捲回身側、脖子微彎、頭微低轉向身體，長寬比 ≤2:1。

---

## 6. 檔案索引

| 檔案 | 用途 |
|---|---|
| `working_db/generated_assets/dinos_2/bban_samples/_sophnet_key.txt` | SophNet 金鑰（gitignored，覆寫即換） |
| `working_db/generated_assets/dinos_2/bban_samples/_gen_sophnet_styleA_stegosaurus.py` | SophNet 任務端點生成器 |
| `working_db/generated_assets/dinos_2/bban_samples/_gen_gemini_styleA_stegosaurus.py` | Gemini 雙參考生成器 |
| `working_db/generated_assets/dinos_2/bban_samples/_gen_compare_backends.py` | 雙後端對照生成器（同提示詞、同 spec 列） |
| `working_db/generated_assets/dinos_2/bban_samples/_gen_sophnet_retry.py` | SophNet 擬人緩解重試（A 純文字強化／B /image-edit） |
| `working_db/generated_assets/dinos_2/bban_samples/_post_styleA_stegosaurus.py`（單張）／`_post_compare.py`（對照組） | 共用後製鍊 |
| `working_db/generated_assets/dinos_2/bban_samples/gemini_styleA_stegosaurus_512.webp` | 風格A 成品範例（512 tile） |
| `working_db/reports/styleA_spec_report.html` | 風格A 規格總集（批量生產規格、139 筆生成規格、批量替換審查、雙後端比較） |
| `working_db/reports/styleA_phase2_report.html` | 風格A Phase 2 批量成果（134 張過閘成品與部署紀錄） |

## 7. 一句話記憶
- SophNet：id（22 字元）≠ 可呼叫的 secret（86 字元，建 key 時才顯示）；Bearer 認證＋必帶 `User-Agent`；模型部署會浮動 → 先免費探針再花錢；**純文字生圖走任務端點（非同步輪詢），`/image-edit` 只收「有 images」的編輯任務**——收到 10012 先檢查路由與參數，別急著換模型。
- Gemini：`as_ref()` 壓白底當風格參考 + 物種照當解剖參考，品質最穩。
- 後製：rembg → 底部貼齊 4% 邊距 → 512×512 RGBA WebP(q90)。

## 8. 2026-10-16 下午追加實測（雙後端比較，見 `working_db/reports/styleA_spec_report.html`）

- **`/image-edit` 不吃純文字生圖**：prompt-only body 一律回 `10012`（與空 input 同訊號，探針判讀要小心）——純文字生圖必須走**任務端點** `POST .../easyllms/imagegenerator/task`。
- 任務端點 2026-10-16 下午實況：`Qwen-Image-Plus` → `20011` 未部署；**`qwen-image` 可用**（1328×1328、seed/watermark 參數照收，約 30–60 秒 SUCCEEDED）。
- 回應格式：create 回 `{"output":{"taskId","taskStatus":"PENDING"}}`；poll 回 `output.taskStatus`＋`output.results[].url`（OSS 預簽名）。
- qwen-image 風格A 適配度（同 spec 列 260、與 Gemini 同要素要求對照）：趣味動作/配件/污漬/金甲等「清單型要素」多能命中、剪影規則一次過；但 **2/2 無視純白背景指令**（出深綠桌面場景）、實體公仔攝影質感、臉部擬人化、解剖偶有漂移（多龍角）——數據閘能過但風格A 不像。
- 現成腳本：`working_db/generated_assets/dinos_2/bban_samples/_gen_compare_backends.py`（SophNet 任務端點＋Gemini 雙後端對照）、`_post_compare.py`、`_build_compare_report.py`。

### 8.1 擬人嬰兒臉緩解實測（同日重試，腳本 `_gen_sophnet_retry.py`）

- **根因**：qwen-image 無參考圖時，「baby + 大眼 + 笑容」觸發 baby-schema 擬人先驗；電商公仔產品照先驗解釋了深綠桌面背景；提示詞的家族特徵「pink inner ears」在純文字下被**字面化成粉紅大外耳**（人耳形狀）。
- **Variant A（純文字強化，seed 555001）**：插入爬蟲臉條款（reptile snout/nostrils/fangs/ear openings＋NO human face/ears/cheeks）＋負向詞加「拟人化, 人脸, 人类耳朵, 婴儿脸, 儿童」。結果：**擬人臉可救**（臉部回到爬蟲吻部）、剪影 0.95 全場最方正、後製 11 閘全過；但**白底 3/3 全部失守**（仍深綠場景），且 pink inner ears 仍長成外耳——該句在純文字模式下應整句移除。
- **Variant B（/image-edit 編輯模式，images=伴伴 2 星圖 GitHub Pages URL）**：參考圖可用公網 URL 直餵（percent-encoded 中文檔名 OK）。結果：**白底繼承成功**（halo 0.0366 全場最乾淨）、量化指標全過；但**擬人化反向加重**——演成人類嬰兒身體＋恐龍頭套，比純文字版更不像恐龍。
- **結論**：SophNet 走風格A 的最佳組合＝Variant A 路線＋移除 pink inner ears 句＋白底指令前置加重＋多抽選優；`/image-edit` 適合改風不適合控擬人。正式資產仍以 Gemini 雙參考為準，SophNet 定位為便宜備援線。

## 9. 未來使用須注意（教訓清單，2026-10-16 定稿）

### SophNet ImageGenerator
1. **路由先想清楚**：純文字生圖 → 任務端點（非同步輪詢）；`/image-edit` 必須帶 `input.images`。`10012` 有兩種成因（缺 images／參數不合法），先檢查路由與參數再怪模型。
2. **模型可用性每次重探**：部署浮動且大小寫變體不同步；免費探針只證「認證＋已部署」，任務端點真正可跑要花 ~¥0.25 短 prompt 才測得出（棄單也計費）。
3. **請求基本盤**：`Authorization: Bearer <86 字元 secret>`（建 key 當下只顯示一次，已存 key 檔）＋ `User-Agent: Mozilla/5.0`（沒帶 422）＋中文輸出先 `reconfigure(encoding="utf-8")`。
4. **白底指令無效**（qwen-image 純文字 3/3 失守，出深綠桌面場景）：要白底只能走 `/image-edit` 繼承參考圖底色（halo 全場最佳 0.037），但編輯模式會反向放大擬人化——兩者不可兼得，取捨前想清楚要哪個。
5. **擬人先驗強**：無參考圖時「baby＋大眼＋笑容」必出嬰兒臉——提示詞加爬蟲臉條款（reptile snout/nostrils/ear openings＋NO human face/ears/cheeks，見 `_gen_sophnet_retry.hardened_prompt()`）＋負向詞追加「拟人化, 人脸, 人类耳朵, 婴儿脸, 儿童」，並**整句移除 pink inner ears**（純文字下會字面化成粉紅大外耳）。
6. **定位**：清單型要素（動作/配件/污漬/金甲）命中率高、剪影規則服從，但攝影質感/背景/解剖會漂移——只當便宜備援線；真要用它出圖記得多抽選優＋過後製 11 閘。
7. **深色背景 raw 的後製代價**：rembg 後 halo 偏高（0.147 壓線 vs 白底 raw 0.037），閘門 `no_halo<0.15` 容易擦邊——寧可生成端就讓它出白底。

### 兩條管線共用
8. **跨後端提示詞≠同語義**：SophNet 版需移除參考圖字樣並改寫（`_gen_compare_backends.sophnet_prompt()` 的 4 處替換是現成範本，斷言 0 個 IMAGE 引用）；比較實驗務必同 spec 列＋每後端各抽 2 張留誤差餘裕。
9. **後製縮圖陷阱**：`_thumb_*_raw.png` 會被 `*_raw.png` glob 吃進後製鍊產生垃圾輸出＋假報告列——縮圖換命名或放別的目錄。
10. **參考圖供給**：本機檔案不能直接上傳 SophNet，用公網 URL（GitHub Pages 已驗證，percent-encoded 中文檔名 OK）；raw 圖下載要快（OSS 預簽名會過期）。

## 10. 2026-10-22 追加實測（API 已改版；漫畫人類角色變體測試）

### 路由與回應格式（與本文件 1.3 節不同，以此為準）
- **`/image-edit` 同步路由已死**：全模型 `20204 资源不存在`。生圖與編輯一律走任務端點
  `POST {BASE}/imagegenerator/task`＋輪詢 `GET {BASE}/imagegenerator/task/{taskId}`。
- **回應改包在 `output`**：create 回 `{"requestId", "output":{"taskId","taskStatus":"PENDING"}}`
  （舊文件的 `result` 包裝已不存在）；poll 的 URL 在 `output.results[].url`，
  失敗時整包回 `{"status":20037,...}`（HTTP 400/500，需先 `e.read()` 再解）。
  判斷「建立成功」要看 `output.taskId` 是否存在，別再比對 `result` 鍵。

### 模型可用性（2026-10-22 實況，又全變了）
- `Qwen-Image-Edit`／`Z-Image-Turbo-Edit`：**20030 不在型錄**（空 input 的 10012 只是名稱預檢，
  不能證明已部署）；`qwen-image` 系與 `Z-Image-Turbo`：20011 未部署。
- **`Wan2.6-T2I`（純文生圖）可用**：裸 input（prompt＋negative_prompt）約 1 分鐘 SUCCEEDED。
- **`Qwen-Image-Edit-2509`（編輯模型）可用但帶參數即死**：`input.images` 必帶（否則 10012
  「必须传入至少1张参考图片」）；一旦附 `parameters`（size/seed/watermark）create 直接
  HTTP 500 `20031 图片生成任务创建失败` → 只能送 `{model, input}` 兩層。
- 空任務會計費：探針留下的空 input 任務輪詢回 20037 失敗，錢照燒（~¥0.25/個）。

### 風格能力實測（人類寫實化測試，P2 同格四流派）
- **Edit-2509 會把整格統一 3D 卡通化**：「100% photorealistic live-action」指令完全被無視；
  參考圖鎖恐龍有效，但要「真人質感」別用它。
- **Wan2.6-T2I 對攝影流派指令有感**：photo（85mm 人像）有散景／真實陰影／膚質；
  paint（油畫）有全畫面筆觸；gamecg（3A CG）成 Pixar 級；film（電影實拍）只到動畫電影感，
  不到真底片——寫實度上限：photo > paint ≈ gamecg > film。
- 恐龍文字鎖定（無參考圖）在 Wan2.6-T2I 上四張全命中（紫身紫點／金角金爪／粉紫→暖橘漸層
  翅膜＋紫點／粉內耳／奶油肚），僅男孩年齡偏小（5–7 歲 vs 指定 10 歲）。
- 現成腳本：`working_db/generated_assets/comics/_gen_kidstyle_sophnet.py`
  （含 output 包裝解析、網路例外全捕、create 180 秒逾時＋重試）；成果報告見
  `working_db/reports/kid_style_variants_report.html`。

