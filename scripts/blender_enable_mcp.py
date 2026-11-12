# Blender起動時に MCP for Blender アドオンを有効化してソケットサーバー(9876)を立てる
import bpy, addon_utils, os, shutil
src = os.path.join(os.path.dirname(__file__), "..", "tools", "blender-mcp", "addon.py")
dst_dir = bpy.utils.user_resource("SCRIPTS", path="addons", create=True)
shutil.copy(os.path.abspath(src), os.path.join(dst_dir, "blender_mcp_addon.py"))
addon_utils.modules_refresh()
addon_utils.enable("blender_mcp_addon", default_set=True, persistent=True)
print("BlenderMCP addon enabled")
