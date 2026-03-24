from fastmcp import Client

# Connect to HTTP MCP server
client = Client("http://127.0.0.1:8000/mcp")

async def call(tool_name, args=None):
    async with client:
        return await client.call_tool(tool_name, args or {})