using System;
using System.Collections.Generic;

namespace DragonFinder.Runtime.Persistence
{
    [Serializable]
    public sealed class SaveDataV1
    {
        public int saveVersion = 1;
        public bool tutorialCompleted;
        public List<string> caughtDragonIds = new List<string>();
        public int totalWins;
        public int bestRemainingSeconds;
        public bool sfxEnabled = true;

        public static SaveDataV1 CreateDefault()
        {
            return new SaveDataV1();
        }
    }
}
