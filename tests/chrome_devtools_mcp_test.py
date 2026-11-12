# chrome-devtools-mcp をMCPクライアントから起動 → ページを開く → スクショ & コンソール確認
import asyncio, os, subprocess, time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
srv = subprocess.Popen(["python3", "-m", "http.server", "8765", "-d", "hyperframes/demo"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
SHOT = os.path.abspath("out/chrome_mcp_test.png")
async def main():
    p = StdioServerParameters(command="npx", args=["chrome-devtools-mcp", "--headless", "--isolated",
        "--executablePath", "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome", "--no-usage-statistics", "--viewport", "1920x1080",
        "--chromeArg=--no-sandbox"], env=dict(os.environ))
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = [t.name for t in (await s.list_tools()).tools]
            print("tools:", len(tools), tools)
            pages = (await s.call_tool("list_pages", {})).content[0].text
            print("pages:", pages[:200])
            import re; pid = int(re.search(r"(\d+):", pages).group(1))
            print("nav:", (await s.call_tool("navigate_page", {"pageId": pid, "url": "http://127.0.0.1:8765/index.html"})).content[0].text[:150])
            r1 = await s.call_tool("evaluate_script", {"pageId": pid, "function": "() => { gsap.globalTimeline.getChildren()[0].seek(2.5); return document.title + ' / ' + document.querySelector('#title').textContent }"})
            print("eval:", r1.content[0].text[:300])
            shot = await s.call_tool("take_screenshot", {"pageId": pid})
            import base64
            img = [c for c in shot.content if c.type == "image"][0]
            open(SHOT, "wb").write(base64.b64decode(img.data)); print("screenshot saved")
            r3 = await s.call_tool("list_console_messages", {"pageId": pid})
            print("console:", r3.content[0].text[:300])
try: asyncio.run(main())
finally: srv.terminate()
