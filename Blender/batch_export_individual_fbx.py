bl_info = {
    "name": "Batch Export Individual FBX",
    "author": "kaiden",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Export",
    "description": "Export each selected mesh as individual FBX into its own folder",
    "category": "Import-Export",
}

import bpy
import os

class BatchExportFBXOperator(bpy.types.Operator):
    bl_idname = "export.batch_individual_fbx"
    bl_label = "Batch Export Individual FBX"

    def execute(self, context):
        export_path = context.scene.batch_export_path

        if not export_path:
            self.report({'ERROR'}, "No export path selected")
            return {'CANCELLED'}

        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        original_selection = context.selected_objects
        active_obj = context.view_layer.objects.active

        for obj in selected_objects:
            # Create folder: Export\ObjectName\
            obj_folder = os.path.join(export_path, obj.name)
            os.makedirs(obj_folder, exist_ok=True)

            # File path: ObjectName.fbx
            export_file = os.path.join(obj_folder, f"{obj.name}.fbx")

            # Select only this object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Export FBX
            bpy.ops.export_scene.fbx(
                filepath=export_file,
                use_selection=True,
                apply_scale_options='FBX_SCALE_ALL',
                bake_space_transform=True
            )

        # Restore selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selection:
            obj.select_set(True)
        context.view_layer.objects.active = active_obj

        self.report({'INFO'}, "Export complete!")
        return {'FINISHED'}


class BatchExportPanel(bpy.types.Panel):
    bl_label = "Batch Export FBX"
    bl_idname = "VIEW3D_PT_batch_export_fbx"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Export'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "batch_export_path")
        layout.operator("export.batch_individual_fbx")


def register():
    bpy.types.Scene.batch_export_path = bpy.props.StringProperty(
        name="Export Folder",
        description="Base folder for exports",
        subtype='DIR_PATH'
    )

    bpy.utils.register_class(BatchExportFBXOperator)
    bpy.utils.register_class(BatchExportPanel)


def unregister():
    del bpy.types.Scene.batch_export_path
    bpy.utils.unregister_class(BatchExportFBXOperator)
    bpy.utils.unregister_class(BatchExportPanel)


if __name__ == "__main__":
    register()