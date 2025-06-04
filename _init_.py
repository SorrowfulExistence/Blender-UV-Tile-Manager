bl_info = {
    "name": "UV Tile Manager",
    "author": "SorrowfulExistence",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "UV Editor > Sidebar > UV Tile Manager",
    "description": "manage UV tiles - select and move UV islands between tiles",
    "category": "UV",
}

import bpy
import bmesh
from mathutils import Vector

class UV_TILE_MANAGER_Props(bpy.types.PropertyGroup):
    source_tile_x: bpy.props.IntProperty(
        name="Source Tile X",
        description="X coordinate of source tile",
        default=0,
        min=0,
        max=3
    ) # type: ignore
    source_tile_y: bpy.props.IntProperty(
        name="Source Tile Y", 
        description="Y coordinate of source tile",
        default=0,
        min=0,
        max=3
    ) # type: ignore
    target_tile_x: bpy.props.IntProperty(
        name="Target Tile X",
        description="X coordinate of target tile",
        default=0,
        min=0,
        max=3
    ) # type: ignore
    target_tile_y: bpy.props.IntProperty(
        name="Target Tile Y",
        description="Y coordinate of target tile",
        default=0,
        min=0,
        max=3
    ) # type: ignore
    off_grid_x: bpy.props.FloatProperty(
        name="Off-Grid X",
        description="X offset for moving UVs off the grid",
        default=4.0,
        min=-10.0,
        max=10.0
    ) # type: ignore
    off_grid_y: bpy.props.FloatProperty(
        name="Off-Grid Y",
        description="Y offset for moving UVs off the grid",
        default=0.0,
        min=-10.0,
        max=10.0
    ) # type: ignore

class UV_OT_select_tile(bpy.types.Operator):
    """Select all UV faces within specified tile"""
    bl_idname = "uv.select_tile"
    bl_label = "Select UV Tile"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh")
            return {'CANCELLED'}
        
        props = context.scene.uv_tile_manager
        tile_x = props.source_tile_x
        tile_y = props.source_tile_y
        
        #make sure we're in edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV layer")
            return {'CANCELLED'}
        
        #tile boundaries
        min_u = tile_x
        max_u = tile_x + 1
        min_v = tile_y
        max_v = tile_y + 1
        
        #check each face to see if it's in our tile
        for face in bm.faces:
            face_in_tile = False
            for loop in face.loops:
                uv = loop[uv_layer].uv
                if min_u <= uv.x < max_u and min_v <= uv.y < max_v:
                    face_in_tile = True
                    break
            
            if face_in_tile:
                face.select = True
                #also select the uvs
                for loop in face.loops:
                    loop[uv_layer].select = True
        
        bmesh.update_edit_mesh(me)
        
        #turn on sync selection if it's off
        if not context.tool_settings.use_uv_select_sync:
            context.tool_settings.use_uv_select_sync = True
        
        self.report({'INFO'}, f"Selected UVs in tile ({tile_x}, {tile_y})")
        return {'FINISHED'}

class UV_OT_move_to_tile(bpy.types.Operator):
    """Move selected UV islands to target tile"""
    bl_idname = "uv.move_to_tile"
    bl_label = "Move to Target Tile"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh")
            return {'CANCELLED'}
        
        props = context.scene.uv_tile_manager
        target_x = props.target_tile_x
        target_y = props.target_tile_y
        
        bpy.ops.object.mode_set(mode='EDIT')
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV layer")
            return {'CANCELLED'}
        
        #grab selected faces
        selected_faces = [f for f in bm.faces if f.select]
        if not selected_faces:
            self.report({'WARNING'}, "No faces selected")
            return {'CANCELLED'}
        
        #find the bounds of our selection
        min_uv = Vector((float('inf'), float('inf')))
        max_uv = Vector((float('-inf'), float('-inf')))
        
        for face in selected_faces:
            for loop in face.loops:
                uv = loop[uv_layer].uv
                min_uv.x = min(min_uv.x, uv.x)
                min_uv.y = min(min_uv.y, uv.y)
                max_uv.x = max(max_uv.x, uv.x)
                max_uv.y = max(max_uv.y, uv.y)
        
        #figure out how far to move
        current_tile_x = int(min_uv.x)
        current_tile_y = int(min_uv.y)
        offset_x = target_x - current_tile_x
        offset_y = target_y - current_tile_y
        
        #actually move the uvs
        for face in selected_faces:
            for loop in face.loops:
                loop[uv_layer].uv.x += offset_x
                loop[uv_layer].uv.y += offset_y
        
        bmesh.update_edit_mesh(me)
        
        self.report({'INFO'}, f"Moved selected UVs to tile ({target_x}, {target_y})")
        return {'FINISHED'}

class UV_OT_move_off_grid(bpy.types.Operator):
    """Move selected UV islands off the 0-3 grid"""
    bl_idname = "uv.move_off_grid"
    bl_label = "Move Off Grid"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh")
            return {'CANCELLED'}
        
        props = context.scene.uv_tile_manager
        
        bpy.ops.object.mode_set(mode='EDIT')
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV layer")
            return {'CANCELLED'}
        
        #get what's selected
        selected_faces = [f for f in bm.faces if f.select]
        if not selected_faces:
            self.report({'WARNING'}, "No faces selected")
            return {'CANCELLED'}
        
        #move everything by the offset amount
        for face in selected_faces:
            for loop in face.loops:
                loop[uv_layer].uv.x += props.off_grid_x
                loop[uv_layer].uv.y += props.off_grid_y
        
        bmesh.update_edit_mesh(me)
        
        self.report({'INFO'}, f"Moved selected UVs off grid by ({props.off_grid_x}, {props.off_grid_y})")
        return {'FINISHED'}

class UV_PT_tile_manager(bpy.types.Panel):
    """UV Tile Manager Panel"""
    bl_label = "UV Tile Manager"
    bl_idname = "UV_PT_tile_manager"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "UV Tile Manager"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.uv_tile_manager
        
        #source tile stuff
        box = layout.box()
        box.label(text="Source Tile Selection", icon='SELECT_SET')
        row = box.row()
        row.prop(props, "source_tile_x")
        row.prop(props, "source_tile_y")
        box.operator("uv.select_tile", text="Select Tile", icon='RESTRICT_SELECT_OFF')
        
        #target tile stuff
        box = layout.box()
        box.label(text="Target Tile", icon='FORWARD')
        row = box.row()
        row.prop(props, "target_tile_x")
        row.prop(props, "target_tile_y")
        box.operator("uv.move_to_tile", text="Move to Target Tile", icon='TRANSFORM_MOVE')
        
        #off grid movement
        box = layout.box()
        box.label(text="Move Off Grid", icon='FULLSCREEN_EXIT')
        row = box.row()
        row.prop(props, "off_grid_x")
        row.prop(props, "off_grid_y")
        box.operator("uv.move_off_grid", text="Move Off Grid", icon='EXPORT')
        
        #little visual grid guide
        box = layout.box()
        box.label(text="Grid Reference (0-3):", icon='GRID')
        col = box.column(align=True)
        col.scale_y = 0.5
        for y in range(3, -1, -1):
            row = col.row(align=True)
            for x in range(4):
                if x == props.source_tile_x and y == props.source_tile_y:
                    row.label(text=f"[{x},{y}]")
                else:
                    row.label(text=f"{x},{y}")

def register():
    bpy.utils.register_class(UV_TILE_MANAGER_Props)
    bpy.utils.register_class(UV_OT_select_tile)
    bpy.utils.register_class(UV_OT_move_to_tile)
    bpy.utils.register_class(UV_OT_move_off_grid)
    bpy.utils.register_class(UV_PT_tile_manager)
    
    bpy.types.Scene.uv_tile_manager = bpy.props.PointerProperty(type=UV_TILE_MANAGER_Props)

def unregister():
    del bpy.types.Scene.uv_tile_manager
    
    bpy.utils.unregister_class(UV_PT_tile_manager)
    bpy.utils.unregister_class(UV_OT_move_off_grid)
    bpy.utils.unregister_class(UV_OT_move_to_tile)
    bpy.utils.unregister_class(UV_OT_select_tile)
    bpy.utils.unregister_class(UV_TILE_MANAGER_Props)

if __name__ == "__main__":
    register()