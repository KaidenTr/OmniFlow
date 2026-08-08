In Blender
1. Select all objects, separate materials
2. With all objects selected, on the right panel (V), use UV Tools to generate Auto Light Map UV.
4. Use Simple Bake to export models and PBR textures. Use packedTex to combine Metalness, Roughness, and Ambient Occlusion.  (Tips: locate the Unity Project asset folder, and export to it directly)


In Unity
5. Place the models into the scene
6. Select all models, on top menu "tools", use  Materials Export. (Tips: make a dedicated folder for the materials only)
7. Go to folder contains all extracted materials, select all and change materials to Mochie shader standard
8. Update the all selected materials properties: Workflow from separated to packed, Check on Bakery light map and select desired light map mode (Prefer MonoSH) 
9. To mass apply packedTex, use the tools menu select Mochi pack assigners
10. Ensure have the objects all static and ready to proceed light baking the scene!
