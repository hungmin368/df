using System;
using System.IO;
using UnityEngine;

namespace DragonFinder.Runtime.Persistence
{
    public sealed class JsonSaveRepository
    {
        private bool futureVersionLoaded;

        public JsonSaveRepository(string path = null)
        {
            FilePath = string.IsNullOrWhiteSpace(path)
                ? Path.Combine(Application.persistentDataPath, "dragonfinder.save.json")
                : path;
        }

        public string FilePath { get; }

        public SaveDataV1 Load()
        {
            futureVersionLoaded = false;
            if (!File.Exists(FilePath))
            {
                return SaveDataV1.CreateDefault();
            }

            try
            {
                string json = File.ReadAllText(FilePath);
                SaveDataV1 data = JsonUtility.FromJson<SaveDataV1>(json);
                if (data == null || data.saveVersion <= 0)
                {
                    PreserveCorruptFile();
                    return SaveDataV1.CreateDefault();
                }

                if (data.saveVersion > 1)
                {
                    futureVersionLoaded = true;
                    return SaveDataV1.CreateDefault();
                }

                data.caughtDragonIds ??= new System.Collections.Generic.List<string>();
                return data;
            }
            catch (Exception)
            {
                PreserveCorruptFile();
                return SaveDataV1.CreateDefault();
            }
        }

        public bool Save(SaveDataV1 data)
        {
            if (futureVersionLoaded || data == null || data.saveVersion != 1)
            {
                return false;
            }

            string directory = Path.GetDirectoryName(FilePath);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }

            string temporaryPath = FilePath + ".tmp";
            File.WriteAllText(temporaryPath, JsonUtility.ToJson(data, true));
            if (File.Exists(FilePath))
            {
                string backupPath = FilePath + ".bak";
                File.Replace(temporaryPath, FilePath, backupPath, true);
                if (File.Exists(backupPath))
                {
                    File.Delete(backupPath);
                }
            }
            else
            {
                File.Move(temporaryPath, FilePath);
            }

            return true;
        }

        private void PreserveCorruptFile()
        {
            try
            {
                string copyPath = FilePath + ".corrupt";
                File.Copy(FilePath, copyPath, true);
            }
            catch (IOException)
            {
            }
            catch (UnauthorizedAccessException)
            {
            }
        }
    }
}
