using UnityEngine;
using UnityEditor;
using System.IO;

public class MaterialAssigner : EditorWindow
{
    // Define common suffixes for texture types. Case-insensitive.
    private static readonly string[] albedoSuffixes = { "_albedo", "_diffuse", "_dif", "_color", "_basecolor" };
    private static readonly string[] normalSuffixes = { "_normal", "_norm", "_nrm", "_bump", "_bumpmap" };

    [MenuItem("Tools/Assign Materials From Folder")]
    public static void ShowWindow()
    {
        AssignMaterials();
    }

    private static void AssignMaterials()
    {
        // 1. Look at the selected objects
        GameObject[] selectedObjects = Selection.gameObjects;

        if (selectedObjects.Length == 0)
        {
            EditorUtility.DisplayDialog("No Objects Selected", "Please select one or more GameObjects in the Hierarchy or Scene view.", "OK");
            return;
        }

        // 2. Ask user for the root folder (subfolders will be searched)
        string folderPath = EditorUtility.OpenFolderPanel("Select Root Texture Folder (subfolders will be searched)", "Assets", "");

        if (string.IsNullOrEmpty(folderPath))
        {
            // User cancelled the folder selection
            return;
        }

        // Convert absolute path to a relative Unity path (e.g., "Assets/MyTextures")
        if (!folderPath.StartsWith(Application.dataPath))
        {
            EditorUtility.DisplayDialog("Invalid Folder", "Please select a folder that is inside your project's 'Assets' directory.", "OK");
            return;
        }
        string relativePath = "Assets" + folderPath.Substring(Application.dataPath.Length);

        // Find all texture paths within the selected folder AND its subfolders
        string[] allTexturePaths = Directory.GetFiles(relativePath, "*.*", SearchOption.AllDirectories);
        
        // Batch asset operations for performance
        AssetDatabase.StartAssetEditing();

        try
        {
            // Create a "Materials" subfolder in the root if it doesn't exist
            string materialsFolderPath = Path.Combine(relativePath, "Materials");
            if (!AssetDatabase.IsValidFolder(materialsFolderPath))
            {
                AssetDatabase.CreateFolder(relativePath, "Materials");
            }

            foreach (GameObject obj in selectedObjects)
            {
                ProcessGameObject(obj, allTexturePaths, materialsFolderPath);
            }
        }
        finally
        {
            // Ensure we stop asset editing even if an error occurs
            AssetDatabase.StopAssetEditing();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
        }

        EditorUtility.DisplayDialog("Process Complete", $"Successfully processed {selectedObjects.Length} object(s).\nSearched for textures in the selected folder and all its subfolders.", "OK");
    }

    private static void ProcessGameObject(GameObject obj, string[] allTexturePaths, string materialsFolderPath)
    {
        Renderer renderer = obj.GetComponent<Renderer>();
        if (renderer == null)
        {
            Debug.LogWarning($"Skipping '{obj.name}' because it has no Renderer component.", obj);
            return;
        }

        // 3. Create a new material
        Material newMaterial = new Material(Shader.Find("Standard")); // Use Standard shader by default. Adjust if you use URP/HDRP
        // For URP: Shader.Find("Universal Render Pipeline/Lit")
        // For HDRP: Shader.Find("HDRP/Lit")

        // Find textures from the pre-compiled list that match the object's name
        foreach (string texturePath in allTexturePaths)
        {
            string fileName = Path.GetFileNameWithoutExtension(texturePath).ToLowerInvariant();
            string objectNameLower = obj.name.ToLowerInvariant();

            // Check if the texture name starts with the object name
            if (fileName.StartsWith(objectNameLower))
            {
                // 4. Look for and apply textures based on naming convention
                Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
                if (texture == null) continue;

                // Check for Albedo/Diffuse
                foreach (string suffix in albedoSuffixes)
                {
                    if (fileName.Contains(suffix))
                    {
                        newMaterial.SetTexture("_BaseMap", texture); // URP/HDRP Lit shader
                        newMaterial.SetTexture("_MainTex", texture); // Standard Built-in shader
                        Debug.Log($"Applied Albedo: '{Path.GetFileName(texturePath)}' to '{obj.name}' material.", obj);
                        break;
                    }
                }

                // Check for Normal Map
                foreach (string suffix in normalSuffixes)
                {
                    if (fileName.Contains(suffix))
                    {
                        // Ensure the texture is correctly marked as a Normal Map
                        SetTextureAsNormalMap(texturePath);
                        newMaterial.SetTexture("_BumpMap", texture); // For all pipelines
                        newMaterial.EnableKeyword("_NORMALMAP");
                        Debug.Log($"Applied Normal Map: '{Path.GetFileName(texturePath)}' to '{obj.name}' material.", obj);
                        break;
                    }
                }
            }
        }
        
        // Save the new material as an asset
        string materialPath = Path.Combine(materialsFolderPath, $"{obj.name}_Material.mat");
        materialPath = AssetDatabase.GenerateUniqueAssetPath(materialPath);
        AssetDatabase.CreateAsset(newMaterial, materialPath);
        
        // Apply the new material to the object
        renderer.sharedMaterial = newMaterial;
        Debug.Log($"Created and assigned material at '{materialPath}' for object '{obj.name}'.", obj);
    }

    private static void SetTextureAsNormalMap(string assetPath)
    {
        TextureImporter textureImporter = AssetImporter.GetAtPath(assetPath) as TextureImporter;
        if (textureImporter != null && textureImporter.textureType != TextureImporterType.NormalMap)
        {
            textureImporter.textureType = TextureImporterType.NormalMap;
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceUpdate);
        }
    }
}