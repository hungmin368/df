using System.Collections;
using DragonFinder.Runtime.Presentation;
using NUnit.Framework;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.UI;

namespace DragonFinder.Tests.PlayMode
{
    public sealed class InterfaceSmokeTests
    {
        private InputSettings.EditorInputBehaviorInPlayMode previousEditorInputBehavior;
        private InputSettings.BackgroundBehavior previousBackgroundBehavior;

        [UnitySetUp]
        public IEnumerator LoadMainScene()
        {
            previousEditorInputBehavior = InputSystem.settings.editorInputBehaviorInPlayMode;
            previousBackgroundBehavior = InputSystem.settings.backgroundBehavior;
            InputSystem.settings.editorInputBehaviorInPlayMode = InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
            InputSystem.settings.backgroundBehavior = InputSettings.BackgroundBehavior.IgnoreFocus;
            yield return SceneManager.LoadSceneAsync("Main");
            yield return null;
        }

        [UnityTearDown]
        public IEnumerator RestoreEditorInputBehavior()
        {
            InputSystem.settings.editorInputBehaviorInPlayMode = previousEditorInputBehavior;
            InputSystem.settings.backgroundBehavior = previousBackgroundBehavior;
            yield return null;
        }

        [UnityTest]
        public IEnumerator MenuUsesUguiTmpAndInputSystem()
        {
            AppBootstrap bootstrap = Object.FindFirstObjectByType<AppBootstrap>();
            Assert.That(bootstrap, Is.Not.Null);
            Assert.That(bootstrap.MenuVisible, Is.True);
            Assert.That(Object.FindFirstObjectByType<Canvas>(), Is.Not.Null);
            Assert.That(Object.FindFirstObjectByType<TextMeshProUGUI>(), Is.Not.Null);
            Assert.That(Object.FindFirstObjectByType<InputSystemUIInputModule>(), Is.Not.Null);
            Assert.That(GameObject.Find("StartButton").GetComponent<Button>(), Is.Not.Null);
            yield return null;
        }

        [UnityTest]
        public IEnumerator TutorialCreatesFiveByFiveAccessibleBoard()
        {
            AppBootstrap bootstrap = Object.FindFirstObjectByType<AppBootstrap>();
            bootstrap.StartTutorial();
            yield return null;

            Assert.That(bootstrap.CurrentSession, Is.Not.Null);
            Assert.That(bootstrap.CurrentSession.Puzzle.Size, Is.EqualTo(5));
            Assert.That(bootstrap.CurrentSession.Timed, Is.False);
            Assert.That(GameObject.Find("BoardGrid").transform.childCount, Is.EqualTo(25));
            Assert.That(GameObject.Find("Cell_0").GetComponentInChildren<TMP_Text>().text, Does.Contain("區"));
            Assert.That(EventSystem.current.currentSelectedGameObject, Is.Not.Null);
        }

        [UnityTest]
        public IEnumerator FormalRoundCreatesConfirmedSixBySixState()
        {
            AppBootstrap bootstrap = Object.FindFirstObjectByType<AppBootstrap>();
            bootstrap.StartFormalRound();
            yield return null;

            Assert.That(bootstrap.CurrentSession.Puzzle.Size, Is.EqualTo(6));
            Assert.That(bootstrap.CurrentSession.InitialSeconds, Is.EqualTo(180));
            Assert.That(bootstrap.CurrentSession.CatchersLeft, Is.EqualTo(9));
            Assert.That(GameObject.Find("BoardGrid").transform.childCount, Is.EqualTo(36));
            Assert.That(GameObject.Find("CatcherModeButton").GetComponent<Button>(), Is.Not.Null);
            Assert.That(GameObject.Find("Cell_0").GetComponent<Outline>().enabled, Is.True);
        }

        [UnityTest]
        public IEnumerator MenuKeyboardNavigationMovesBetweenButtons()
        {
            yield return null;
            Assert.That(EventSystem.current.currentSelectedGameObject?.name, Is.EqualTo("StartButton"));

            Keyboard keyboard = InputSystem.AddDevice<Keyboard>();
            InputSystem.QueueStateEvent(keyboard, new KeyboardState(Key.DownArrow));
            yield return null;
            yield return null;
            InputSystem.QueueStateEvent(keyboard, new KeyboardState());
            yield return null;

            Assert.That(EventSystem.current.currentSelectedGameObject?.name, Is.EqualTo("HelpButton"));
        }

        [UnityTest]
        public IEnumerator EnterKeyActivatesFocusedCellExactlyOnce()
        {
            AppBootstrap bootstrap = Object.FindFirstObjectByType<AppBootstrap>();
            bootstrap.StartFormalRound();
            yield return null;

            Keyboard keyboard = InputSystem.AddDevice<Keyboard>();
            InputSystem.QueueStateEvent(keyboard, new KeyboardState(Key.Enter));
            yield return null;
            yield return null;
            InputSystem.QueueStateEvent(keyboard, new KeyboardState());
            yield return null;

            Assert.That(bootstrap.FocusedCellIndex, Is.EqualTo(0));
            Assert.That(bootstrap.CurrentSession.IsMarked(0), Is.True);
        }

        [UnityTest]
        public IEnumerator ArrowAndWasdKeysMoveBoardFocus()
        {
            AppBootstrap bootstrap = Object.FindFirstObjectByType<AppBootstrap>();
            bootstrap.StartFormalRound();
            yield return null;

            Keyboard keyboard = InputSystem.AddDevice<Keyboard>();
            InputSystem.QueueStateEvent(keyboard, new KeyboardState(Key.RightArrow));
            yield return null;
            yield return null;
            InputSystem.QueueStateEvent(keyboard, new KeyboardState());
            yield return null;

            Assert.That(bootstrap.FocusedCellIndex, Is.EqualTo(1));
            Assert.That(EventSystem.current.currentSelectedGameObject?.name, Is.EqualTo("Cell_1"));

            InputSystem.QueueStateEvent(keyboard, new KeyboardState(Key.S));
            yield return null;
            yield return null;
            InputSystem.QueueStateEvent(keyboard, new KeyboardState());
            yield return null;

            Assert.That(bootstrap.FocusedCellIndex, Is.EqualTo(7));
            Assert.That(GameObject.Find("Cell_1").GetComponent<Outline>().enabled, Is.False);
            Assert.That(GameObject.Find("Cell_7").GetComponent<Outline>().enabled, Is.True);
        }

        [UnityTest]
        public IEnumerator TouchTapOnCellTogglesMark()
        {
            AppBootstrap bootstrap = Object.FindFirstObjectByType<AppBootstrap>();
            bootstrap.StartFormalRound();
            yield return null;

            Touchscreen touchscreen = InputSystem.AddDevice<Touchscreen>();
            RectTransform cell = GameObject.Find("Cell_0").GetComponent<RectTransform>();
            Vector3[] corners = new Vector3[4];
            cell.GetWorldCorners(corners);
            Vector2 screenPosition = RectTransformUtility.WorldToScreenPoint(null, (corners[0] + corners[2]) * 0.5f);

            InputSystem.QueueStateEvent(touchscreen, new TouchState { touchId = 1, position = screenPosition, phase = UnityEngine.InputSystem.TouchPhase.Began, pressure = 1f, tapCount = 1 });
            yield return null;
            InputSystem.QueueStateEvent(touchscreen, new TouchState { touchId = 1, position = screenPosition, phase = UnityEngine.InputSystem.TouchPhase.Ended, tapCount = 1 });
            yield return null;
            yield return null;

            Assert.That(bootstrap.CurrentSession.IsMarked(0), Is.True);
        }

        [UnityTest]
        public IEnumerator TutorialCompletesViaKeyboardAndPersistsSave()
        {
            string savePath = System.IO.Path.Combine(Application.persistentDataPath, "dragonfinder.save.json");
            string original = System.IO.File.Exists(savePath) ? System.IO.File.ReadAllText(savePath) : null;

            AppBootstrap bootstrap = Object.FindFirstObjectByType<AppBootstrap>();
            bootstrap.StartTutorial();
            yield return null;

            Keyboard keyboard = InputSystem.AddDevice<Keyboard>();
            try
            {
                yield return Press(keyboard, Key.Space);
                yield return Press(keyboard, Key.Space);
                yield return Press(keyboard, Key.Space);
                yield return Press(keyboard, Key.C);
                yield return Press(keyboard, Key.Enter);
                yield return Press(keyboard, Key.Enter);
                yield return Press(keyboard, Key.Enter);
                yield return Press(keyboard, Key.Enter);
                yield return Press(keyboard, Key.Enter);
                yield return null;
                yield return null;

                Assert.That(bootstrap.CurrentSession.Phase, Is.EqualTo(DragonFinder.Domain.RoundPhase.Won));
                Assert.That(GameObject.Find("ModalLayer").activeSelf, Is.True);
                Assert.That(GameObject.Find("ResultTitle").GetComponent<TMP_Text>().text, Is.EqualTo("教學完成"));
                Assert.That(System.IO.File.Exists(savePath), Is.True);
                var loaded = new DragonFinder.Runtime.Persistence.JsonSaveRepository(savePath).Load();
                Assert.That(loaded.tutorialCompleted, Is.True);
            }
            finally
            {
                if (original == null)
                {
                    if (System.IO.File.Exists(savePath)) { System.IO.File.Delete(savePath); }
                }
                else
                {
                    System.IO.File.WriteAllText(savePath, original);
                }
            }
        }

        private static IEnumerator Press(Keyboard keyboard, Key key)
        {
            InputSystem.QueueStateEvent(keyboard, new KeyboardState(key));
            yield return null;
            yield return null;
            InputSystem.QueueStateEvent(keyboard, new KeyboardState());
            yield return null;
        }
    }
}
