# MCPクライアントとして mcp-for-blender を起動し、ツール一覧取得→シーン操作→レンダリング
import asyncio, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
OUT = os.path.abspath("out/blender_mcp_test.png")
CODE = f'''
import bpy
bpy.ops.mesh.primitive_torus_add(location=(0,0,1.2))
bpy.context.active_object.name = "MCP_Torus"
s = bpy.context.scene
s.render.engine = "BLENDER_EEVEE" if False else "CYCLES"; s.cycles.samples = 8; s.cycles.device = "CPU"
s.render.resolution_x, s.render.resolution_y = 480, 270
s.render.filepath = r"{OUT}"
bpy.ops.render.render(write_still=True)
print("objects:", [o.name for o in bpy.data.objects])
'''
async def main():
    p = StdioServerParameters(command=".venv/bin/mcp-for-blender", env={**os.environ, "DISABLE_TELEMETRY": "true"})
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = [t.name for t in (await s.list_tools()).tools]
            print("tools:", len(tools), tools[:8])
            res = await s.call_tool("get_scene_info", {})
            print("scene:", res.content[0].text[:200])
            res = await s.call_tool("execute_blender_code", {"code": CODE})
            print("exec:", res.content[0].text[:300])
asyncio.run(main())
