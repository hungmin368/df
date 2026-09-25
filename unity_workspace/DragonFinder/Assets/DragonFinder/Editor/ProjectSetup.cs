using System.IO;
using DragonFinder.Runtime.Presentation;
using TMPro;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace DragonFinder.Editor
{
    public static class ProjectSetup
    {
        private const string ScenePath = "Assets/DragonFinder/Scenes/Main.unity";
        private const string PipelinePath = "Assets/DragonFinder/Settings/DragonFinderURP.asset";
        private const string RendererPath = "Assets/DragonFinder/Settings/DragonFinder2DRenderer.asset";
        private const string TMPSettingsPath = "Assets/TextMesh Pro/Resources/TMP Settings.asset";

        [MenuItem("Tools/Dragon Finder/Configure Project")]
        public static void Configure()
        {
            ImportTextMeshProResources();
            DragonContentImporter.ImportContent();
            ConfigureRenderPipeline();
            ConfigurePlayer();
            CreateMainScene();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
        }

        private static void ImportTextMeshProResources()
        {
            if (AssetDatabase.LoadAssetAtPath<TMP_Settings>(TMPSettingsPath) != null)
            {
                return;
            }

            TMP_PackageResourceImporter.ImportResources(true, false, false);
            AssetDatabase.Refresh();

            // Unity imports packages asynchronously, so a batch run reports the files only on the next launch.
            if (AssetDatabase.LoadAssetAtPath<TMP_Settings>(TMPSettingsPath) == null)
            {
                throw new InvalidDataException(
                    "TextMeshPro Essential Resources are missing. Import \"Package Resources/TMP Essential Resources.unitypackage\" " +
                    "from the com.unity.ugui package through the Unity command line (-importPackage) and run this setup again.");
            }
        }

        private static void ConfigureRenderPipeline()
        {
            Renderer2DData renderer = AssetDatabase.LoadAssetAtPath<Renderer2DData>(RendererPath);
            if (renderer == null)
            {
                renderer = ScriptableObject.CreateInstance<Renderer2DData>();
                AssetDatabase.CreateAsset(renderer, RendererPath);
            }

            UniversalRenderPipelineAsset pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(PipelinePath);
            if (pipeline == null)
            {
                pipeline = UniversalRenderPipelineAsset.Create(renderer);
                AssetDatabase.CreateAsset(pipeline, PipelinePath);
            }
            else
            {
                var serialized = new SerializedObject(pipeline);
                SerializedProperty renderers = serialized.FindProperty("m_RendererDataList");
                renderers.arraySize = 1;
                renderers.GetArrayElementAtIndex(0).objectReferenceValue = renderer;
                serialized.FindProperty("m_DefaultRendererIndex").intValue = 0;
                serialized.ApplyModifiedPropertiesWithoutUndo();
            }

            GraphicsSettings.defaultRenderPipeline = pipeline;
            QualitySettings.renderPipeline = pipeline;
            EditorUtility.SetDirty(renderer);
            EditorUtility.SetDirty(pipeline);
        }

        private static void ConfigurePlayer()
        {
            PlayerSettings.companyName = "Dragon Finder Studio";
            PlayerSettings.productName = "Dragon Finder";
            PlayerSettings.bundleVersion = "0.1.0";
            PlayerSettings.defaultScreenWidth = 1280;
            PlayerSettings.defaultScreenHeight = 720;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.resizableWindow = true;
            PlayerSettings.runInBackground = false;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.Mono2x);
            EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Standalone, BuildTarget.StandaloneWindows64);

            Object playerSettings = Unsupported.GetSerializedAssetInterfaceSingleton("PlayerSettings");
            var serialized = new SerializedObject(playerSettings);
            SerializedProperty inputHandler = serialized.FindProperty("activeInputHandler");
            if (inputHandler != null)
            {
                inputHandler.intValue = 1;
            }
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateMainScene()
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var cameraObject = new GameObject("Main Camera", typeof(Camera));
            cameraObject.tag = "MainCamera";
            Camera camera = cameraObject.GetComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color32(13, 23, 35, 255);
            camera.orthographic = true;
            cameraObject.transform.position = new Vector3(0, 0, -10);

            var bootstrap = new GameObject("AppBootstrap");
            bootstrap.AddComponent<AppBootstrap>();
            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        }
    }
}
