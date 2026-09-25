using System;

namespace DragonFinder.Domain
{
    public enum RoundPhase
    {
        Playing,
        Won,
        Lost
    }

    public enum CellActionKind
    {
        Ignored,
        Marked,
        Unmarked,
        Caught,
        Missed,
        Won,
        Lost
    }

    public readonly struct CellAction
    {
        public CellAction(CellActionKind kind, int index)
        {
            Kind = kind;
            Index = index;
        }

        public CellActionKind Kind { get; }
        public int Index { get; }
    }

    public sealed class GameSession
    {
        private readonly bool[] marked;
        private readonly bool[] revealed;

        public GameSession(BoardPuzzle puzzle, bool timed)
        {
            Puzzle = puzzle ?? throw new ArgumentNullException(nameof(puzzle));
            Timed = timed;
            InitialSeconds = timed ? puzzle.Size * 30 : 0;
            RemainingSeconds = InitialSeconds;
            CatchersLeft = puzzle.Size + 3;
            marked = new bool[puzzle.Size * puzzle.Size];
            revealed = new bool[marked.Length];
            Phase = RoundPhase.Playing;
        }

        public BoardPuzzle Puzzle { get; }
        public bool Timed { get; }
        public int CatchersLeft { get; private set; }
        public int Found { get; private set; }
        public bool CatcherMode { get; private set; }
        public double InitialSeconds { get; }
        public double RemainingSeconds { get; private set; }
        public RoundPhase Phase { get; private set; }

        public bool IsMarked(int index) => index >= 0 && index < marked.Length && marked[index];
        public bool IsRevealed(int index) => index >= 0 && index < revealed.Length && revealed[index];

        public void SetCatcherMode(bool enabled)
        {
            CatcherMode = Phase == RoundPhase.Playing && CatchersLeft > 0 && enabled;
        }

        public CellAction ExecuteCell(int index)
        {
            if (CatcherMode)
            {
                return Capture(index);
            }

            return ToggleMark(index);
        }

        public CellAction ToggleMark(int index)
        {
            if (!CanUse(index) || revealed[index])
            {
                return new CellAction(CellActionKind.Ignored, index);
            }

            marked[index] = !marked[index];
            return new CellAction(marked[index] ? CellActionKind.Marked : CellActionKind.Unmarked, index);
        }

        public CellAction Capture(int index)
        {
            if (!CanUse(index) || revealed[index] || CatchersLeft <= 0)
            {
                return new CellAction(CellActionKind.Ignored, index);
            }

            CatchersLeft--;
            if (Puzzle.IsAnswerCell(index))
            {
                revealed[index] = true;
                marked[index] = false;
                Found++;
                if (Timed)
                {
                    RemainingSeconds = Math.Min(InitialSeconds, RemainingSeconds + 30);
                }

                if (Found >= Puzzle.Size)
                {
                    Phase = RoundPhase.Won;
                    CatcherMode = false;
                    return new CellAction(CellActionKind.Won, index);
                }

                return new CellAction(CellActionKind.Caught, index);
            }

            marked[index] = true;
            if (CatchersLeft <= 0)
            {
                Phase = RoundPhase.Lost;
                CatcherMode = false;
                return new CellAction(CellActionKind.Lost, index);
            }

            return new CellAction(CellActionKind.Missed, index);
        }

        public void Tick(double deltaSeconds, bool paused)
        {
            if (!Timed || paused || Phase != RoundPhase.Playing || deltaSeconds <= 0)
            {
                return;
            }

            RemainingSeconds = Math.Max(0, RemainingSeconds - deltaSeconds);
            if (RemainingSeconds <= 0)
            {
                Phase = RoundPhase.Lost;
                CatcherMode = false;
            }
        }

        private bool CanUse(int index)
        {
            return Phase == RoundPhase.Playing && index >= 0 && index < marked.Length;
        }
    }
}
