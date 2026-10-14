# worklog_bundle-consistency-check

- 任務：檢查 `index.html`（多檔主線）與 `dragonfinder_v1.9.10.html`（單檔封裝版）內容是否一致
- 日期：2026-10-12
- Task ID：bundle-consistency-check

## 步驟紀錄

1. 確認 bundle 生成方式與來源：`build_single_file.mjs` 將 `css/fonts.css`、`css/style.css`、`js/data.js`、`js/tower.js`、`js/main.js` 與全部資產（webp／png／svg／woff2）內嵌為單一 HTML；bundle 頭部註解記載「生成於 2026-09-24、來源 commit `1aaa76d`」。
2. 以 git 歷史盤點 bundle 生成後動到網頁源碼的提交：`c3e4f50`（dinos_2 logo／資料更名；其工作區變更實際已含於 bundle）、`677f484`（2026-09-28 教學文案「為什麼那一格合理」）。
3. 權威比對：複製現行 `index.html`／`css/`／`js/`／`assets/` 與 `build_single_file.mjs` 至暫存目錄，以 `node build_single_file.mjs` 重建 bundle（0.9 秒、成功，無殘留資源引用），排除第 2 行生成註解後與現有 bundle 逐行 diff。
4. 結果：僅 **6 行對（6 個 hunk）**不同，全部位於內嵌 main.js 的教學區段；其餘（外層 HTML、fonts.css、style.css、data.js、tower.js、全部 base64 資產）**完全一致**。
5. 差異即 `677f484` 內容：`whyReveal()` 函式（`js/main.js:2612`，startDemo 前）＋ 5 處教學揭露文案（`js/main.js:2642／2663／2675／2711／2750`）；現有 bundle 完全不含（`grep whyReveal` 在 bundle 中 = 0，重建檔中 = 4）。
6. 量化佐證：重建檔 30,963,427 bytes vs 現有 bundle 30,962,268 bytes（+1,159 bytes）。

## 附帶事件（檢查期間發現）

- 工作區的 `unity_archive_pause_report.html` 一度自磁碟消失（`git status` 顯示 ` D`）；經查 `unity_archive_*` 兩個檔案已不在 repo，完整副本位於上一層目錄 `C:\MY_AI_JOBS\`。
- 已將 repo 內的 `unity_archive_pause_report.html` 以 `git restore` 還原至 `HEAD`（`66d3f5e`）版本；還原後內容與 `C:\MY_AI_JOBS\unity_archive_pause_report.html` 一致（忽略 CRLF/LF 差異，md5 同為 `f38bbcd6f2b56966eb62c41317855212`）。
- 複驗移出的封存檔：`C:\MY_AI_JOBS\unity_archive_20261012.zip` 大小 218,996,499 bytes（與封存完成時一致）；`7z t` 通過（95 資料夾、2,427 檔案、解壓後 689,791,282 bytes、Everything is Ok）。

## 最終狀態

- 結論：**內容不一致**——單檔封裝版落後一次更新（2026-09-28 教學「為什麼」文案，commit `677f484`）；除該 6 行外逐位元一致。
- 未重新生成 bundle、未變更任何檔案內容（暫存重建與比對檔已清理；`unity_archive_pause_report.html` 曾自工作區消失、已還原至 `HEAD`）。
- 產出：`bundle_consistency_report.html`；`worklogs/worklog_unity-archive-pause.md` 追加後記（封存檔新位置與複驗結果）。
- commit：（本 worklog、報告與上述後記尚未 commit，待確認）
