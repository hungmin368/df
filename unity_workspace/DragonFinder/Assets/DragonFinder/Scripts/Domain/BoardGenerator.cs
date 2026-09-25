using System;
using System.Collections.Generic;

namespace DragonFinder.Domain
{
    public static class BoardGenerator
    {
        public static BoardPuzzle GenerateUnique(int size, int seed, int maxAttempts = 5000)
        {
            var random = new Random(seed);
            for (int attempt = 0; attempt < maxAttempts; attempt++)
            {
                int[] regions = GenerateConnectedRegions(size, random);
                if (regions == null)
                {
                    continue;
                }

                int solutionCount = BoardSolver.CountSolutions(size, regions, 2, out int[] solution);
                if (solutionCount == 1)
                {
                    return new BoardPuzzle(size, regions, solution);
                }
            }

            if (size == 5)
            {
                return BoardPuzzle.Tutorial5();
            }

            if (size == 6)
            {
                return BoardPuzzle.Fallback6();
            }

            throw new InvalidOperationException($"Unable to generate a unique {size}x{size} puzzle.");
        }

        private static int[] GenerateConnectedRegions(int size, Random random)
        {
            int cellCount = size * size;
            var regions = new int[cellCount];
            Array.Fill(regions, -1);

            var cells = new List<int>(cellCount);
            for (int i = 0; i < cellCount; i++)
            {
                cells.Add(i);
            }

            for (int region = 0; region < size; region++)
            {
                int choice = random.Next(cells.Count);
                int seed = cells[choice];
                cells.RemoveAt(choice);
                regions[seed] = region;
            }

            while (cells.Count > 0)
            {
                var expandable = new List<int>();
                for (int i = 0; i < cells.Count; i++)
                {
                    if (GetAdjacentRegions(cells[i], size, regions).Count > 0)
                    {
                        expandable.Add(cells[i]);
                    }
                }

                if (expandable.Count == 0)
                {
                    return null;
                }

                int cell = expandable[random.Next(expandable.Count)];
                List<int> adjacent = GetAdjacentRegions(cell, size, regions);
                regions[cell] = adjacent[random.Next(adjacent.Count)];
                cells.Remove(cell);
            }

            var counts = new int[size];
            for (int i = 0; i < regions.Length; i++)
            {
                counts[regions[i]]++;
            }

            for (int region = 0; region < size; region++)
            {
                if (counts[region] < 2)
                {
                    return null;
                }
            }

            return regions;
        }

        private static List<int> GetAdjacentRegions(int cell, int size, IReadOnlyList<int> regions)
        {
            int row = cell / size;
            int column = cell % size;
            var result = new List<int>(4);
            Add(row - 1, column);
            Add(row + 1, column);
            Add(row, column - 1);
            Add(row, column + 1);
            return result;

            void Add(int targetRow, int targetColumn)
            {
                if (targetRow < 0 || targetRow >= size || targetColumn < 0 || targetColumn >= size)
                {
                    return;
                }

                int region = regions[targetRow * size + targetColumn];
                if (region >= 0 && !result.Contains(region))
                {
                    result.Add(region);
                }
            }
        }
    }
}
