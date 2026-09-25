#if DF_TUTORIAL_VERIFY
using System;
using System.Collections;
using System.IO;
using System.Reflection;
using DragonFinder.Domain;
using DragonFinder.Runtime.Persistence;
using UnityEngine;

namespace DragonFinder.Runtime.Presentation
{
    public sealed class TutorialVerificationRunner : MonoBehaviour
    {
        private const string ResultFileName = "tutorial-verification-result.txt";

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Install()
        {
            var host = new GameObject("TutorialVerificationRunner");
            DontDestroyOnLoad(host);
            host.AddComponent<TutorialVerificationRunner>();
        }

        private IEnumerator Start()
        {
            yield return null;
            yield return null;

            try
            {
                VerifyTutorialCompletion();
                WriteResult("PASS");
                Debug.Log("TutorialVerification: PASS");
            }
            catch (Exception exception)
            {
                WriteResult($"FAIL\n{exception}");
                Debug.LogException(exception);
            }

            yield return new WaitForSecondsRealtime(1f);
            Application.Quit(0);
        }

        private static void VerifyTutorialCompletion()
        {
            AppBootstrap bootstrap = FindFirstObjectByType<AppBootstrap>();
            if (bootstrap == null)
            {
                throw new InvalidOperationException("AppBootstrap was not found.");
            }

            MethodInfo handleTutorialCell = typeof(AppBootstrap).GetMethod("HandleTutorialCell", BindingFlags.Instance | BindingFlags.NonPublic);
            MethodInfo handleCell = typeof(AppBootstrap).GetMethod("HandleCell", BindingFlags.Instance | BindingFlags.NonPublic);
            MethodInfo toggleCatcherMode = typeof(AppBootstrap).GetMethod("ToggleCatcherMode", BindingFlags.Instance | BindingFlags.NonPublic);
            if (handleTutorialCell == null || handleCell == null || toggleCatcherMode == null)
            {
                throw new InvalidOperationException("Tutorial input handlers were not found.");
            }

            bootstrap.StartTutorial();
            int safeCell = bootstrap.FocusedCellIndex;
            handleTutorialCell.Invoke(bootstrap, new object[] { safeCell });
            handleTutorialCell.Invoke(bootstrap, new object[] { safeCell });
            handleTutorialCell.Invoke(bootstrap, new object[] { safeCell });
            toggleCatcherMode.Invoke(bootstrap, null);

            for (int row = 0; row < bootstrap.CurrentSession.Puzzle.Size; row++)
            {
                int answerCell = bootstrap.CurrentSession.Puzzle.AnswerCellForRow(row);
                handleCell.Invoke(bootstrap, new object[] { answerCell });
            }

            if (bootstrap.CurrentSession.Phase != RoundPhase.Won)
            {
                throw new InvalidOperationException($"Tutorial ended in {bootstrap.CurrentSession.Phase}.");
            }

            string savePath = Path.Combine(Application.persistentDataPath, "dragonfinder.save.json");
            SaveDataV1 save = new JsonSaveRepository(savePath).Load();
            if (!save.tutorialCompleted || save.saveVersion != 1)
            {
                throw new InvalidOperationException("Tutorial completion was not saved as saveVersion 1.");
            }
        }

        private static void WriteResult(string value)
        {
            File.WriteAllText(Path.Combine(Application.persistentDataPath, ResultFileName), value);
        }
    }
}
#endif
