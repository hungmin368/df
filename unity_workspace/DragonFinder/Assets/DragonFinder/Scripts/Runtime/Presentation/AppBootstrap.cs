using System;
using System.Collections.Generic;
using DragonFinder.Domain;
using DragonFinder.Runtime.Data;
using DragonFinder.Runtime.Persistence;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;

namespace DragonFinder.Runtime.Presentation
{
    public sealed class AppBootstrap : MonoBehaviour
    {
        private static readonly Color[] RegionColors =
        {
            new Color32(91, 170, 255, 255), new Color32(255, 150, 150, 255),
            new Color32(118, 214, 160, 255), new Color32(244, 205, 98, 255),
            new Color32(185, 145, 255, 255), new Color32(255, 174, 92, 255)
        };

        private readonly List<Button> cellButtons = new List<Button>();
        private readonly List<TMP_Text> cellLabels = new List<TMP_Text>();
        private readonly List<Outline> cellOutlines = new List<Outline>();
        private readonly List<DragonDefinition> activeDragons = new List<DragonDefinition>();

        private DragonCatalog catalog;
        private TutorialBoardDefinition tutorialBoard;
        private JsonSaveRepository repository;
        private SaveDataV1 save;
        private SfxPlayer sfx;
        private TMP_FontAsset font;
        private CanvasScaler canvasScaler;
        private RectTransform presentation;
        private GameObject menuScreen;
        private GameObject gameScreen;
        private GameObject resultOverlay;
        private RectTransform boardRoot;
        private TMP_Text menuProgress;
        private TMP_Text startButtonLabel;
        private TMP_Text menuSfxLabel;
        private TMP_Text scaleButtonLabel;
        private TMP_Text modeLabel;
        private TMP_Text timerLabel;
        private TMP_Text foundLabel;
        private TMP_Text catcherLabel;
        private TMP_Text statusLabel;
        private TMP_Text catcherButtonLabel;
        private TMP_Text resultTitle;
        private TMP_Text resultBody;
        private TMP_Text resultPrimaryLabel;
        private Button resultSecondaryButton;
        private Action resultPrimaryAction;
        private GameSession session;
        private bool tutorialMode;
        private int tutorialStage;
        private int tutorialTargetRow;
        private int focusedCell;
        private float interfaceScale = 1f;

        public GameSession CurrentSession => session;
        public int FocusedCellIndex => focusedCell;
        public bool MenuVisible => menuScreen != null && menuScreen.activeSelf;

        private void Awake()
        {
            Application.runInBackground = false;
            catalog = Resources.Load<DragonCatalog>("Content/DragonCatalog");
            tutorialBoard = Resources.Load<TutorialBoardDefinition>("Content/TutorialBoard");
            repository = new JsonSaveRepository();
            save = repository.Load();
            sfx = gameObject.AddComponent<SfxPlayer>();
            sfx.Enabled = save.sfxEnabled;
            font = CreateRuntimeFont();
            EnsureEventSystem();
            BuildInterface();
            ShowMenu();
        }

        private void Update()
        {
            HandleGlobalKeys();
            if (session == null || !gameScreen.activeSelf || resultOverlay.activeSelf)
            {
                return;
            }

            RoundPhase previous = session.Phase;
            session.Tick(Time.unscaledDeltaTime, !Application.isFocused);
            if (previous == RoundPhase.Playing && session.Phase == RoundPhase.Lost)
            {
                CompleteRound(false);
                return;
            }

            SyncFocusFromSelection();
            HandleGameKeys();
            RefreshHud();
        }

        private void EnsureEventSystem()
        {
            if (EventSystem.current != null)
            {
                return;
            }

            var eventSystem = new GameObject("EventSystem", typeof(EventSystem));
            InputSystemUIInputModule module = eventSystem.AddComponent<InputSystemUIInputModule>();
            module.AssignDefaultActions();
        }

        private void BuildInterface()
        {
            var canvasObject = new GameObject("DragonFinderCanvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            Canvas canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasScaler = canvasObject.GetComponent<CanvasScaler>();
            canvasScaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            canvasScaler.referenceResolution = new Vector2(1920, 1080);
            canvasScaler.matchWidthOrHeight = 1f;

            RectTransform canvasRect = canvasObject.GetComponent<RectTransform>();
            CreatePanel("Background", canvasRect, Vector2.zero, Vector2.zero, new Color32(13, 23, 35, 255), true);
            presentation = CreatePanel("Presentation16x9", canvasRect, Vector2.zero, new Vector2(720, 1000), new Color32(25, 39, 57, 255), false);
            CreateMenu();
            CreateGameScreen();
            CreateResultOverlay(canvasRect);
        }

        private void CreateMenu()
        {
            menuScreen = CreateContainer("MenuScreen", presentation);
            CreateText("Title", menuScreen.transform, "DRAGON FINDER", 54, new Vector2(0, 365), new Vector2(650, 90), Color.white, FontStyles.Bold);
            CreateText("Subtitle", menuScreen.transform, "恐龍尋跡・Unity 垂直切片", 28, new Vector2(0, 285), new Vector2(650, 60), new Color32(117, 230, 190, 255));
            menuProgress = CreateText("ProgressSummary", menuScreen.transform, string.Empty, 24, new Vector2(0, 205), new Vector2(620, 70), new Color32(210, 222, 236, 255));

            Button startButton = CreateButton("StartButton", menuScreen.transform, "開始", new Vector2(0, 85), new Vector2(500, 72), StartFromMenu);
            startButtonLabel = startButton.GetComponentInChildren<TMP_Text>();
            CreateButton("HelpButton", menuScreen.transform, "操作說明", new Vector2(0, -5), new Vector2(500, 68), ShowHelp);
            Button scaleButton = CreateButton("ScaleButton", menuScreen.transform, "介面大小：100%", new Vector2(0, -95), new Vector2(500, 68), CycleInterfaceScale);
            scaleButtonLabel = scaleButton.GetComponentInChildren<TMP_Text>();
            Button soundButton = CreateButton("MenuSfxButton", menuScreen.transform, "音效：開", new Vector2(0, -185), new Vector2(500, 68), ToggleSfx);
            menuSfxLabel = soundButton.GetComponentInChildren<TMP_Text>();
            CreateButton("QuitButton", menuScreen.transform, "離開遊戲", new Vector2(0, -275), new Vector2(500, 68), Application.Quit);
            CreateText("MenuFooter", menuScreen.transform, "離線遊玩・不收集資料", 20, new Vector2(0, -405), new Vector2(620, 50), new Color32(153, 174, 198, 255));
        }

        private void CreateGameScreen()
        {
            gameScreen = CreateContainer("GameScreen", presentation);
            modeLabel = CreateText("ModeLabel", gameScreen.transform, string.Empty, 32, new Vector2(0, 446), new Vector2(650, 52), Color.white, FontStyles.Bold);
            timerLabel = CreateText("TimerLabel", gameScreen.transform, string.Empty, 24, new Vector2(-220, 394), new Vector2(200, 45), Color.white);
            foundLabel = CreateText("FoundLabel", gameScreen.transform, string.Empty, 24, new Vector2(0, 394), new Vector2(200, 45), Color.white);
            catcherLabel = CreateText("CatcherLabel", gameScreen.transform, string.Empty, 24, new Vector2(220, 394), new Vector2(200, 45), Color.white);
            statusLabel = CreateText("StatusLabel", gameScreen.transform, string.Empty, 22, new Vector2(0, 337), new Vector2(650, 64), new Color32(188, 239, 221, 255));
            boardRoot = CreatePanel("BoardGrid", gameScreen.transform as RectTransform, new Vector2(0, -5), new Vector2(620, 620), new Color32(13, 20, 30, 255), false);
            Button catcherButton = CreateButton("CatcherModeButton", gameScreen.transform, "捕捉模式：關 (C)", new Vector2(-170, -370), new Vector2(310, 62), ToggleCatcherMode);
            catcherButtonLabel = catcherButton.GetComponentInChildren<TMP_Text>();
            CreateButton("RestartButton", gameScreen.transform, "重新開始 (R)", new Vector2(170, -370), new Vector2(280, 62), RestartRound);
            CreateButton("BackButton", gameScreen.transform, "返回主選單 (Esc)", new Vector2(0, -447), new Vector2(360, 58), ShowMenu);
            gameScreen.SetActive(false);
        }

        private void CreateResultOverlay(RectTransform canvasRect)
        {
            resultOverlay = CreateContainer("ModalLayer", canvasRect);
            Image shade = resultOverlay.AddComponent<Image>();
            shade.color = new Color(0, 0, 0, 0.78f);
            RectTransform shadeRect = resultOverlay.GetComponent<RectTransform>();
            Stretch(shadeRect);
            RectTransform dialog = CreatePanel("ResultDialog", shadeRect, Vector2.zero, new Vector2(620, 520), new Color32(30, 48, 68, 255), false);
            resultTitle = CreateText("ResultTitle", dialog, string.Empty, 44, new Vector2(0, 165), new Vector2(560, 80), Color.white, FontStyles.Bold);
            resultBody = CreateText("ResultBody", dialog, string.Empty, 25, new Vector2(0, 45), new Vector2(540, 145), new Color32(215, 228, 240, 255));
            Button primary = CreateButton("ResultPrimaryButton", dialog, "繼續", new Vector2(0, -85), new Vector2(420, 68), () => resultPrimaryAction?.Invoke());
            resultPrimaryLabel = primary.GetComponentInChildren<TMP_Text>();
            resultSecondaryButton = CreateButton("ResultSecondaryButton", dialog, "返回主選單", new Vector2(0, -175), new Vector2(420, 62), ShowMenu);
            resultOverlay.SetActive(false);
        }

        private void StartFromMenu()
        {
            if (save.tutorialCompleted)
            {
                StartFormalRound();
            }
            else
            {
                StartTutorial();
            }
        }

        public void StartTutorial()
        {
            BoardPuzzle puzzle = tutorialBoard != null ? tutorialBoard.CreatePuzzle() : BoardPuzzle.Tutorial5();
            tutorialMode = true;
            tutorialStage = 0;
            tutorialTargetRow = 0;
            BeginRound(puzzle, false, true, 5, 20260924);
            focusedCell = tutorialBoard != null ? tutorialBoard.SafeCell : 0;
            statusLabel.text = "先在高亮安全格按 Space 或點擊，標記 ×。";
            RefreshBoard();
        }

        public void StartFormalRound()
        {
            int seed = unchecked((int)DateTime.UtcNow.Ticks);
            BoardPuzzle puzzle = BoardGenerator.GenerateUnique(6, seed);
            tutorialMode = false;
            BeginRound(puzzle, true, false, 6, seed);
            statusLabel.text = "每行、每列、每區各一隻龍；龍彼此不能相鄰。";
        }

        private void BeginRound(BoardPuzzle puzzle, bool timed, bool lowStarsOnly, int dragonCount, int seed)
        {
            session = new GameSession(puzzle, timed);
            activeDragons.Clear();
            activeDragons.AddRange(PickDragons(dragonCount, lowStarsOnly, seed));
            focusedCell = 0;
            BuildBoard(puzzle.Size);
            menuScreen.SetActive(false);
            resultOverlay.SetActive(false);
            gameScreen.SetActive(true);
            modeLabel.text = timed ? "6×6 正式探索" : "5×5 新手教學";
            RefreshBoard();
            RefreshHud();
            FocusCurrentCell();
        }

        private List<DragonDefinition> PickDragons(int count, bool lowStarsOnly, int seed)
        {
            var candidates = new List<DragonDefinition>();
            if (catalog != null)
            {
                foreach (DragonDefinition dragon in catalog.Dragons)
                {
                    if (dragon != null && (!lowStarsOnly || dragon.Stars <= 2))
                    {
                        candidates.Add(dragon);
                    }
                }
            }

            if (candidates.Count < count)
            {
                throw new InvalidOperationException("Dragon catalog does not contain enough entries for this round.");
            }

            var random = new System.Random(seed);
            for (int i = candidates.Count - 1; i > 0; i--)
            {
                int other = random.Next(i + 1);
                (candidates[i], candidates[other]) = (candidates[other], candidates[i]);
            }

            return candidates.GetRange(0, count);
        }

        private void BuildBoard(int size)
        {
            for (int i = boardRoot.childCount - 1; i >= 0; i--)
            {
                Destroy(boardRoot.GetChild(i).gameObject);
            }

            cellButtons.Clear();
            cellLabels.Clear();
            cellOutlines.Clear();
            GridLayoutGroup grid = boardRoot.GetComponent<GridLayoutGroup>();
            if (grid == null)
            {
                grid = boardRoot.gameObject.AddComponent<GridLayoutGroup>();
            }

            grid.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
            grid.constraintCount = size;
            grid.spacing = new Vector2(4, 4);
            grid.padding = new RectOffset(6, 6, 6, 6);
            float available = 608 - (size - 1) * 4;
            grid.cellSize = new Vector2(available / size, available / size);

            for (int index = 0; index < size * size; index++)
            {
                int capturedIndex = index;
                Button button = CreateButton($"Cell_{index}", boardRoot, string.Empty, Vector2.zero, Vector2.zero, () => HandleCell(capturedIndex));
                TMP_Text label = button.GetComponentInChildren<TMP_Text>();
                label.fontSize = size == 5 ? 27 : 22;
                Outline outline = button.gameObject.AddComponent<Outline>();
                outline.effectDistance = new Vector2(4, -4);
                outline.effectColor = new Color32(255, 240, 120, 255);
                outline.enabled = false;
                cellButtons.Add(button);
                cellLabels.Add(label);
                cellOutlines.Add(outline);
            }
        }

        private void HandleCell(int index)
        {
            if (session == null || session.Phase != RoundPhase.Playing)
            {
                return;
            }

            focusedCell = index;
            if (tutorialMode)
            {
                HandleTutorialCell(index);
                return;
            }

            ApplyAction(session.ExecuteCell(index));
        }

        private void HandleTutorialCell(int index)
        {
            int safeCell = tutorialBoard != null ? tutorialBoard.SafeCell : 0;
            if (tutorialStage < 3)
            {
                if (index != safeCell)
                {
                    statusLabel.text = "請操作黃色高亮的安全格。";
                    sfx.PlayMissed();
                    return;
                }

                CellAction action = session.ToggleMark(index);
                if (tutorialStage == 0 && action.Kind == CellActionKind.Marked)
                {
                    tutorialStage = 1;
                    statusLabel.text = "很好，再按一次取消 ×。";
                }
                else if (tutorialStage == 1 && action.Kind == CellActionKind.Unmarked)
                {
                    tutorialStage = 2;
                    statusLabel.text = "再標記一次，確認你已熟悉排除操作。";
                }
                else if (tutorialStage == 2 && action.Kind == CellActionKind.Marked)
                {
                    tutorialStage = 3;
                    statusLabel.text = "按 C 或下方按鈕開啟捕捉模式。";
                }

                sfx.PlayClick();
                RefreshBoard();
                return;
            }

            if (tutorialStage == 3 || !session.CatcherMode)
            {
                statusLabel.text = "請先開啟捕捉模式。";
                sfx.PlayMissed();
                return;
            }

            int expected = session.Puzzle.AnswerCellForRow(tutorialTargetRow);
            if (index != expected)
            {
                statusLabel.text = "教學中請捕捉黃色高亮的目標格。";
                sfx.PlayMissed();
                return;
            }

            ApplyAction(session.Capture(index));
            if (session.Phase == RoundPhase.Playing)
            {
                tutorialTargetRow++;
                statusLabel.text = $"成功！繼續捕捉第 {tutorialTargetRow + 1} 隻龍。";
                focusedCell = session.Puzzle.AnswerCellForRow(tutorialTargetRow);
                RefreshBoard();
                FocusCurrentCell();
            }
        }

        private void ApplyAction(CellAction action)
        {
            switch (action.Kind)
            {
                case CellActionKind.Marked:
                case CellActionKind.Unmarked:
                    sfx.PlayClick();
                    break;
                case CellActionKind.Caught:
                    sfx.PlayCaught();
                    statusLabel.text = "捕捉成功，時間回復 30 秒。";
                    break;
                case CellActionKind.Missed:
                    sfx.PlayMissed();
                    statusLabel.text = "這裡沒有龍，已自動標記 ×。";
                    break;
                case CellActionKind.Won:
                    sfx.PlayWin();
                    CompleteRound(true);
                    return;
                case CellActionKind.Lost:
                    sfx.PlayLose();
                    CompleteRound(false);
                    return;
            }

            RefreshBoard();
            RefreshHud();
        }

        private void ToggleCatcherMode()
        {
            if (session == null || session.Phase != RoundPhase.Playing)
            {
                return;
            }

            session.SetCatcherMode(!session.CatcherMode);
            sfx.PlayClick();
            if (tutorialMode && tutorialStage == 3 && session.CatcherMode)
            {
                tutorialStage = 4;
                tutorialTargetRow = 0;
                focusedCell = session.Puzzle.AnswerCellForRow(0);
                statusLabel.text = "捕捉模式已開啟，捕捉黃色高亮的第一隻龍。";
                FocusCurrentCell();
            }

            RefreshBoard();
            RefreshHud();
        }

        private void CompleteRound(bool won)
        {
            if (won && tutorialMode)
            {
                save.tutorialCompleted = true;
                repository.Save(save);
                ShowResult("教學完成", "你已學會標記與捕捉！\n現在開始 6×6 正式探索。", "進入 6×6", StartFormalRound, true);
                return;
            }

            if (won)
            {
                foreach (DragonDefinition dragon in activeDragons)
                {
                    if (!save.caughtDragonIds.Contains(dragon.Id))
                    {
                        save.caughtDragonIds.Add(dragon.Id);
                    }
                }

                save.totalWins++;
                save.bestRemainingSeconds = Math.Max(save.bestRemainingSeconds, Mathf.FloorToInt((float)session.RemainingSeconds));
                repository.Save(save);
                ShowResult("探索成功", $"找到 {session.Found} 隻龍\n剩餘 {Mathf.FloorToInt((float)session.RemainingSeconds)} 秒", "再玩一次", StartFormalRound, true);
            }
            else
            {
                ShowResult("探索失敗", session.CatchersLeft <= 0 ? "捕捉器已用完，這局的新發現不會保存。" : "時間歸零，這局的新發現不會保存。", "重新挑戰", StartFormalRound, true);
            }
        }

        private void ShowResult(string title, string body, string primaryText, Action primaryAction, bool showSecondary)
        {
            resultTitle.text = title;
            resultBody.text = body;
            resultPrimaryLabel.text = primaryText;
            resultPrimaryAction = primaryAction;
            resultSecondaryButton.gameObject.SetActive(showSecondary);
            resultOverlay.SetActive(true);
            EventSystem.current.SetSelectedGameObject(resultPrimaryLabel.transform.parent.gameObject);
        }

        private void ShowHelp()
        {
            ShowResult(
                "操作說明",
                "方向鍵／WASD：移動焦點\nSpace：切換 ×\nC：切換捕捉模式\nEnter：操作目前格\nR：重開　M：音效　Esc：返回",
                "返回",
                () => resultOverlay.SetActive(false),
                false);
        }

        private void RestartRound()
        {
            if (tutorialMode)
            {
                StartTutorial();
            }
            else
            {
                StartFormalRound();
            }
        }

        private void ShowMenu()
        {
            session = null;
            if (gameScreen != null)
            {
                gameScreen.SetActive(false);
            }
            if (resultOverlay != null)
            {
                resultOverlay.SetActive(false);
            }
            menuScreen.SetActive(true);
            menuProgress.text = $"教學：{(save.tutorialCompleted ? "已完成" : "未完成")}　收集：{save.caughtDragonIds.Count}/8　勝場：{save.totalWins}";
            startButtonLabel.text = save.tutorialCompleted ? "開始 6×6 正式探索" : "開始 5×5 教學";
            menuSfxLabel.text = save.sfxEnabled ? "音效：開 (M)" : "音效：關 (M)";
            EventSystem.current.SetSelectedGameObject(startButtonLabel.transform.parent.gameObject);
        }

        private void ToggleSfx()
        {
            save.sfxEnabled = !save.sfxEnabled;
            sfx.Enabled = save.sfxEnabled;
            repository.Save(save);
            menuSfxLabel.text = save.sfxEnabled ? "音效：開 (M)" : "音效：關 (M)";
            if (save.sfxEnabled)
            {
                sfx.PlayClick();
            }
        }

        private void CycleInterfaceScale()
        {
            interfaceScale = interfaceScale >= 1.1f ? 0.9f : interfaceScale + 0.1f;
            presentation.localScale = Vector3.one * interfaceScale;
            scaleButtonLabel.text = $"介面大小：{Mathf.RoundToInt(interfaceScale * 100)}%";
            sfx.PlayClick();
        }

        private void HandleGlobalKeys()
        {
            Keyboard keyboard = Keyboard.current;
            if (keyboard == null)
            {
                return;
            }

            if (keyboard.mKey.wasPressedThisFrame)
            {
                ToggleSfx();
            }
        }

        private void HandleGameKeys()
        {
            Keyboard keyboard = Keyboard.current;
            if (keyboard == null)
            {
                return;
            }

            if (keyboard.spaceKey.wasPressedThisFrame)
            {
                if (tutorialMode)
                {
                    HandleTutorialCell(focusedCell);
                }
                else
                {
                    ApplyAction(session.ToggleMark(focusedCell));
                }
            }
            if (keyboard.cKey.wasPressedThisFrame)
            {
                ToggleCatcherMode();
            }
            if (keyboard.rKey.wasPressedThisFrame)
            {
                RestartRound();
            }
            if (keyboard.escapeKey.wasPressedThisFrame)
            {
                ShowMenu();
            }
        }

        private void SyncFocusFromSelection()
        {
            EventSystem eventSystem = EventSystem.current;
            if (eventSystem == null)
            {
                return;
            }

            GameObject selected = eventSystem.currentSelectedGameObject;
            if (selected == null)
            {
                return;
            }

            for (int index = 0; index < cellButtons.Count; index++)
            {
                if (cellButtons[index].gameObject == selected)
                {
                    if (focusedCell != index)
                    {
                        focusedCell = index;
                        RefreshBoard();
                    }
                    return;
                }
            }
        }

        private void RefreshBoard()
        {
            if (session == null)
            {
                return;
            }

            int tutorialExpected = -1;
            if (tutorialMode)
            {
                tutorialExpected = tutorialStage < 3
                    ? (tutorialBoard != null ? tutorialBoard.SafeCell : 0)
                    : tutorialStage >= 4 ? session.Puzzle.AnswerCellForRow(tutorialTargetRow) : -1;
            }

            for (int index = 0; index < cellButtons.Count; index++)
            {
                int region = session.Puzzle.RegionAt(index);
                Image image = cellButtons[index].GetComponent<Image>();
                image.color = RegionColors[region % RegionColors.Length];
                string regionName = ((char)('A' + region)).ToString();
                if (session.IsRevealed(index))
                {
                    int row = index / session.Puzzle.Size;
                    DragonDefinition dragon = activeDragons[row];
                    image.color = dragon.Color;
                    cellLabels[index].text = $"◆\n{dragon.DisplayName}";
                }
                else if (session.IsMarked(index))
                {
                    cellLabels[index].text = $"×\n區{regionName}";
                }
                else
                {
                    cellLabels[index].text = $"區{regionName}";
                }

                cellOutlines[index].enabled = index == focusedCell || index == tutorialExpected;
                cellOutlines[index].effectColor = index == tutorialExpected
                    ? new Color32(255, 240, 90, 255)
                    : new Color32(255, 255, 255, 255);
            }
        }

        private void RefreshHud()
        {
            if (session == null)
            {
                return;
            }

            timerLabel.text = session.Timed ? $"時間 {Mathf.CeilToInt((float)session.RemainingSeconds)} 秒" : "時間 不計時";
            foundLabel.text = $"發現 {session.Found}/{session.Puzzle.Size}";
            catcherLabel.text = $"捕捉器 {session.CatchersLeft}";
            catcherButtonLabel.text = session.CatcherMode ? "捕捉模式：開 (C)" : "捕捉模式：關 (C)";
        }

        private void FocusCurrentCell()
        {
            if (focusedCell >= 0 && focusedCell < cellButtons.Count && EventSystem.current != null)
            {
                EventSystem.current.SetSelectedGameObject(cellButtons[focusedCell].gameObject);
            }
        }

        private TMP_FontAsset CreateRuntimeFont()
        {
            string[] families = { "Microsoft JhengHei UI", "Microsoft JhengHei", "Microsoft YaHei UI", "Arial" };
            foreach (string family in families)
            {
                try
                {
                    TMP_FontAsset asset = TMP_FontAsset.CreateFontAsset(family, "Regular", 48);
                    if (asset != null)
                    {
                        asset.name = $"Runtime {family}";
                        return asset;
                    }
                }
                catch (Exception)
                {
                }
            }

            return TMP_Settings.defaultFontAsset;
        }

        private GameObject CreateContainer(string name, Transform parent)
        {
            var value = new GameObject(name, typeof(RectTransform));
            RectTransform rect = value.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            Stretch(rect);
            return value;
        }

        private RectTransform CreatePanel(string name, RectTransform parent, Vector2 position, Vector2 size, Color color, bool stretch)
        {
            var value = new GameObject(name, typeof(RectTransform), typeof(Image));
            RectTransform rect = value.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            if (stretch)
            {
                Stretch(rect);
            }
            else
            {
                rect.anchorMin = rect.anchorMax = new Vector2(0.5f, 0.5f);
                rect.anchoredPosition = position;
                rect.sizeDelta = size;
            }
            value.GetComponent<Image>().color = color;
            return rect;
        }

        private TMP_Text CreateText(string name, Transform parent, string text, float size, Vector2 position, Vector2 dimensions, Color color, FontStyles styles = FontStyles.Normal)
        {
            var value = new GameObject(name, typeof(RectTransform), typeof(TextMeshProUGUI));
            RectTransform rect = value.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = rect.anchorMax = new Vector2(0.5f, 0.5f);
            rect.anchoredPosition = position;
            rect.sizeDelta = dimensions;
            TextMeshProUGUI label = value.GetComponent<TextMeshProUGUI>();
            label.font = font;
            label.text = text;
            label.fontSize = size;
            label.fontStyle = styles;
            label.color = color;
            label.alignment = TextAlignmentOptions.Center;
            label.enableWordWrapping = true;
            label.raycastTarget = false;
            return label;
        }

        private Button CreateButton(string name, Transform parent, string text, Vector2 position, Vector2 dimensions, UnityEngine.Events.UnityAction action)
        {
            var value = new GameObject(name, typeof(RectTransform), typeof(Image), typeof(Button));
            RectTransform rect = value.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = rect.anchorMax = new Vector2(0.5f, 0.5f);
            rect.anchoredPosition = position;
            rect.sizeDelta = dimensions;
            Image image = value.GetComponent<Image>();
            image.color = new Color32(45, 105, 119, 255);
            Button button = value.GetComponent<Button>();
            button.targetGraphic = image;
            ColorBlock colors = button.colors;
            colors.normalColor = new Color32(45, 105, 119, 255);
            colors.highlightedColor = new Color32(63, 145, 157, 255);
            colors.selectedColor = new Color32(75, 169, 154, 255);
            colors.pressedColor = new Color32(34, 83, 96, 255);
            colors.disabledColor = new Color32(70, 79, 89, 255);
            button.colors = colors;
            button.navigation = new Navigation { mode = Navigation.Mode.Automatic };
            button.onClick.AddListener(action);
            Vector2 labelSize = dimensions == Vector2.zero ? new Vector2(80, 80) : dimensions - new Vector2(20, 10);
            TMP_Text label = CreateText("Label", value.transform, text, 24, Vector2.zero, labelSize, Color.white, FontStyles.Bold);
            if (dimensions == Vector2.zero)
            {
                RectTransform labelRect = label.rectTransform;
                Stretch(labelRect);
                labelRect.offsetMin = new Vector2(4, 4);
                labelRect.offsetMax = new Vector2(-4, -4);
            }
            label.transform.SetAsLastSibling();
            return button;
        }

        private static void Stretch(RectTransform rect)
        {
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
        }
    }
}
