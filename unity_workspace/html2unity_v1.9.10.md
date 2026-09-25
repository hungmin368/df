# DragonFinder HTML v1.9.10 → Unity 轉換狀態追蹤表

- 來源版本：**v1.9.10**（`index.html`／`dragonfinder_v1.9.10.html`）
- 目標專案：`unity_workspace/DragonFinder`（Unity 6000.3.24f1）
- 步驟定義：見 `html2unity.md`；逐步詳細說明：見 `html2unity_report.html`
- **本檔為唯一狀態來源：每個任務執行時都必須進來更新狀態與補充說明。**
- 最後更新：2026-09-25（建立本表；同日修正 Git 狀態與步驟 61 備註，並把 html2unity 規則寫入 `unity_workspace/AGENTS.md`；同日完成步驟 19 盤面池與步驟 20 多尺寸生成任務）

## 狀態定義

| 狀態 | 意義 |
|---|---|
| 未進行 | 尚未開始 |
| 進行中 | 已開工、尚未完成或尚未通過驗證 |
| 已完成 | 已實作並通過驗證、留有證據 |
| 故障 | 實作或驗證失敗、被阻擋 |
| 待決策 | 需使用者決定方向才能繼續 |

## 狀態統計

| 已完成 | 進行中 | 待決策 | 未進行 | 故障 | 總計 |
|---|---|---|---|---|---|
| 40 | 1 | 1 | 28 | 0 | 70 |

## 步驟狀態表

| 流水號 | 階段 | 步驟 | 狀態 | 補充說明 |
|---|---|---|---|---|
| 01 | A 前置與決策 | 技術基線決策 | 已完成 | Unity 6 LTS／URP 2D／uGUI+TMP／Windows 先／JSON 中介／離線；`worklog_unity-conversion-decisions.md` |
| 02 | A 前置與決策 | 建立 Unity 工作區與隔離規範 | 已完成 | `unity_workspace/`＋`unity_workspace/AGENTS.md`；與網頁版不得互相引用 |
| 03 | A 前置與決策 | 垂直切片範圍界定 | 已完成 | `unity_conversion_plan_report.html`；明確排除圖鑑、地圖、經濟、龍塔、故事等 |
| 04 | B 專案骨架 | Unity 編輯器安裝與專案建立 | 已完成 | `6000.3.24f1`；專案位於 `unity_workspace/DragonFinder` |
| 05 | B 專案骨架 | 套件解析與版本鎖定 | 已完成 | Input System 1.20.0／URP 17.3.0／uGUI+TMP 2.0.0／Test Framework 1.6.0 |
| 06 | B 專案骨架 | URP 2D 渲染管線與品質設定 | 已完成 | `DragonFinderURP`＋`DragonFinder2DRenderer` 已掛入 GraphicsSettings 與品質層級 |
| 07 | B 專案骨架 | 目錄結構與組件分割（asmdef） | 已完成 | `DragonFinder.Domain`（無 UnityEngine 依賴）／`Runtime`／`Editor`／`Tests.EditMode`／`Tests.PlayMode` |
| 08 | B 專案骨架 | 主場景與玩家設定 | 已完成 | `Scenes/Main.unity`；Win64 x64、Mono、1280×720 可縮放、版號 0.1.0 |
| 09 | B 專案骨架 | TextMeshPro 必要資源匯入 | 已完成 | `Assets/TextMesh Pro` 已含 TMP Settings／shader／LiberationSans SDF |
| 10 | B 專案骨架 | 介面缺字形清查與修正 | 已完成 | `✕`→`×`；199 個介面字元全數存在於 `Microsoft JhengHei UI` |
| 11 | C 核心規則層 | 棋盤模型、索引與鄰接 | 已完成 | `Domain/BoardPuzzle.cs`、`BoardRules.cs`；對應網頁版 `neighbors4` |
| 12 | C 核心規則層 | 規則驗證（行列區各一、八方向不相鄰） | 已完成 | `BoardRules`；EditMode 覆蓋 |
| 13 | C 核心規則層 | 連通區域判定 | 已完成 | 每區連通且至少 2 格；對應 `randomRegions`／`connectedAfterRemoval` |
| 14 | C 核心規則層 | 唯一解求解器 | 已完成 | `BoardSolver.cs`；支援解數量與節點上限；對應 `solve2` |
| 15 | C 核心規則層 | 決定性生成器與備援盤 | 已完成 | `BoardGenerator.cs`；對應 `generatePuzzle`（定向獵殺／0 解回退／關鍵寶箱破局） |
| 16 | C 核心規則層 | 5×5 教學固定唯一解盤面 | 已完成 | 區域 `[3,3,3,2,2,…]`、答案行 `[1,3,0,2,4]`，已驗證唯一解 |
| 17 | C 核心規則層 | 6×6 備援唯一解盤面 | 已完成 | 區域 `[1,1,1,1,1,0,…]`、答案行 `[4,2,0,3,1,5]`，已驗證唯一解 |
| 18 | C 核心規則層 | 回合狀態機（計時、捕捉、勝負） | 已完成 | `GameSession.cs`；180 秒、9 捕捉器、+30 秒上限、勝利先於耗盡、逾時 |
| 19 | C 核心規則層 | 盤面池預生成與旋轉鏡像 | 已完成 | 任務 html2unity-board-pool：`BoardTransforms`（8 變體，語意同 `transformBoard`）／`BoardPool`（Take／RefillOnce）／`AppBootstrap` 閒置暖池與正式局取用；EditMode 21/21、PlayMode 9/9 通過（`TestResults/pool-editmode.xml`／`pool-playmode.xml`） |
| 20 | C 核心規則層 | 多尺寸盤面生成（4×4–18×18） | 已完成 | 任務 html2unity-multisize-generation：`RegionBuilder`（`randomRegions`／`connectedAfterRemoval`）／`BoardSolver.Solve`（`solve2` 位元傳播、節點上限）／`PuzzleGenerator`（定向獵殺／0 解回退／關鍵寶箱）／`BoardGenerationPolicy`（1200-3000-8000 階梯、N>=14 單次 8000、節點熔斷）；EditMode 33/33、PlayMode 9/9 通過（`TestResults/multisize-editmode.xml`／`multisize-playmode.xml`） |
| 21 | D 內容與存檔 | 內容中介 JSON（8 隻代表龍） | 已完成 | `content.v1.json`；8 筆 `DF001`–`DF008` |
| 22 | D 內容與存檔 | ScriptableObject 內容模型與 Editor 匯入器 | 已完成 | `DragonContentImporter`／`DragonCatalog`／`DragonDefinition`／`TutorialBoardDefinition` |
| 23 | D 內容與存檔 | 內容匯入驗證 | 已完成 | EditMode `ImportedContentContainsEightDragonsAndValidTutorial` 等 |
| 24 | D 內容與存檔 | 完整圖鑑資料匯入（140 筆） | 未進行 | 76 常見（1–2★）＋63 遠古王者（3–5★）＋伴伴 No.000；來源 `js/data.js` |
| 25 | D 內容與存檔 | saveVersion=1 本機 JSON 存檔 | 已完成 | 原子寫入、損壞檔保留、未來版本保護；路徑 `%USERPROFILE%\AppData\LocalLow\Dragon Finder Studio\Dragon Finder\` |
| 26 | D 內容與存檔 | 存檔欄位擴充與版本遷移 | 未進行 | 需納入 16 個 `dinodoku-*` 進度鍵（圖鑑／經濟／技能／隨行／故事／關卡／龍塔…） |
| 27 | E 介面與輸入 | uGUI+TextMeshPro 版面與縮放 | 已完成 | `Presentation16x9` 720×1000 置中於 1920×1080 CanvasScaler；介面大小 90%–110% |
| 28 | E 介面與輸入 | 主選單（垂直切片版） | 已完成 | 開始教學／開始 6×6 正式探索、介面大小、音效開關、離線宣示 |
| 29 | E 介面與輸入 | 5×5 教學流程 | 已完成 | 3 標記 → C 切換捕捉 → 5 捕捉 → 教學完成；PlayMode 完整通關測試 |
| 30 | E 介面與輸入 | 6×6 正式局流程 | 已完成 | 180 秒、9 捕捉器、標記與捕捉操作 |
| 31 | E 介面與輸入 | 結果結算與重玩 | 已完成 | 勝敗覆層、重玩、回主選單 |
| 32 | E 介面與輸入 | 鍵盤導覽與快捷鍵 | 已完成 | EventSystem 單一路徑；修掉 Enter 雙發與方向鍵雙跳；C/R/Esc/M |
| 33 | E 介面與輸入 | 滑鼠與觸控輸入 | 已完成 | 共用 uGUI 指標管線；PlayMode 觸控點擊測試 |
| 34 | E 介面與輸入 | 無障礙回饋 | 已完成 | 焦點框、區A–區F、狀態文字、UI 縮放；不以顏色為唯一辨識 |
| 35 | E 介面與輸入 | 音效系統（程式生成 SFX） | 已完成 | `SfxPlayer.cs`；五種音效＋M 開關持久化；無 BGM |
| 36 | E 介面與輸入 | 主選單完整化（探索地圖、夥伴面板、導覽列） | 未進行 | 對應 `#ov-menu`：地圖節點、圖鑑完成度、夥伴對話／餵食、獎勵／戰績／故事／玩法／退出 |
| 37 | E 介面與輸入 | 關卡／區域選擇與解鎖 | 未進行 | 對應 `REGION_META`（起源地～蒼穹龍境共 15 區）／`LV`／`renderLV` |
| 38 | E 介面與輸入 | HUD 完整化（局數、分數、生命值、資源） | 未進行 | 對應 `header .hud`：局數、分數、🎟、🌌、🧪、沙漏、生命值 |
| 39 | E 介面與輸入 | 提示系統（星願種子） | 未進行 | 對應 `findRandomSafe`；耗 1 種子指出未捕獲恐龍、優先救援被 ✕ 排除者、不扣時間 |
| 40 | E 介面與輸入 | 流程畫面（清除／重來／放棄／生成中／生成失敗／休息） | 未進行 | 對應 `#controls`、`#ov-loading`、`#ov-genfail`、`#ov-rest`、`#ov-exit` |
| 41 | E 介面與輸入 | 圖鑑介面 | 未進行 | 對應 `#ov-dexfull`／`#ov-dex`；頁籤、詳情、棲地、設為隨行 |
| 42 | E 介面與輸入 | 隨行夥伴與技能系統 | 未進行 | 對應 `slotsOf`／`awakenCostOf`／`triggerBuddySkill`；技能槽、潛能激發、潛能值、冷卻 |
| 43 | E 介面與輸入 | 友好度與餵食 | 未進行 | 對應 `frGain`／`feedBuddy`；餵食 +5%、帶出場過關 +5%、伴伴起始 50% |
| 44 | E 介面與輸入 | 經濟系統（券／種子／藥水） | 未進行 | 對應 `ECON`／`econRender`；獎勵券、星願種子、進化藥水 |
| 45 | E 介面與輸入 | 伴伴進化 | 未進行 | 對應 `evolveCompanion`；🧪×3／×5／×8／×12 逐星進化 |
| 46 | E 介面與輸入 | 獎勵小遊戲 ×6 | 未進行 | 刮刮樂／拉霸／翻牌／輪盤／剪影／尋寶九宮格；對應 `#reward-games` |
| 47 | E 介面與輸入 | 故事系統 | 未進行 | 對應 `playStory`／`openStory`；序章＋15 區首次過關故事 |
| 48 | E 介面與輸入 | 龍塔模式 | 未進行 | 對應 `js/tower.js`；6×6–13×13、共 2000 層、`dinodoku-tower` |
| 49 | E 介面與輸入 | 寶箱獎勵流程 | 未進行 | 對應 `findKeyChest`／`res-chests`；關鍵寶箱格與過關寶箱 |
| 50 | E 介面與輸入 | 工程模式 | 未進行 | 對應 `#ov-dev`／`openDev`；跳關、資源加給、清存檔／重置 |
| 51 | F 素材與音訊 | 恐龍圖像與 3D 素材匯入 | 未進行 | `assets/dinos`（139 webp）、`assets/dinos_2`（11 筆）與 3D 展示素材 |
| 52 | F 素材與音訊 | 場景與品牌素材 | 未進行 | `map.png`、`assets/story`（16 svg）、`game_logo.png`、游標 |
| 53 | F 素材與音訊 | 背景音樂與完整音效組 | 未進行 | 目前僅程式生成短音效 |
| 54 | G 建置與驗證 | Windows x64 批次建置 | 已完成 | `Builds/Windows`；`DragonFinder.exe`／`UnityPlayer.dll` 皆 PE32+ x86-64 |
| 55 | G 建置與驗證 | EditMode 測試套件 | 已完成 | 13/13 通過（`TestResults/editmode.xml`） |
| 56 | G 建置與驗證 | PlayMode 測試套件 | 已完成 | 8/8 通過（`TestResults/playmode.xml`），含完整教學通關＋存檔往返 |
| 57 | G 建置與驗證 | 啟動冒煙測試與日誌稽核 | 已完成 | `Player.log` 零例外、零錯誤、零缺字形；程序存活後正常關閉 |
| 58 | G 建置與驗證 | 離線與零遙測稽核 | 已完成 | 源碼無網路 API、套件無連線模組、日誌無網路活動 |
| 59 | G 建置與驗證 | 實機存檔端對端驗證 | 已完成 | `DF_TUTORIAL_VERIFY` 驗證版寫出 `PASS`＋`saveVersion=1`；正式版回讀顯示「教學：已完成」 |
| 60 | G 建置與驗證 | 垂直切片驗證報告 | 已完成 | `vertical_slice_verification_report.html`；另附實機截圖 `release-save-read.png` |
| 61 | G 建置與驗證 | 驗證專用程式碼清理 | 待決策 | 報告稱「驗證後已移除驗證啟動器與建置入口」，但 `TutorialVerificationBuild.cs`／`TutorialVerificationRunner.cs` 仍在專案中（兩檔已隨 `438a0db` 提交） |
| 62 | G 建置與驗證 | 實體輸入人工複核 | 未進行 | 需以真實鍵盤／滑鼠在正式版完成一局教學（本機合成輸入被系統攔截） |
| 63 | G 建置與驗證 | 解析度與介面巡檢 | 未進行 | 1280×720、1600×900、1920×1080 |
| 64 | G 建置與驗證 | 完整回歸測試套件 | 未進行 | 多尺寸、多流程、存檔遷移的回歸測試 |
| 65 | G 建置與驗證 | 效能驗證 | 未進行 | 18×18 生成時間、盤面池、記憶體與啟動時間 |
| 66 | H 追蹤與發行 | 版號與更新紀錄機制 | 未進行 | 對應網頁版 v1.9.10 版號顯示與更新紀錄 |
| 67 | H 追蹤與發行 | 打包與發行流程 | 未進行 | 對應 `build_single_file.mjs` 單檔打包與 App Store 發佈流程 |
| 68 | H 追蹤與發行 | iOS 適配 | 未進行 | 待 Windows 版成熟且經明確授權後開始 |
| 69 | H 追蹤與發行 | 轉換追蹤文件維護 | 進行中 | 本表與 `html2unity.md`、`html2unity_report.html` 同步維護；規則已寫入 `unity_workspace/AGENTS.md` 的 Conversion Tracking 章節 |
| 70 | H 追蹤與發行 | Unity 工作紀錄維護與缺口補登 | 未進行 | 補登 2026-09-25 10:44–11:08 驗證後段步驟（驗證版建置、實機截圖、報告更新） |

## 更新方式

1. 任務開始時：把對應步驟狀態改為「進行中」，並在補充說明寫上任務代號。
2. 任務完成且驗證通過後：改為「已完成」，補充說明寫上證據（測試結果、產出檔案、時間）。
3. 驗證失敗或被阻擋：改為「故障」，在補充說明寫上原因與待處理項目。
4. 需要使用者決定：改為「待決策」，在補充說明寫上選項。
5. 每次更新都要同步「狀態統計」列與 `html2unity.md` 的進度快照。
