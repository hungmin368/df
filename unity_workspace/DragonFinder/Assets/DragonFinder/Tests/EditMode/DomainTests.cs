using System;
using System.IO;
using System.Linq;
using DragonFinder.Domain;
using DragonFinder.Runtime.Data;
using DragonFinder.Runtime.Persistence;
using NUnit.Framework;
using UnityEngine;

namespace DragonFinder.Tests.EditMode
{
    public sealed class DomainTests
    {
        [Test]
        public void FixedBoardsAreConnectedAndUnique()
        {
            AssertUnique(BoardPuzzle.Tutorial5());
            AssertUnique(BoardPuzzle.Fallback6());
        }

        [TestCase(1)]
        [TestCase(20260924)]
        [TestCase(-741852)]
        public void GeneratedSixBySixBoardIsUnique(int seed)
        {
            AssertUnique(BoardGenerator.GenerateUnique(6, seed));
        }

        [Test]
        public void FormalRoundUsesConfirmedTimeAndCatcherRules()
        {
            var session = new GameSession(BoardPuzzle.Fallback6(), true);
            Assert.That(session.InitialSeconds, Is.EqualTo(180));
            Assert.That(session.RemainingSeconds, Is.EqualTo(180));
            Assert.That(session.CatchersLeft, Is.EqualTo(9));

            for (int row = 0; row < 5; row++)
            {
                session.Capture(session.Puzzle.AnswerCellForRow(row));
            }

            for (int index = 0; session.CatchersLeft > 1; index++)
            {
                if (!session.Puzzle.IsAnswerCell(index) && !session.IsRevealed(index))
                {
                    session.Capture(index);
                }
            }

            CellAction finalAction = session.Capture(session.Puzzle.AnswerCellForRow(5));
            Assert.That(finalAction.Kind, Is.EqualTo(CellActionKind.Won));
            Assert.That(session.Phase, Is.EqualTo(RoundPhase.Won));
            Assert.That(session.CatchersLeft, Is.EqualTo(0));
        }

        [Test]
        public void TutorialRoundIsUntimedWithFivePlusThreeCatchers()
        {
            var session = new GameSession(BoardPuzzle.Tutorial5(), false);
            Assert.That(session.Timed, Is.False);
            Assert.That(session.InitialSeconds, Is.Zero);
            Assert.That(session.RemainingSeconds, Is.Zero);
            Assert.That(session.CatchersLeft, Is.EqualTo(8));

            session.Tick(1000, false);
            session.Tick(1000, true);
            Assert.That(session.Phase, Is.EqualTo(RoundPhase.Playing));

            for (int row = 0; row < 4; row++)
            {
                CellAction action = session.Capture(session.Puzzle.AnswerCellForRow(row));
                Assert.That(action.Kind, Is.EqualTo(CellActionKind.Caught));
                Assert.That(session.RemainingSeconds, Is.Zero);
            }

            Assert.That(session.Capture(session.Puzzle.AnswerCellForRow(4)).Kind, Is.EqualTo(CellActionKind.Won));
            Assert.That(session.Phase, Is.EqualTo(RoundPhase.Won));
        }

        [Test]
        public void CatchingRestoresThirtySecondsCappedAtTotal()
        {
            var session = new GameSession(BoardPuzzle.Fallback6(), true);
            session.Tick(60, false);
            Assert.That(session.RemainingSeconds, Is.EqualTo(120));

            session.Capture(session.Puzzle.AnswerCellForRow(0));
            Assert.That(session.RemainingSeconds, Is.EqualTo(150));
            session.Capture(session.Puzzle.AnswerCellForRow(1));
            Assert.That(session.RemainingSeconds, Is.EqualTo(180));
            session.Capture(session.Puzzle.AnswerCellForRow(2));
            Assert.That(session.RemainingSeconds, Is.EqualTo(180));
            Assert.That(session.Phase, Is.EqualTo(RoundPhase.Playing));
        }

        [Test]
        public void MissedCaptureMarksCellAndLosesWhenCatchersRunOut()
        {
            var session = new GameSession(BoardPuzzle.Fallback6(), true);
            session.SetCatcherMode(true);
            Assert.That(session.CatcherMode, Is.True);

            int[] misses = Enumerable.Range(0, 11).Where(index => !session.Puzzle.IsAnswerCell(index)).Take(9).ToArray();
            for (int i = 0; i < 8; i++)
            {
                Assert.That(session.Capture(misses[i]).Kind, Is.EqualTo(CellActionKind.Missed));
                Assert.That(session.IsMarked(misses[i]), Is.True);
            }

            Assert.That(session.CatchersLeft, Is.EqualTo(1));
            Assert.That(session.Capture(misses[8]).Kind, Is.EqualTo(CellActionKind.Lost));
            Assert.That(session.Phase, Is.EqualTo(RoundPhase.Lost));
            Assert.That(session.CatcherMode, Is.False);

            session.SetCatcherMode(true);
            Assert.That(session.CatcherMode, Is.False);
            Assert.That(session.ToggleMark(0).Kind, Is.EqualTo(CellActionKind.Ignored));
        }

        [Test]
        public void MarkingAndTimeoutFollowRoundState()
        {
            var session = new GameSession(BoardPuzzle.Fallback6(), true);
            int safeCell = Enumerable.Range(0, 36).First(index => !session.Puzzle.IsAnswerCell(index));
            Assert.That(session.ToggleMark(safeCell).Kind, Is.EqualTo(CellActionKind.Marked));
            Assert.That(session.IsMarked(safeCell), Is.True);
            Assert.That(session.ToggleMark(safeCell).Kind, Is.EqualTo(CellActionKind.Unmarked));
            session.Tick(181, false);
            Assert.That(session.Phase, Is.EqualTo(RoundPhase.Lost));
            Assert.That(session.RemainingSeconds, Is.Zero);
        }

        [Test]
        public void SaveVersionOneRoundTripsWithoutActiveBoardState()
        {
            string directory = Path.Combine(Path.GetTempPath(), "DragonFinderTests", Guid.NewGuid().ToString("N"));
            string path = Path.Combine(directory, "save.json");
            try
            {
                var repository = new JsonSaveRepository(path);
                var source = new SaveDataV1
                {
                    tutorialCompleted = true,
                    totalWins = 3,
                    bestRemainingSeconds = 91,
                    sfxEnabled = false
                };
                source.caughtDragonIds.Add("DF001");
                Assert.That(repository.Save(source), Is.True);

                SaveDataV1 loaded = repository.Load();
                Assert.That(loaded.saveVersion, Is.EqualTo(1));
                Assert.That(loaded.tutorialCompleted, Is.True);
                Assert.That(loaded.caughtDragonIds, Is.EquivalentTo(new[] { "DF001" }));
                Assert.That(File.ReadAllText(path), Does.Not.Contain("remainingSeconds"));
                Assert.That(File.ReadAllText(path), Does.Not.Contain("regions"));
            }
            finally
            {
                if (Directory.Exists(directory))
                {
                    Directory.Delete(directory, true);
                }
            }
        }

        [Test]
        public void FutureSaveVersionIsNotOverwritten()
        {
            string directory = Path.Combine(Path.GetTempPath(), "DragonFinderTests", Guid.NewGuid().ToString("N"));
            string path = Path.Combine(directory, "save.json");
            Directory.CreateDirectory(directory);
            const string futureJson = "{\"saveVersion\":99,\"tutorialCompleted\":true}";
            File.WriteAllText(path, futureJson);
            try
            {
                var repository = new JsonSaveRepository(path);
                repository.Load();
                Assert.That(repository.Save(SaveDataV1.CreateDefault()), Is.False);
                Assert.That(File.ReadAllText(path), Is.EqualTo(futureJson));
            }
            finally
            {
                Directory.Delete(directory, true);
            }
        }

        [Test]
        public void ImportedContentContainsEightDragonsAndValidTutorial()
        {
            DragonCatalog catalog = Resources.Load<DragonCatalog>("Content/DragonCatalog");
            TutorialBoardDefinition tutorial = Resources.Load<TutorialBoardDefinition>("Content/TutorialBoard");
            Assert.That(catalog, Is.Not.Null);
            Assert.That(catalog.Dragons.Count, Is.EqualTo(8));
            Assert.That(catalog.Dragons.Select(dragon => dragon.Id).Distinct().Count(), Is.EqualTo(8));
            Assert.That(catalog.Dragons.Count(dragon => dragon.Stars <= 2), Is.GreaterThanOrEqualTo(5));
            Assert.That(tutorial, Is.Not.Null);
            AssertUnique(tutorial.CreatePuzzle());
        }

        [Test]
        public void DomainAssemblyHasNoUnityEngineReference()
        {
            string[] names = typeof(BoardPuzzle).Assembly.GetReferencedAssemblies().Select(reference => reference.Name).ToArray();
            Assert.That(names.Any(name => name.StartsWith("UnityEngine", StringComparison.Ordinal)), Is.False);
        }

        private static void AssertUnique(BoardPuzzle puzzle)
        {
            Assert.That(BoardRules.HasValidRegions(puzzle.Size, puzzle.Regions), Is.True);
            Assert.That(BoardRules.IsValidSolution(puzzle.Size, puzzle.Regions, puzzle.AnswerColumns), Is.True);
            Assert.That(BoardSolver.CountSolutions(puzzle.Size, puzzle.Regions, 2, out int[] first), Is.EqualTo(1));
            Assert.That(first, Is.EqualTo(puzzle.AnswerColumns));
        }
    }
}
