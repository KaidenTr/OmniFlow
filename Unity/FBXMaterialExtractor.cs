using UnityEditor;
using UnityEngine;
using System.IO;
using System.Linq;

public class FBXMaterialExtractor : EditorWindow
{
    private string sourceFolder = "Assets/Models";
    private string targetFolder = "Assets/ExtractedMaterials";

    [MenuItem("Tools/Extract FBX Materials")]
    public static void ShowWindow()
    {
        GetWindow(typeof(FBXMaterialExtractor));
    }

    void OnGUI()
    {
        GUILayout.Label("FBX Material Extractor", EditorStyles.boldLabel);
        sourceFolder = EditorGUILayout.TextField("Source Folder", sourceFolder);
        targetFolder = EditorGUILayout.TextField("Target Folder", targetFolder);

        if (GUILayout.Button("Extract Materials"))
        {
            ExtractAllMaterials();
        }
    }

    void ExtractAllMaterials()
    {
        string[] fbxPaths = Directory.GetFiles(sourceFolder, "*.fbx", SearchOption.AllDirectories);

        foreach (string fbxPath in fbxPaths)
        {
            string assetPath = fbxPath.Replace("\\", "/");

            ModelImporter importer = AssetImporter.GetAtPath(assetPath) as ModelImporter;
            if (importer != null)
            {
                importer.materialLocation = ModelImporterMaterialLocation.External;
                importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;

                string relativeTargetFolder = Path.Combine(targetFolder, Path.GetFileNameWithoutExtension(assetPath));
                Directory.CreateDirectory(relativeTargetFolder);

                AssetDatabase.WriteImportSettingsIfDirty(assetPath);
                AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceUpdate);

                Material[] materials = AssetDatabase.LoadAllAssetsAtPath(assetPath)
                    .OfType<Material>()
                    .ToArray();

                foreach (Material mat in materials)
                {
                    string matPath = Path.Combine(relativeTargetFolder, mat.name + ".mat");
                    AssetDatabase.CreateAsset(Object.Instantiate(mat), matPath);
                }
            }
        }

        AssetDatabase.Refresh();
        Debug.Log("Material extraction complete.");
    }
}
