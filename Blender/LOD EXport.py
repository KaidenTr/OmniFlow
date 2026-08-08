import bpy
import os
from mathutils import Vector

bl_info = {
    "name": "Export LOD Groups for Unity",
    "author": "kaiden",
    "version": (1, 5),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Export LOD Groups",
    "description": "Exports individual LOD parent objects from collections",
    "category": "Import-Export",
}

class OBJECT_OT_export_lod_groups(bpy.types.Operator):
    bl_idname = "object.export_lod_groups"
    bl_label = "Export LOD Groups"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory: bpy.props.StringProperty(subtype='DIR_PATH')
    export_format: bpy.props.EnumProperty(
        items=[
            ('FBX', "FBX", "Export as FBX"),
            ('GLB', "GLTF Binary", "Export as GLB"),
        ],
        name="Format",
        default='FBX'
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        # Get all collections in the scene
        collections = [col for col in bpy.data.collections if col.objects]
        
        if not collections:
            self.report({'WARNING'}, "No collections found")
            return {'CANCELLED'}
        
        # Store original selection
        original_selection = context.selected_objects
        original_active = context.active_object
        
        # Create export directory if it doesn't exist
        os.makedirs(self.directory, exist_ok=True)
        
        exported_files = []
        
        for collection in collections:
            # Find LOD parent objects in collection (objects with "_LODParent" in name)
            lod_parents = [obj for obj in collection.objects if "_LODParent" in obj.name or "_LODGroup" in obj.name]
            
            for parent in lod_parents:
                # Select only this parent and its children
                bpy.ops.object.select_all(action='DESELECT')
                parent.select_set(True)
                for child in parent.children:
                    child.select_set(True)
                
                # Set export path
                export_path = os.path.join(self.directory, f"{parent.name}.{self.export_format.lower()}")
                
                # Export based on selected format
                if self.export_format == 'FBX':
                    bpy.ops.export_scene.fbx(
                        filepath=export_path,
                        use_selection=True,
                        apply_scale_options='FBX_SCALE_UNITS',
                        bake_space_transform=True,
                        object_types={'EMPTY', 'MESH'},
                        use_mesh_modifiers=True,
                        mesh_smooth_type='FACE'
                    )
                elif self.export_format == 'GLB':
                    bpy.ops.export_scene.gltf(
                        filepath=export_path,
                        export_format='GLB',
                        export_selected=True,
                        export_apply=True
                    )
                
                exported_files.append(export_path)
        
        # Restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selection:
            obj.select_set(True)
        context.view_layer.objects.active = original_active
        
        self.report({'INFO'}, f"Exported {len(exported_files)} LOD groups to {self.directory}")
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_export_lod_groups.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_export_lod_groups)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_export_lod_groups)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()