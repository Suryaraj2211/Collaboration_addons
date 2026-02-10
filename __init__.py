bl_info = {
    "name": "Real-Time Collaboration",
    "author": "Antigravity",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > N-Panel > Collaboration",
    "description": "Real-time collaboration add-on for Blender",
    "warning": "",
    "wiki_url": "",
    "category": "Development",
}

import bpy
from . import ui
from . import client

def register():
    ui.register()
    client.register()

def unregister():
    ui.unregister()
    client.unregister()

if __name__ == "__main__":
    register()
