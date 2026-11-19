# %% [markdown]
# # Lab 5.3 — MCP: list the server's tools and resources, call a tool, test the access token
# Explore it visually too:  npx @modelcontextprotocol/inspector .venv/bin/python mcp_server/server.py

# %%
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard.agent.mcp_client import _client, call_tool, list_tools  # noqa: E402


async def show_resources() -> None:
    blobs = await _client().get_resources("records")
    for blob in blobs:
        print(blob.metadata.get("uri"), "->", blob.as_string()[:150], "...")


async def show_prompt() -> None:
    messages = await _client().get_prompt("records", "troubleshoot_aircraft",
                                          arguments={"tail_number": "N123AB", "symptom": "engine 2 vibration"})
    print("Prompt 'troubleshoot_aircraft' ->", messages[0].content[:150], "...")


# MCP servers offer three things: tools (actions), resources (data to read) and prompts (reusable templates)
print("Tools:", asyncio.run(list_tools()))
asyncio.run(show_resources())
asyncio.run(show_prompt())

# %%
print(call_tool("get_aircraft", {"tail_number": "N123AB"}))
for row in call_tool("get_maintenance_history", {"tail_number": "N123AB", "ata_chapter": 72, "limit": 3}):
    print(row)


# %% A wrong token is refused by the server
async def wrong_token() -> str:
    tools = {t.name: t for t in await _client().get_tools()}
    return await tools["get_aircraft"].ainvoke({"tail_number": "N123AB", "access_token": "wrong"})

print(asyncio.run(wrong_token()))
