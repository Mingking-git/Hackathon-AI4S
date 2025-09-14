from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP("Blender 🚀")

import logging

# Set up logging (this just prints messages to your terminal for debugging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the MCP server object
import blender_client


# Here’s where you define your tools (functions the AI can use)
# @mcp.tool()
def draw_cube_in_blender(size: int = 2, location: Optional[list[int]] = None):
    """
    This function creates a cube in Blender using the input size and location.
    """
    if location is None:
        location = [0, 0, 1]
    cmd = {"command": "create_cube", "params": {"size": size, "location": location}}
    blender_client.send_command_to_blender(cmd)
    return f"Created a cube with size {size} at {location}."


# @mcp.tool()
def draw_sphere_in_blender(radius: int = 1, location: Optional[list[int]] = None):
    """Draw a sphere in Blender."""
    if location is None:
        location = [0, 0, 1]
    cmd = {"command": "create_sphere", "params": {"radius": radius, "location": location}}

    blender_client.send_command_to_blender(cmd)
    return f"Created a sphere with radius {radius} at {location}."


@mcp.tool()
def draw_shapes_in_blender(cmds: list[dict]):
    """Draw shapes in Blender.
    example cmd to create cube = {"command": "create_cube", "params": {"size": 2, "location": [1, 2, 3]}}
    example cmd to create sphere = {"command": "create_sphere", "params": {"radius": 3, "location": [1, 2, 3]}}
    """
    for cmd in cmds:
        blender_client.send_command_to_blender(cmd)
    return f"Shapes created in Blender."


@mcp.tool()
def draw_shapes_in_blender_by_python(python_script: str):
    """Python script to draw shapes in Blender.
    example:
    draw a cube:    bpy.ops.mesh.primitive_cube_add(size=size, enter_editmode=False, align='WORLD', location=location)
    draw a sphere:  bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
    """
    cmd = {
        "command": "python",
        "params": {
            "script": python_script,
        },
    }

    blender_client.send_command_to_blender(cmd)
    return f"Shapes created in Blender."

@mcp.tool()
def simulation_in_blender_by_python(python_script: str):
    """Python script to draw shapes in Blender. Make sure the script can be put into a JSON Argument.
    example:
    draw a cube:    bpy.ops.mesh.primitive_cube_add(size=size, enter_editmode=False, align='WORLD', location=location)
    draw a sphere:  bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
    """
    cmd = {
        "command": "run_physics_simulation",
        "params": {
            "script": python_script,
        },
    }

    blender_client.send_command_to_blender(cmd)
    return f"Shapes created in Blender."


# This is the main entry point for your server
def main():
    logger.info('Starting your-new-server')
    mcp.run('stdio')


if __name__ == "__main__":
    main()

