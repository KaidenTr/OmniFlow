bl_info = {
    "name": "Keep Render UV Map Only",
    "author": "Kaiden",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > UV Tools",
    "description": "Deletes all UV maps except the one with the camera icon (render UV)",
    "category": "UV"
}

import bpy

class OBJECT_OT_keep_render_uv(bpy.types.Operator):
    """Keep only the UV map marked with the camera icon"""
    bl_idname = "object.keep_render_uv"
    bl_label = "Keep Render UV Only"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            uv_layers = obj.data.uv_layers
            if not uv_layers:
                continue

            # Find the render UV (camera icon)
            render_uv = None
            for uv in uv_layers:
                if uv.active_render:
                    render_uv = uv
                    break

            if not render_uv:
                self.report({'WARNING'}, f"{obj.name}: No render UV found")
                continue

            # Remove all others
            to_remove = [uv for uv in uv_layers if uv != render_uv]

            for uv in to_remove:
                uv_layers.remove(uv)

            self.report({'INFO'}, f"{obj.name}: kept '{render_uv.name}'")

        return {'FINISHED'}


class OBJECT_PT_keep_render_uv_panel(bpy.types.Panel):
    bl_label = "UV Cleanup"
    bl_idname = "OBJECT_PT_keep_render_uv_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "UV Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.keep_render_uv", icon='RESTRICT_RENDER_OFF')


def register():
    bpy.utils.register_class(OBJECT_OT_keep_render_uv)
    bpy.utils.register_class(OBJECT_PT_keep_render_uv_panel)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_keep_render_uv)
    bpy.utils.unregister_class(OBJECT_PT_keep_render_uv_panel)


if __name__ == "__main__":
    register()