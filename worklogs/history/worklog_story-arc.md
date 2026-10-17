# DragonFinder 故事主線強化

- 日期：2026-10-15
- Task ID：story-arc

## 執行紀錄

1. 檢視 `AGENTS.md`、故事系統與區域設定。確認故事以 `js/main.js` 的 `STORY` 陣列管理，序章與第 4×4 至 18×18 區域章節透過現有播放流程解鎖，角色立繪與場景素材沿用現有設定。

2. 重寫 js/main.js 的故事章節。新增熄燈危機、被抹去名字的星眠、爺爺的探索往事與伴伴身世伏筆；各區域章節逐步揭露真相，終章以群體記憶和陪伴解開危機。保留原章節 ID、標題、角色 ID 與播放／解鎖介面。

3. 以 
ode --check 檢查 js/main.js 語法，通過；以本機 HTTP 伺服器讀取 index.html 與 js/main.js，皆回應 200；git diff --check 無空白錯誤。

## 最終狀態

- 完成：故事主線與全部章節文本重寫。
- 驗證：JavaScript 語法檢查及本機 HTTP 載入成功。
- Commit hash：尚未提交。
