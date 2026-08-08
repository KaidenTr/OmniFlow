using UnityEngine;
using UnityEditor;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

public class MochiePackedAssigner : EditorWindow
{
    [MenuItem("Tools/Daz3D/Root Name Fix (Final)")]
    public static void AssignMochiePackedMapsRecursive()
    {
        string rootPath = GetSelectedPath();
        if (string.IsNullOrEmpty(rootPath))
        {
            EditorUtility.DisplayDialog("Error", "Please select the root folder containing Materials and Exports.", "OK");
            return;
        }

        // 1. Get all textures in the folder
        string[] allTexGuids = AssetDatabase.FindAssets("t:Texture", new[] { rootPath });
        var texturePaths = allTexGuids.Select(guid => AssetDatabase.GUIDToAssetPath(guid)).ToList();

        int assignedCount = 0;
        string[] matGuids = AssetDatabase.FindAssets("t:Material", new[] { rootPath });
        
        foreach (string guid in matGuids)
        {
            string matPath = AssetDatabase.GUIDToAssetPath(guid);
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
            if (mat == null) continue;

            // 2. ROOT NAME LOGIC: 
            string cleanName = mat.name;
            if (cleanName.Contains("__"))
            {
                // We take everything before the LAST __
                // Example: Group_...Dirt.002__PBR_Diffuse -> Group_...Dirt.002
                int lastIndex = cleanName.LastIndexOf("__");
                cleanName = cleanName.Substring(0, lastIndex);
            }
            
            // FIXED: Removed the Regex line that was deleting the ".002" suffix.
            // This ensures .002 material looks for .002 texture.
            string searchName = cleanName.ToLower();

            // 3. SEARCH: Find a texture that starts with the full Root Name (including .002)
            string matchedTexPath = texturePaths.FirstOrDefault(path => {
                string fileName = Path.GetFileName(path).ToLower();
                // We check if it starts with the root name and is followed by the packed indicator
                return fileName.StartsWith(searchName) && fileName.Contains("packedtex");
            });

            if (!string.IsNullOrEmpty(matchedTexPath))
            {
                Texture2D packedTex = AssetDatabase.LoadAssetAtPath<Texture2D>(matchedTexPath);

                if (packedTex != null)
                {
                    Undo.RecordObject(mat, "Assign Mochie Packed Map");

                    mat.SetTexture("_PackedMap", packedTex);
                    mat.SetInt("_PrimaryWorkflow", 1); 
                    mat.EnableKeyword("_WORKFLOW_PACKED_ON");
                    
                    mat.SetInt("_RoughnessChannel", 1); // Green
                    mat.SetInt("_MetallicChannel", 2);  // Blue
                    mat.SetInt("_OcclusionChannel", 0); // Red

                    EditorUtility.SetDirty(mat);
                    assignedCount++;
                    Debug.Log($"<color=green>SUCCESS:</color> Mat [{mat.name}] -> [{Path.GetFileName(matchedTexPath)}]");
                }
            }
            else
            {
                if(mat.name.Contains("Group_"))
                    Debug.LogWarning($"<color=orange>NOT FOUND:</color> Search term [{searchName}] for Material [{mat.name}]");
            }
        }

        AssetDatabase.SaveAssets();
        EditorUtility.DisplayDialog("Daz3D Matcher", $"Matched {assignedCount} materials!", "OK");
    }

    private static string GetSelectedPath()
    {
        var obj = Selection.activeObject;
        if (obj == null) return null;
        string path = AssetDatabase.GetAssetPath(obj.GetInstanceID());
        return Directory.Exists(path) ? path : Path.GetDirectoryName(path);
    }
}