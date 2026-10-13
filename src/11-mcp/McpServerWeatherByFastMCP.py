"""
【案例】用 FastMCP 实现天气查询 MCP 服务（SSE + 指定 host/port）

对应教程章节：第 20 章 - MCP 模型上下文协议 → 6、案例实战：本地 MCP 天气服务与客户端

知识点速览：
- 这是一个“网络化 MCP Tool 服务”案例：它只暴露一个天气查询工具，用来配合同目录的 mcp.json
  和 McpClientAgent.py 演示“服务端独立启动 → 客户端连接 → Agent 调工具”这条完整链路。
- 与 McpServer.py 的关系：McpServer.py 是教学版极简服务端，这个文件才是更贴近真实 SDK 用法的
  FastMCP 写法；两者都在讲“服务端暴露工具”，只是抽象层级不同。
- 与 McpServerByFastMCP.py 的关系：后者重点在 Tools / Resources / Prompts 三类能力，这个文件则聚焦
  “一个真实工具如何通过网络方式暴露出去”。
- 本仓库保留 transport="sse" 的写法，是为了和 mcp.json、课程截图、网络化示例保持一致；如果从
  当前官方主线理解，初学者还要知道 stdio 和 HTTP/Streamable HTTP 才是更需要重点理解的传输方式。
- 正确写法：mcp = FastMCP("服务名")  →  mcp.run(transport="sse", host="127.0.0.1", port=8000)
- 错误写法：mcp = FastMCP("服务名", host="127.0.0.1", port=8000)  # FastMCP 构造函数不支持 host/port
"""
