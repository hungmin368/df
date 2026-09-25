using System;
using System.Collections.Generic;

namespace DragonFinder.Domain
{
    public sealed class BoardPuzzle
    {
        private readonly int[] regions;
        private readonly int[] answerColumns;

        public BoardPuzzle(int size, int[] regions, int[] answerColumns)
        {
            if (size < 2)
            {
                throw new ArgumentOutOfRangeException(nameof(size));
            }

            this.regions = regions != null ? (int[])regions.Clone() : throw new ArgumentNullException(nameof(regions));
            this.answerColumns = answerColumns != null ? (int[])answerColumns.Clone() : throw new ArgumentNullException(nameof(answerColumns));
            Size = size;

            if (!BoardRules.HasValidRegions(size, this.regions))
            {
                throw new ArgumentException("Regions must form connected groups with valid IDs.", nameof(regions));
            }

            if (!BoardRules.IsValidSolution(size, this.regions, this.answerColumns))
            {
                throw new ArgumentException("Answer columns do not satisfy the puzzle rules.", nameof(answerColumns));
            }
        }

        public int Size { get; }
        public IReadOnlyList<int> Regions => regions;
        public IReadOnlyList<int> AnswerColumns => answerColumns;

        public int Index(int row, int column)
        {
            if (row < 0 || row >= Size || column < 0 || column >= Size)
            {
                throw new ArgumentOutOfRangeException();
            }

            return row * Size + column;
        }

        public int RegionAt(int index)
        {
            if (index < 0 || index >= regions.Length)
            {
                throw new ArgumentOutOfRangeException(nameof(index));
            }

            return regions[index];
        }

        public int AnswerCellForRow(int row)
        {
            if (row < 0 || row >= Size)
            {
                throw new ArgumentOutOfRangeException(nameof(row));
            }

            return Index(row, answerColumns[row]);
        }

        public bool IsAnswerCell(int index)
        {
            if (index < 0 || index >= regions.Length)
            {
                return false;
            }

            int row = index / Size;
            return answerColumns[row] == index % Size;
        }

        public static BoardPuzzle Tutorial5()
        {
            return new BoardPuzzle(
                5,
                new[] { 3, 3, 3, 2, 2, 3, 3, 3, 2, 2, 4, 4, 2, 2, 2, 4, 4, 0, 2, 2, 4, 4, 0, 1, 1 },
                new[] { 1, 3, 0, 2, 4 });
        }

        public static BoardPuzzle Fallback6()
        {
            return new BoardPuzzle(
                6,
                new[] { 1, 1, 1, 1, 1, 0, 2, 1, 4, 1, 0, 0, 2, 5, 4, 3, 0, 0, 2, 5, 4, 3, 0, 0, 2, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
                new[] { 4, 2, 0, 3, 1, 5 });
        }
    }
}
