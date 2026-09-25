using System;
using System.Collections.Generic;

namespace DragonFinder.Domain
{
    public static class BoardRules
    {
        public static bool HasValidRegions(int size, IReadOnlyList<int> regions)
        {
            if (size < 2 || regions == null || regions.Count != size * size)
            {
                return false;
            }

            var counts = new int[size];
            for (int i = 0; i < regions.Count; i++)
            {
                int region = regions[i];
                if (region < 0 || region >= size)
                {
                    return false;
                }

                counts[region]++;
            }

            for (int region = 0; region < size; region++)
            {
                if (counts[region] < 2 || !IsRegionConnected(size, regions, region, counts[region]))
                {
                    return false;
                }
            }

            return true;
        }

        public static bool IsValidSolution(int size, IReadOnlyList<int> regions, IReadOnlyList<int> answerColumns)
        {
            if (!HasValidRegions(size, regions) || answerColumns == null || answerColumns.Count != size)
            {
                return false;
            }

            var usedColumns = new bool[size];
            var usedRegions = new bool[size];
            for (int row = 0; row < size; row++)
            {
                int column = answerColumns[row];
                if (column < 0 || column >= size || usedColumns[column])
                {
                    return false;
                }

                int region = regions[row * size + column];
                if (usedRegions[region])
                {
                    return false;
                }

                if (row > 0 && Math.Abs(column - answerColumns[row - 1]) <= 1)
                {
                    return false;
                }

                usedColumns[column] = true;
                usedRegions[region] = true;
            }

            return true;
        }

        private static bool IsRegionConnected(int size, IReadOnlyList<int> regions, int targetRegion, int expectedCount)
        {
            int start = -1;
            for (int i = 0; i < regions.Count; i++)
            {
                if (regions[i] == targetRegion)
                {
                    start = i;
                    break;
                }
            }

            if (start < 0)
            {
                return false;
            }

            var visited = new bool[regions.Count];
            var queue = new Queue<int>();
            queue.Enqueue(start);
            visited[start] = true;
            int count = 0;

            while (queue.Count > 0)
            {
                int index = queue.Dequeue();
                count++;
                int row = index / size;
                int column = index % size;
                TryVisit(row - 1, column);
                TryVisit(row + 1, column);
                TryVisit(row, column - 1);
                TryVisit(row, column + 1);
            }

            return count == expectedCount;

            void TryVisit(int row, int column)
            {
                if (row < 0 || row >= size || column < 0 || column >= size)
                {
                    return;
                }

                int index = row * size + column;
                if (!visited[index] && regions[index] == targetRegion)
                {
                    visited[index] = true;
                    queue.Enqueue(index);
                }
            }
        }
    }
}
