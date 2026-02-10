import bpy

class RTC_PT_MainPanel(bpy.types.Panel):
    bl_label = "Real-Time Collaboration"
    bl_idname = "RTC_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Collaboration'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Status Indicator (Simplified)
        # In a real addon, we'd access the client.connection_status variable directly
        # For now, we rely on the console or simple props if we added them to scene
        
        layout.label(text="Session Control")
        
        row = layout.row()
        row.prop(scene, "rtc_server_url", text="Server")

        row = layout.row()
        op = row.operator("rtc.connect", text="Host Session")
        op.action = "host"
        
        layout.separator()
        
        row = layout.row()
        row.prop(scene, "rtc_room_code", text="Code")
        
        row = layout.row()
        op = row.operator("rtc.connect", text="Join Session")
        op.action = "join"
        
        layout.separator()
        layout.operator("rtc.disconnect", text="Disconnect")

classes = (
    RTC_PT_MainPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.rtc_server_url = bpy.props.StringProperty(
        name="Server URL",
        description="WebSocket URL of the Relay Server (e.g., ws://192.168.1.5:8765)",
        default="ws://localhost:8765"
    )

    bpy.types.Scene.rtc_room_code = bpy.props.StringProperty(
        name="Room Code",
        description="Enter the room code to join",
        default=""
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.rtc_server_url
    del bpy.types.Scene.rtc_room_code
