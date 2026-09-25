using System;
using System.Collections.Generic;

namespace DragonFinder.Domain
{
    public readonly struct CellFix
    {
        public CellFix(int row, int column, bool isCat)
        {
            Row = row;
            Column = column;
            IsCat = isCat;
        }

        public int Row { get; }
        public int Column { get; }
        public bool IsCat { get; }
    }

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

            List<int[]> solutions = Solve(size, regions, int.MaxValue, limit, null);
            if (solutions.Count > 0)
            {
                firstSolution = solutions[0];
            }

            return solutions.Count;
        }

        /// <summary>Solves up to <paramref name="maxSolutions"/> puzzles; returns null when the node limit aborted the search.</summary>
        public static List<int[]> Solve(int size, IReadOnlyList<int> regions, int nodeLimit, int maxSolutions, IReadOnlyList<CellFix> fixes)
        {
            if (size < 2)
            {
                throw new ArgumentOutOfRangeException(nameof(size));
            }

            if (maxSolutions < 1)
            {
                throw new ArgumentOutOfRangeException(nameof(maxSolutions));
            }

            return new Search(size, regions, nodeLimit, maxSolutions, fixes).Run();
        }

        private sealed class Search
        {
            private readonly int size;
            private readonly int allColumns;
            private readonly int nodeLimit;
            private readonly int maxSolutions;
            private readonly int[] regions;
            private readonly int[] regionColumnMasks;
            private readonly int[] candidate;
            private readonly int[] answer;
            private readonly int[] candidateStack;
            private readonly int[] answerStack;
            private readonly int[] usedColumnStack;
            private readonly int[] usedRegionStack;
            private readonly List<int[]> solutions = new List<int[]>();
            private long nodes;
            private bool aborted;
            private int usedColumns;
            private int usedRegions;

            public Search(int size, IReadOnlyList<int> regions, int nodeLimit, int maxSolutions, IReadOnlyList<CellFix> fixes)
            {
                this.size = size;
                this.nodeLimit = nodeLimit;
                this.maxSolutions = maxSolutions;
                this.regions = new int[size * size];
                for (int i = 0; i < this.regions.Length; i++)
                {
                    this.regions[i] = regions[i];
                }

                allColumns = (1 << size) - 1;
                regionColumnMasks = new int[size * size];
                for (int row = 0; row < size; row++)
                {
                    for (int column = 0; column < size; column++)
                    {
                        regionColumnMasks[row * size + this.regions[row * size + column]] |= 1 << column;
                    }
                }

                candidate = new int[size];
                answer = new int[size];
                candidateStack = new int[(size + 1) * size];
                answerStack = new int[(size + 1) * size];
                usedColumnStack = new int[size + 1];
                usedRegionStack = new int[size + 1];

                var bannedCat = new int[size];
                var bannedColumns = new int[size];
                Array.Fill(bannedCat, -1);
                if (fixes != null)
                {
                    for (int i = 0; i < fixes.Count; i++)
                    {
                        CellFix fix = fixes[i];
                        if (fix.IsCat)
                        {
                            bannedCat[fix.Row] = fix.Column;
                        }
                        else
                        {
                            bannedColumns[fix.Row] |= 1 << fix.Column;
                        }
                    }
                }

                for (int row = 0; row < size; row++)
                {
                    int mask = bannedCat[row] >= 0 ? 1 << bannedCat[row] : allColumns;
                    mask &= ~bannedColumns[row];
                    candidate[row] = mask;
                    answer[row] = -1;
                }
            }

            public List<int[]> Run()
            {
                SearchRows(0);
                return aborted ? null : solutions;
            }

            private void SearchRows(int depth)
            {
                if (aborted || solutions.Count >= maxSolutions)
                {
                    return;
                }

                if (!Propagate())
                {
                    return;
                }

                int filled = 0;
                for (int row = 0; row < size; row++)
                {
                    if (answer[row] != -1)
                    {
                        filled++;
                    }
                }

                if (filled == size)
                {
                    solutions.Add((int[])answer.Clone());
                    return;
                }

                int bestRow = -1;
                int bestCount = int.MaxValue;
                int bestMask = 0;
                for (int row = 0; row < size; row++)
                {
                    if (answer[row] != -1)
                    {
                        continue;
                    }

                    int count = PopCount(candidate[row]);
                    if (count < bestCount)
                    {
                        bestCount = count;
                        bestRow = row;
                        bestMask = candidate[row];
                        if (count == 1)
                        {
                            break;
                        }
                    }
                }

                if (bestRow < 0)
                {
                    return;
                }

                SaveState(depth);
                while (bestMask != 0)
                {
                    int column = LowestColumn(bestMask);
                    bestMask &= bestMask - 1;
                    if (++nodes > nodeLimit)
                    {
                        aborted = true;
                        return;
                    }

                    RestoreState(depth);
                    Place(bestRow, column);
                    SearchRows(depth + 1);
                    if (aborted || solutions.Count >= maxSolutions)
                    {
                        return;
                    }
                }
            }

            private bool Propagate()
            {
                bool changed = true;
                while (changed)
                {
                    changed = false;
                    for (int row = 0; row < size; row++)
                    {
                        if (answer[row] != -1)
                        {
                            continue;
                        }

                        int mask = candidate[row] & ~usedColumns;
                        for (int region = 0; region < size; region++)
                        {
                            if ((usedRegions & (1 << region)) != 0)
                            {
                                mask &= ~regionColumnMasks[row * size + region];
                            }
                        }

                        if (row > 0 && answer[row - 1] != -1)
                        {
                            mask &= ~NeighbourMask(answer[row - 1]);
                        }

                        if (row < size - 1 && answer[row + 1] != -1)
                        {
                            mask &= ~NeighbourMask(answer[row + 1]);
                        }

                        mask &= allColumns;
                        if (mask != candidate[row])
                        {
                            candidate[row] = mask;
                            changed = true;
                        }

                        if (mask == 0)
                        {
                            return false;
                        }
                    }

                    switch (FindForced(out int forcedRow, out int forcedColumn))
                    {
                        case ForcedResult.Contradiction:
                            return false;
                        case ForcedResult.Found:
                            Place(forcedRow, forcedColumn);
                            changed = true;
                            break;
                    }
                }

                return true;
            }

            private ForcedResult FindForced(out int row, out int column)
            {
                for (int r = 0; r < size; r++)
                {
                    int mask = candidate[r];
                    if (answer[r] == -1 && mask != 0 && (mask & (mask - 1)) == 0)
                    {
                        row = r;
                        column = LowestColumn(mask);
                        return ForcedResult.Found;
                    }
                }

                for (int c = 0; c < size; c++)
                {
                    if ((usedColumns & (1 << c)) != 0)
                    {
                        continue;
                    }

                    int count = CountColumnCandidates(c, out int who);
                    if (count == 0)
                    {
                        row = column = -1;
                        return ForcedResult.Contradiction;
                    }

                    if (count == 1)
                    {
                        row = who;
                        column = c;
                        return ForcedResult.Found;
                    }
                }

                for (int region = 0; region < size; region++)
                {
                    if ((usedRegions & (1 << region)) != 0)
                    {
                        continue;
                    }

                    int count = CountRegionCandidates(region, out int regionRow, out int regionColumn);
                    if (count == 0)
                    {
                        row = column = -1;
                        return ForcedResult.Contradiction;
                    }

                    if (count == 1)
                    {
                        row = regionRow;
                        column = regionColumn;
                        return ForcedResult.Found;
                    }
                }

                row = column = -1;
                return ForcedResult.None;
            }

            private int CountColumnCandidates(int column, out int firstRow)
            {
                int count = 0;
                firstRow = -1;
                for (int row = 0; row < size && count <= 1; row++)
                {
                    if (answer[row] == -1 && (candidate[row] & (1 << column)) != 0)
                    {
                        count++;
                        firstRow = row;
                    }
                }

                return count;
            }

            private int CountRegionCandidates(int region, out int firstRow, out int firstColumn)
            {
                int count = 0;
                firstRow = -1;
                firstColumn = -1;
                for (int row = 0; row < size && count <= 1; row++)
                {
                    if (answer[row] != -1)
                    {
                        continue;
                    }

                    int mask = candidate[row] & regionColumnMasks[row * size + region];
                    while (mask != 0)
                    {
                        int column = LowestColumn(mask);
                        mask &= mask - 1;
                        count++;
                        firstRow = row;
                        firstColumn = column;
                        if (count > 1)
                        {
                            break;
                        }
                    }
                }

                return count;
            }

            private void Place(int row, int column)
            {
                answer[row] = column;
                candidate[row] = 0;
                usedColumns |= 1 << column;
                usedRegions |= 1 << regions[row * size + column];
            }

            private void SaveState(int depth)
            {
                Array.Copy(candidate, 0, candidateStack, depth * size, size);
                Array.Copy(answer, 0, answerStack, depth * size, size);
                usedColumnStack[depth] = usedColumns;
                usedRegionStack[depth] = usedRegions;
            }

            private void RestoreState(int depth)
            {
                Array.Copy(candidateStack, depth * size, candidate, 0, size);
                Array.Copy(answerStack, depth * size, answer, 0, size);
                usedColumns = usedColumnStack[depth];
                usedRegions = usedRegionStack[depth];
            }

            private int NeighbourMask(int column)
            {
                int mask = 1 << column;
                if (column - 1 >= 0)
                {
                    mask |= 1 << (column - 1);
                }

                if (column + 1 < size)
                {
                    mask |= 1 << (column + 1);
                }

                return mask;
            }

            private enum ForcedResult
            {
                None,
                Found,
                Contradiction
            }

            private static int PopCount(int value)
            {
                int count = 0;
                while (value != 0)
                {
                    value &= value - 1;
                    count++;
                }

                return count;
            }

            private static int LowestColumn(int mask)
            {
                int index = 0;
                while ((mask & 1) == 0)
                {
                    mask >>= 1;
                    index++;
                }

                return index;
            }
        }
    }
}
