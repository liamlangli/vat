using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEditor;

[System.Serializable]
struct Box
{
    public float[] min;
    public float[] max;
}

[System.Serializable]
struct Meta
{
    public int width;
    public int height;
    public Box box;
}

public class create_vat_mesh
{
    [MenuItem("VAT/Create VAT Mesh")]
    private static void Create()
    {
        var active = Selection.activeObject;
        if (active is Texture2D) {
            var texture = active as Texture2D;
            var texturePath = AssetDatabase.GetAssetPath(texture);
            var vertexCount = texture.width - (texture.width % 3);
            var indices = new ushort[vertexCount];
            var normals = new Vector3[vertexCount];
            var vertices = new Vector3[vertexCount];

            for (int i = 0; i < vertexCount; ++i)
            {
                normals[i] = new Vector3();
                vertices[i] = new Vector3();
                indices[i] = (ushort)i;
            }

            var mesh = new Mesh();
            mesh.vertices = vertices;
            mesh.normals = normals;
            mesh.SetIndices(indices, MeshTopology.Triangles, 0, false);

            var dir = Path.GetDirectoryName(texturePath);
            var metaJson = File.ReadAllText(Path.Join(dir, "meta.json"));
            var meta = JsonUtility.FromJson<Meta>(metaJson);

            var bounds = new Bounds();
            bounds.min = new Vector3(meta.box.min[0], meta.box.min[1], meta.box.min[2]);
            bounds.max = new Vector3(meta.box.max[0], meta.box.max[1], meta.box.max[2]);

            mesh.bounds = bounds;

            var meshPath = Path.Join(dir, Path.GetFileNameWithoutExtension(texturePath) + "_mesh.asset");
            if (File.Exists(meshPath)) {
                File.Delete(meshPath);
            }

            AssetDatabase.CreateAsset(mesh, meshPath);
            AssetDatabase.SaveAssets();
        }
        else
        {
            Debug.Log("please select vat texture");
        }
    }
}
