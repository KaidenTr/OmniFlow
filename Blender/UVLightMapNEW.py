bl_info = {
    "name": "Auto Lightmap UV",
    "author": "K (Edited)",
    "version": (1, 4),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > UV Tools",
    "description": "Creates LightmapUVs using Angle Based Unwrap",
    "category": "UV"
}

import bpy

class AutoLightmapUV(bpy.types.Operator):
    """Automatically generate Lightmap UVs with Angle Based Unwrap"""
    bl_idname = "object.auto_lightmap_uv"
    bl_label = "Auto Lightmap UV"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        
        for obj in selected_objects:
            if obj.type == 'MESH':
                bpy.ops.object.select_all(action='DESELECT')
                
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

                uv_map_name = "LightmapUV"
                uv_layers = obj.data.uv_layers

                if uv_map_name not in [uv.name for uv in uv_layers]:
                    uv_layers.new(name=uv_map_name)

                obj.data.uv_layers.active = uv_layers[uv_map_name]

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                # 🔁 REPLACED THIS LINE:
                # bpy.ops.uv.smart_project()

                # ✅ Angle Based Unwrap
                bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)

                bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class AutoLightmapUVPanel(bpy.types.Panel):
    bl_label = "Lightmap UV Generator"
    bl_idname = "OBJECT_PT_auto_lightmap_uv"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "UV Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.auto_lightmap_uv")


def register():
    bpy.utils.register_class(AutoLightmapUV)
    bpy.utils.register_class(AutoLightmapUVPanel)


def unregister():
    bpy.utils.unregister_class(AutoLightmapUV)
    bpy.utils.unregister_class(AutoLightmapUVPanel)


if __name__ == "__main__":
    register()