using System;
using System.Collections.Generic;

namespace DragonFinder.Domain
{
    public static class BoardSolver
    {
        public static int CountSolutions(int size, IReadOnlyList<int> regions, int limit, out int[] firstSolution)
        {
            if (limit < 1)
            {
                throw new ArgumentOutOfRangeException(nameof(limit));
            }

            firstSolution = null;
            if (!BoardRules.HasValidRegions(size, regions))
            {
                return 0;
            }

            var answer = new int[size];
            var usedColumns = new bool[size];
            var usedRegions = new bool[size];
            int[] first = null;
            int count = 0;
            Search(0);
            firstSolution = first;
            return count;

            void Search(int row)
            {
                if (count >= limit)
                {
                    return;
                }

                if (row == size)
                {
                    count++;
                    if (first == null)
                    {
                        first = (int[])answer.Clone();
                    }
                    return;
                }

                for (int column = 0; column < size; column++)
                {
                    int region = regions[row * size + column];
                    if (usedColumns[column] || usedRegions[region])
                    {
                        continue;
                    }

                    if (row > 0 && Math.Abs(column - answer[row - 1]) <= 1)
                    {
                        continue;
                    }

                    answer[row] = column;
                    usedColumns[column] = true;
                    usedRegions[region] = true;
                    Search(row + 1);
                    usedRegions[region] = false;
                    usedColumns[column] = false;
                }
            }
        }
    }
}
