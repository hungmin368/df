using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace DragonFinder.Editor
{
    public static class WindowsBuild
    {
        [MenuItem("Tools/Dragon Finder/Build Windows x64")]
        public static void BuildRelease()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)?.FullName ?? throw new InvalidOperationException("Project root was not found.");
            string outputDirectory = Path.Combine(projectRoot, "Builds", "Windows");
            Directory.CreateDirectory(outputDirectory);

            var options = new BuildPlayerOptions
            {
                scenes = new[] { "Assets/DragonFinder/Scenes/Main.unity" },
                locationPathName = Path.Combine(outputDirectory, "DragonFinder.exe"),
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            };

            BuildReport report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
            {
                throw new BuildFailedException($"Windows build failed: {report.summary.result}");
            }

            Debug.Log($"Windows build completed: {report.summary.outputPath}");
        }
    }
}
