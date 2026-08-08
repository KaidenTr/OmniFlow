import bpy
from mathutils import Vector

bl_info = {
    "name": "Auto LOD Generator for Unity",
    "author": "Kaiden",
    "version": (1, 4),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Auto LOD Generator for Unity",
    "description": "Generates LOD hierarchy ready for Unity with auto LOD configuration",
    "category": "Object",
}

# LOD configuration (percentage of screen height)
LOD_LEVELS = {
    "LOD0": 0.7,  # 50% screen height
    "LOD1": 0.5,  # 30%
    "LOD2": 0.25, # 15%
}

# Decimation ratios for each LOD
DECIMATION_RATIOS = {
    "LOD0": 1.0,   # No reduction
    "LOD1": 0.5,   # 50% reduction
    "LOD2": 0.25,   # 80% reduction
}

class OBJECT_OT_auto_lod_unity(bpy.types.Operator):
    bl_idname = "object.auto_lod_unity"
    bl_label = "Auto LOD Generator for Unity"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        for obj in selected:
            original_name = obj.name
            original_matrix = obj.matrix_world.copy()

            # Calculate the center of the original object's geometry in world space
            local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
            global_bbox_center = obj.matrix_world @ local_bbox_center

            # Create parent empty at the geometry center
            parent_empty = bpy.data.objects.new(original_name + "_LODGroup", None)
            context.collection.objects.link(parent_empty)
            parent_empty.location = global_bbox_center

            # Add custom properties for Unity LOD Group
            parent_empty["unity_LODGroup"] = True
            parent_empty["unity_LODLevels"] = len(LOD_LEVELS)
            
            # Store all created LODs to parent them at the end
            lod_objects = []

            for lod_label, decimation_ratio in DECIMATION_RATIOS.items():
                # Create new object
                new_obj = obj.copy()
                new_obj.data = obj.data.copy()
                new_obj.name = f"{original_name}_{lod_label}"
                context.collection.objects.link(new_obj)
                
                # Apply the original transform
                new_obj.matrix_world = original_matrix

                # Apply decimation if needed
                if decimation_ratio < 1.0:
                    mod = new_obj.modifiers.new(name="Decimate", type='DECIMATE')
                    mod.ratio = decimation_ratio
                    context.view_layer.objects.active = new_obj
                    bpy.ops.object.modifier_apply(modifier=mod.name)

                # Add LOD level custom property
                new_obj["unity_LODLevel"] = lod_label
                new_obj["unity_LODScreenHeight"] = LOD_LEVELS[lod_label]
                
                lod_objects.append(new_obj)

            # Parent all LODs to the empty while maintaining their world positions
            for lod_obj in lod_objects:
                lod_obj.parent = parent_empty
                lod_obj.matrix_parent_inverse = parent_empty.matrix_world.inverted()

            # Delete original mesh
            bpy.data.objects.remove(obj, do_unlink=True)

            # Add custom script for Unity auto-configuration
            self.add_unity_lod_script(parent_empty)

        self.report({'INFO'}, f"LODs created and configured for Unity with {len(LOD_LEVELS)} levels.")
        return {'FINISHED'}

    def add_unity_lod_script(self, parent_empty):
        """Adds a custom property that Unity can use to auto-configure LODs"""
        # These properties will be visible in Unity
        parent_empty["unity_autoConfigureLOD"] = True
        parent_empty["unity_LODScreenHeights"] = str(list(LOD_LEVELS.values()))
        
        # Add note for Unity import
        parent_empty["unity_note"] = (
            "This object contains LODs for Unity. "
            "Import with FBX exporter and Unity will automatically: "
            "1. Create LOD Group component "
            "2. Assign LOD meshes "
            "3. Set screen percentages"
        )

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_auto_lod_unity.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_auto_lod_unity)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_auto_lod_unity)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()