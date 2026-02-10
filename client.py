import bpy
import asyncio
import websockets
import json
import threading
import queue
import time

# --- Global State ---
send_queue = queue.Queue()
receive_queue = queue.Queue()
connection_status = "Disconnected"
is_running = False

# --- Async WebSocket Client ---
async def websocket_loop(uri):
    global connection_status, is_running
    is_running = True
    connection_status = "Connecting..."
    
    try:
        async with websockets.connect(uri) as websocket:
            connection_status = "Connected"
            print("RTC: Connected to server.")

            async def sender():
                while is_running:
                    try:
                        msg = send_queue.get(block=False)
                        await websocket.send(json.dumps(msg))
                    except queue.Empty:
                        await asyncio.sleep(0.01)
                    except websockets.exceptions.ConnectionClosed:
                        break
                    except Exception as e:
                        print(f"RTC Send Error: {e}")
                        break

            async def receiver():
                try:
                    async for message in websocket:
                        if not is_running: break
                        try:
                            data = json.loads(message)
                            receive_queue.put(data)
                        except json.JSONDecodeError:
                            print("RTC: Received invalid JSON")
                except websockets.exceptions.ConnectionClosed:
                    print("RTC: Connection Closed")

            await asyncio.gather(sender(), receiver())
            
    except Exception as e:
        connection_status = "Error"
        print(f"RTC Connection Failed: {e}")
    finally:
        is_running = False
        connection_status = "Disconnected"
        print("RTC: Client stopped.")

def start_thread(uri):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_loop(uri))

# --- Blender Operators ---

class RTC_OT_Connect(bpy.types.Operator):
    bl_idname = "rtc.connect"
    bl_label = "Connect"
    bl_description = "Connect to the Relay Server"
    
    action: bpy.props.StringProperty() # 'host' or 'join'

    def execute(self, context):
        global is_running
        
        if is_running:
            self.report({'WARNING'}, "Already connected!")
            return {'CANCELLED'}

        # Start Thread
        server_url = context.scene.rtc_server_url
        t = threading.Thread(target=start_thread, args=(server_url,), daemon=True)
        t.start()
        
        # Determine initial action
        # Capture values locally to avoid ReferenceError in thread
        action_type = self.action
        code = context.scene.rtc_room_code
        

        def send_init_action():
            time.sleep(1.0) # Wait for connection (increased to 1s)
            if action_type == "host":
                send_queue.put({"action": "host"})
            elif action_type == "join":
                send_queue.put({"action": "join", "room_id": code})
        
        threading.Thread(target=send_init_action, daemon=True).start()

        # Start Modal Logic
        bpy.ops.rtc.sync_handler('INVOKE_DEFAULT')
        
        return {'FINISHED'}

class RTC_OT_Disconnect(bpy.types.Operator):
    bl_idname = "rtc.disconnect"
    bl_label = "Disconnect"
    
    def execute(self, context):
        global is_running
        is_running = False
        return {'FINISHED'}

class RTC_OT_SyncHandler(bpy.types.Operator):
    bl_idname = "rtc.sync_handler"
    bl_label = "RTC Sync Handler"
    
    _timer = None
    _last_transforms = {} # {obj_name: (loc, rot, scale)}
    _updating_remote = False # Flag to ignore updates we just applied

    def modal(self, context, event):
        global is_running, connection_status
        
        if not is_running:
            return {'FINISHED'}

        if event.type == 'TIMER':
            # 1. Process Incoming Messages
            while not receive_queue.empty():
                msg = receive_queue.get()
                self.handle_message(context, msg)

            # 2. Check for Local Changes (only if valid context)
            if context.mode == 'OBJECT':
                self.check_local_changes(context)
                
        return {'PASS_THROUGH'}

    def handle_message(self, context, msg):
        msg_type = msg.get("type")
        
        if msg_type == "hosted":
            context.scene.rtc_room_code = msg.get("room_id")
            print(f"RTC: Hosting Room {msg.get('room_id')}")
        
        elif msg_type == "update":
            data = msg.get("data")
            obj_name = data.get("name")
            print(f"RTC: Received update for '{obj_name}'")
            
            if obj_name in context.scene.objects:
                obj = context.scene.objects[obj_name]
                
                # Set flag so we don't send this back
                self._updating_remote = True
                
                obj.location = data['location']
                obj.rotation_euler = data['rotation']
                obj.scale = data['scale']
                
                # Force update
                obj.keyframe_insert(data_path="location", frame=context.scene.frame_current) if obj.animation_data else None
                context.view_layer.update()
                
                # Update our "last known" so we don't think it changed locally next tick
                self._last_transforms[obj_name] = (
                    tuple(obj.location), 
                    tuple(obj.rotation_euler), 
                    tuple(obj.scale)
                )
                
                self._updating_remote = False
            else:
                 print(f"RTC Warning: Object '{obj_name}' not found in this scene!")

    def check_local_changes(self, context):
        if self._updating_remote:
            return

        obj = context.active_object
        if not obj: return
        
        # Create a simplified signature of transform
        current_transform = (
            tuple(obj.location),
            tuple(obj.rotation_euler),
            tuple(obj.scale)
        )
        
        last = self._last_transforms.get(obj.name)
        
        # Check if transform has changed
        if last != current_transform:
            self._last_transforms[obj.name] = current_transform
            
            # Send Update
            print(f"RTC: Sending update for '{obj.name}'")
            update_data = {
                "name": obj.name,
                "location": list(obj.location),
                "rotation": list(obj.rotation_euler),
                "scale": list(obj.scale)
            }
            send_queue.put({"action": "update", "data": update_data})

    def invoke(self, context, event):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.05, window=context.window) # 20fps check
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

classes = (
    RTC_OT_Connect,
    RTC_OT_Disconnect,
    RTC_OT_SyncHandler,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
