using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(MeshFilter))]
public class MeshInfoEditor : Editor
{
    public override void OnInspectorGUI()
    {
        base.OnInspectorGUI();

        MeshFilter mf = (MeshFilter)target;
        Mesh mesh = mf.sharedMesh;

        if (mesh != null)
        {
            int triangleCount = mesh.triangles.Length / 3;
            int vertexCount = mesh.vertexCount;

            EditorGUILayout.LabelField("Polygon Info", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Triangles:", triangleCount.ToString());
            EditorGUILayout.LabelField("Vertices:", vertexCount.ToString());
        }
    }
}
