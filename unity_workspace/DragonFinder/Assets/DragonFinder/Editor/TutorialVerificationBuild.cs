using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace DragonFinder.Editor
{
    public static class TutorialVerificationBuild
    {
        public static void Build()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)?.FullName ?? throw new InvalidOperationException("Project root was not found.");
            string outputDirectory = Path.Combine(projectRoot, "Builds", "TutorialVerification");
            Directory.CreateDirectory(outputDirectory);

            var options = new BuildPlayerOptions
            {
                scenes = new[] { "Assets/DragonFinder/Scenes/Main.unity" },
                locationPathName = Path.Combine(outputDirectory, "DragonFinderTutorialVerify.exe"),
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.Development,
                extraScriptingDefines = new[] { "DF_TUTORIAL_VERIFY" }
            };

            BuildReport report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
            {
                throw new BuildFailedException($"Tutorial verification build failed: {report.summary.result}");
            }

            Debug.Log($"Tutorial verification build completed: {report.summary.outputPath}");
        }
    }
}
