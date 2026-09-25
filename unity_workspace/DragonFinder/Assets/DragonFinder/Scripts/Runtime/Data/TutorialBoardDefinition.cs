using DragonFinder.Domain;
using UnityEngine;

namespace DragonFinder.Runtime.Data
{
    [CreateAssetMenu(menuName = "Dragon Finder/Tutorial Board")]
    public sealed class TutorialBoardDefinition : ScriptableObject
    {
        [SerializeField] private int size;
        [SerializeField] private int[] regions;
        [SerializeField] private int[] answerColumns;
        [SerializeField] private int safeCell;

        public int SafeCell => safeCell;

        public void Initialize(int valueSize, int[] valueRegions, int[] valueAnswerColumns, int valueSafeCell)
        {
            size = valueSize;
            regions = (int[])valueRegions.Clone();
            answerColumns = (int[])valueAnswerColumns.Clone();
            safeCell = valueSafeCell;
        }

        public BoardPuzzle CreatePuzzle()
        {
            return new BoardPuzzle(size, regions, answerColumns);
        }
    }
}
