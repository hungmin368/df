using System;
using System.Collections.Generic;
using System.IO;
using DragonFinder.Domain;
using DragonFinder.Runtime.Data;
using UnityEditor;
using UnityEngine;

namespace DragonFinder.Editor
{
    public static class DragonContentImporter
    {
        private const string SourcePath = "Assets/DragonFinder/Editor/ImportSource/content.v1.json";
        private const string OutputPath = "Assets/DragonFinder/Resources/Content";

        [MenuItem("Tools/Dragon Finder/Import Content")]
        public static void ImportContent()
        {
            ContentSource source = JsonUtility.FromJson<ContentSource>(File.ReadAllText(SourcePath));
            Validate(source);
            Directory.CreateDirectory(Path.Combine(OutputPath, "Dragons"));
            AssetDatabase.Refresh();

            var definitions = new List<DragonDefinition>();
            foreach (DragonSource dragon in source.dragons)
            {
                string path = $"{OutputPath}/Dragons/{dragon.id}.asset";
                DragonDefinition definition = AssetDatabase.LoadAssetAtPath<DragonDefinition>(path);
                if (definition == null)
                {
                    definition = ScriptableObject.CreateInstance<DragonDefinition>();
                    AssetDatabase.CreateAsset(definition, path);
                }

                definition.Initialize(dragon.id, dragon.displayName, dragon.stars, dragon.colorHtml, dragon.accessibilityLabel);
                EditorUtility.SetDirty(definition);
                definitions.Add(definition);
            }

            DragonCatalog catalog = LoadOrCreate<DragonCatalog>($"{OutputPath}/DragonCatalog.asset");
            catalog.Initialize(definitions);
            EditorUtility.SetDirty(catalog);

            TutorialBoardDefinition tutorial = LoadOrCreate<TutorialBoardDefinition>($"{OutputPath}/TutorialBoard.asset");
            tutorial.Initialize(source.tutorial.size, source.tutorial.regions, source.tutorial.answerColumns, source.tutorial.safeCell);
            EditorUtility.SetDirty(tutorial);

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
        }

        private static T LoadOrCreate<T>(string path) where T : ScriptableObject
        {
            T asset = AssetDatabase.LoadAssetAtPath<T>(path);
            if (asset != null)
            {
                return asset;
            }

            asset = ScriptableObject.CreateInstance<T>();
            AssetDatabase.CreateAsset(asset, path);
            return asset;
        }

        private static void Validate(ContentSource source)
        {
            if (source == null || source.schemaVersion != 1)
            {
                throw new InvalidDataException("Content schemaVersion must be 1.");
            }

            if (source.dragons == null || source.dragons.Length < 6 || source.dragons.Length > 12)
            {
                throw new InvalidDataException("Content must contain 6 to 12 dragons.");
            }

            var ids = new HashSet<string>(StringComparer.Ordinal);
            int lowStarCount = 0;
            foreach (DragonSource dragon in source.dragons)
            {
                if (string.IsNullOrWhiteSpace(dragon.id) || !ids.Add(dragon.id))
                {
                    throw new InvalidDataException("Dragon IDs must be non-empty and unique.");
                }

                if (string.IsNullOrWhiteSpace(dragon.displayName) || dragon.stars < 1 || dragon.stars > 5)
                {
                    throw new InvalidDataException($"Dragon {dragon.id} has invalid display data.");
                }

                if (!ColorUtility.TryParseHtmlString(dragon.colorHtml, out _))
                {
                    throw new InvalidDataException($"Dragon {dragon.id} has an invalid color.");
                }

                if (dragon.stars <= 2)
                {
                    lowStarCount++;
                }
            }

            if (lowStarCount < 5)
            {
                throw new InvalidDataException("The tutorial requires at least five one- or two-star dragons.");
            }

            TutorialSource tutorial = source.tutorial ?? throw new InvalidDataException("Tutorial data is missing.");
            var puzzle = new BoardPuzzle(tutorial.size, tutorial.regions, tutorial.answerColumns);
            int solutionCount = BoardSolver.CountSolutions(puzzle.Size, puzzle.Regions, 2, out _);
            if (solutionCount != 1 || tutorial.safeCell < 0 || tutorial.safeCell >= tutorial.size * tutorial.size || puzzle.IsAnswerCell(tutorial.safeCell))
            {
                throw new InvalidDataException("Tutorial puzzle must have one solution and a safe highlighted cell.");
            }
        }

        [Serializable]
        private sealed class ContentSource
        {
            public int schemaVersion;
            public DragonSource[] dragons;
            public TutorialSource tutorial;
        }

        [Serializable]
        private sealed class DragonSource
        {
            public string id;
            public string displayName;
            public int stars;
            public string colorHtml;
            public string accessibilityLabel;
        }

        [Serializable]
        private sealed class TutorialSource
        {
            public int size;
            public int[] regions;
            public int[] answerColumns;
            public int safeCell;
        }
    }
}
