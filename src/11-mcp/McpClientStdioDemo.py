"""
【案例】使用官方 mcp SDK 以 stdio 方式连接 MCP 服务端（客户端侧）

对应教程章节：第 20 章 - MCP 模型上下文协议

知识点速览：
- 客户端“接管服务端 stdin/stdout”的本质：用 asyncio 把服务端脚本拉成子进程，
  拿到它的 stdin/stdout 管道，再用两个协程在管道上收发音 JSON（JSON-RPC）。
- mcp SDK 的 `stdio_client` 已经把“拉子进程 + 接管管道”封装好了，我们只管拿到
  (read, write) 两条流，交给 `ClientSession` 跑协议即可。
- 注意：服务端必须由客户端拉起，绝不能自己在终端单独运行（否则 stdin 是键盘，
  会触发 Invalid JSON，参见 McpServerByFastMCP.py 的注释）。
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    # 1) 描述“怎么启动服务端”——客户端会据此 fork 出子进程并接管它的 stdin/stdout
    server_params = StdioServerParameters(
        command=sys.executable,  # 用当前解释器，确保和服务端用同一个 venv
        args=["src/11-mcp/McpServerByFastMCP.py"],  # 服务端脚本路径（相对项目根目录）
    )

    # 2) stdio_client 拉起子进程，yield 出 (read_stream, write_stream)
    #    read = 从服务端 stdout 读到的消息；write = 要写给服务端 stdin 的消息
    async with stdio_client(server_params) as (read, write):
        # 3) ClientSession 在两条流之上实现 JSON-RPC（initialize / list_tools / call_tool ...）
        async with ClientSession(read, write) as session:
            await session.initialize()  # 建立会话（MCP 握手）

            tools = await session.list_tools()
            print("服务端暴露的工具:", [t.name for t in tools.tools])

            # 4) 调用服务端的 add 工具
            result = await session.call_tool("add", {"a": 2, "b": 3})
            print("call_tool('add', {a:2, b:3}) =>", result)


if __name__ == "__main__":
    asyncio.run(main())
