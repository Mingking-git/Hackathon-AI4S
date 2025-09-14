# To install this addon:
# 1. Open Blender
# 2. Go to Edit > Preferences > Add-ons
# 3. Click "Install..." and select this file.
# 4. Enable the addon by checking the box.
# You will find the server controls in the 3D View sidebar (N key) > "AI MCP" tab.

bl_info = {
    "name": "AI4S Hackathon",
    "author": "AI4S Hackathon",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > AI MCP Tab",
    "description": "Runs a server to receive JSON commands for object creation and importing.",
    "category": "Development",
}

import bpy
import socket
import threading
import queue
import json
import os  # Import the os module for file path operations

# --- Globals for Server Management ---
server_thread = None
server_socket = None
stop_thread = threading.Event()
command_queue = queue.Queue()


# --- Command Execution ---

def execute_create_cube(params):
    size = params.get("size", 2)
    location = params.get("location", (0, 0, 0))
    bpy.ops.mesh.primitive_cube_add(size=size, enter_editmode=False, align='WORLD', location=location)
    return f"Created a cube with size {size} at {location}."


def execute_create_sphere(params):
    radius = params.get("radius", 1)
    location = params.get("location", (0, 0, 0))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
    return f"Created a sphere with radius {radius} at {location}."


def execute_create_snowman():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 1.5))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 3.5))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(0, 0, 5.2))
    return "Created a snowman."

# --- NEW: Physics Simulation Execution ---
def execute_physics_simulation(params):
    """
    Executes a physics simulation script, then bakes, plays, and optionally renders.
    """
    python_script = params.get("script", "").strip()
    if not python_script:
        return "Error: No script provided for physics simulation."

    # Step 1: Execute the user's script to set up the scene
    try:
        print("Executing physics setup script...")
        exec(python_script)
        print("Script execution finished.")
    except Exception as e:
        error_message = f"Error during physics script execution: {e}"
        print(error_message)
        return error_message

    # Step 2: Bake all physics simulations in the scene
    try:
        print("Baking all physics simulations...")
        # Deselect all objects first to ensure the context is correct
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.ptcache.bake_all(bake=True)
        print("Baking complete.")
    except Exception as e:
        # This might fail if there's nothing to bake, which is not a critical error.
        print(f"Info: Could not bake physics simulations (maybe none require baking). Details: {e}")

    # Step 3: Handle Playback or Rendering
    if params.get("render_animation", False):
        print("Starting animation render...")
        try:
            # Configure render output settings
            output_dir = os.path.join(os.path.expanduser("~"), "blender_renders")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Use a timestamp to avoid overwriting files
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bpy.context.scene.render.filepath = os.path.join(output_dir, f"phys_sim_{timestamp}.mp4")

            bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
            bpy.context.scene.render.ffmpeg.format = 'MPEG4'
            bpy.context.scene.render.ffmpeg.codec = 'H264'
            bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'

            # Trigger the render
            bpy.ops.render.render(animation=True)
            print(f"Rendering complete. Output saved to: {bpy.context.scene.render.filepath}")
            return "Physics simulation setup, baked, and rendered."
        except Exception as e:
            error_message = f"Error during rendering: {e}"
            print(error_message)
            return error_message
    else:
        # If not rendering, just play the animation in the viewport
        print("Starting animation playback in viewport...")
        bpy.context.scene.frame_set(bpy.context.scene.frame_start)
        bpy.ops.screen.animation_play()
        return "Physics simulation setup, baked, and now playing."


def execute_python(params):
    python_script = params.get("script")
    python_script = python_script.strip()
    # execute python script
    if os.path.exists('/Users/kaneg/Work/jt-hackathon/error.log'):
        with open('/Users/kaneg/Work/jt-hackathon/error.log', 'w') as f:
            try:
                exec(python_script)
            except Exception as e:
                f.write(str(e))
    else:
        exec(python_script)
    return "Created by script."


def execute_import_model(params):
    """Imports a 3D model file into the scene."""
    extension = params.get("type")
    model_content = params.get("content")
    if not model_content:
        print("Error: No model_content provided for import_model command.")
        return "Error: model_content missing."
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=True) as tmp:
        tmp.write(model_content)
        tmp.flush()  # Ensure data is written
        print(f"Temporary file created at: {tmp.name}")
        filepath = tmp.name
        try:
            # create temp file from model_content
            # filepath = os.mkstemp(suffix=f".{extension}")[1]
            # with open(filepath, "w") as f:
            #     f.write(model_content)
            print(f"Importing model from: {filepath}")
            if extension == 'obj':
                bpy.ops.import_scene.obj(filepath=filepath)
            elif extension == 'glb' or extension == 'gltf':
                bpy.ops.import_scene.gltf(filepath=filepath)
            elif extension == 'fbx':
                bpy.ops.import_scene.fbx(filepath=filepath)
            else:
                print(f"Error: Unsupported file extension '{extension}'")
                return f"Error: Unsupported file type."

            return f"Successfully imported {os.path.basename(filepath)}."
        except Exception as e:
            print(f"Blender import failed: {e}")
            return "Error: Blender import failed."


def server_logic(host, port):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        server_socket.settimeout(1.0)
        print(f"[Blender Server] Listening for JSON commands on {host}:{port}")
        while not stop_thread.is_set():
            try:
                conn, addr = server_socket.accept()
                with conn:
                    data = conn.recv(40960)
                    if not data: break
                    try:
                        command_payload = json.loads(data.decode('utf-8'))
                        print(f"[Blender Server] Received JSON: {command_payload}")
                        command_queue.put(command_payload)
                        conn.sendall(b"JSON command received.")
                    except json.JSONDecodeError:
                        conn.sendall(b"Error: Invalid JSON.")
            except socket.timeout:
                continue
    except Exception as e:
        print(f"[Blender Server] Server error: {e}")
    finally:
        print("[Blender Server] Shutting down.")
        if server_socket:
            server_socket.close()
            server_socket = None


def process_command_queue():
    try:
        task = command_queue.get_nowait()
        command = task.get("command")
        params = task.get("params", {})

        print(f"Processing command: {command}")

        if command == "create_cube":
            execute_create_cube(params)
        elif command == "create_sphere":
            execute_create_sphere(params)
        elif command == "create_snowman":
            execute_create_snowman()
        elif command == "import_model":
            execute_import_model(params)
        elif command == "python":
            execute_python(params)
        elif command == "run_physics_simulation":
            execute_physics_simulation(params)
        else:
            print(f"Unknown command: {command}")
    except queue.Empty:
        pass
    return 0.1


# --- Blender UI and Registration (No changes from previous version) ---
class MCP_OT_StartServer(bpy.types.Operator):
    bl_idname = "mcp.start_server"
    bl_label = "Start Server"

    def execute(self, context):
        global server_thread, stop_thread
        if server_thread and server_thread.is_alive():
            self.report({'WARNING'}, "Server is already running.")
            return {'CANCELLED'}
        bpy.app.timers.register(process_command_queue, first_interval=0.1)
        stop_thread.clear()
        server_thread = threading.Thread(target=server_logic, args=('localhost', 9876))
        server_thread.start()
        context.scene.mcp_server_status = "Running"
        self.report({'INFO'}, "MCP Server Started.")
        return {'FINISHED'}


class MCP_OT_StopServer(bpy.types.Operator):
    bl_idname = "mcp.stop_server"
    bl_label = "Stop Server"

    def execute(self, context):
        global server_thread, stop_thread
        if not server_thread or not server_thread.is_alive():
            self.report({'WARNING'}, "Server is not running.")
            context.scene.mcp_server_status = "Stopped"
            return {'CANCELLED'}
        stop_thread.set()
        if bpy.app.timers.is_registered(process_command_queue):
            bpy.app.timers.unregister(process_command_queue)
        server_thread.join(timeout=2.0)
        context.scene.mcp_server_status = "Stopped"
        self.report({'INFO'}, "MCP Server Stopped.")
        return {'FINISHED'}


class MCP_PT_Panel(bpy.types.Panel):
    bl_label = "AI MCP Server"
    bl_idname = "MCP_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI MCP'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text=f"Status: {context.scene.mcp_server_status}")
        layout.row().operator(MCP_OT_StartServer.bl_idname)
        layout.row().operator(MCP_OT_StopServer.bl_idname)


classes = (MCP_OT_StartServer, MCP_OT_StopServer, MCP_PT_Panel)


def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.mcp_server_status = bpy.props.StringProperty(name="Server Status", default="Stopped")


def unregister():
    if bpy.context.scene.mcp_server_status == "Running":
        class DummyContext: scene = bpy.context.scene

        MCP_OT_StopServer().execute(DummyContext())
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mcp_server_status


if __name__ == "__main__":
    register()

