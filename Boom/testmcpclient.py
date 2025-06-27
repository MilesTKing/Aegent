import asyncio
from fastmcp import Client

client = Client("http://0.0.0.0:8090/mcp")  # or your server address

async def call_tool():
    async with client:
        result = await client.call_tool(
            name="greet",
            arguments={"name": "Miles"}
        )
        print(result)

asyncio.run(call_tool())