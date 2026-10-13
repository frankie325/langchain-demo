"""
【案例】基于 mcp.json + LangChain Agent 的 MCP 客户端（LLM + MCP 工具）

对应教程章节：
- 第 20 章 - MCP 模型上下文协议 → 6、案例实战：本地 MCP 天气服务与客户端
- 第 21 章 - Agent 智能体 → 5、实操与案例（5.4 Agent + MCP）

知识点速览（2026 更新）：
- ⚠️ 官方迁移：原来的 `langchain-mcp-adapters`（MultiServerMCPClient）已**废弃**。
  LangChain 官方已将 MCP 支持并回主库 `langchain.mcp` 命名空间（基于 FastMCP 4），
  推荐安装 `langchain[mcp]` 并使用 `MCPAdapter`。详见：
  https://docs.langchain.com/oss/python/migrate/langchain-mcp-adapters
- 本案例改用 `from langchain.mcp import MCPAdapter` 加载 mcp.json 中的多台 MCP
  服务并获取工具列表，再交给 LangChain 的 create_tool_calling_agent + AgentExecutor，
  形成「LLM + MCP 工具」的对话 Agent。
- MCPAdapter 是异步上下文管理器：进入时建立所有连接、退出时统一关闭；
  传输方式（stdio / streamable-http）由配置里的 command/args 或 url **自动推断**，
  不再需要（且已不支持）旧式的 `transport` 字段，SSE 传输也不再被支持。
- mcp.json 是“客户端侧的连接配置约定”，不是 MCP 协议本身。
- 流程：加载 mcp.json → MCPAdapter 上下文内获取工具 → 创建模型与提示 → 组装 Agent → 聊天循环。
- 注意：`langchain[mcp]` 当前为 beta，导入会触发 LangChainBetaWarning，API 可能变动。
- 依赖：pip install "langchain[mcp]" langchain-openai langchain-classic loguru；
  需配置环境变量 aliQwen-api（或改用其他兼容 OpenAI 的 api_key/base_url）。
"""

import asyncio
import json
import os
import warnings
from pathlib import Path

# langchain[mcp] 当前为 beta，导入时会打印 LangChainBetaWarning；如想看到提示可删除下面这行
warnings.filterwarnings("ignore", message=r".*\bbeta\b.*")

from loguru import logger
from dotenv import load_dotenv

load_dotenv()


# 默认 mcp.json 路径（与本文件同目录）
_MCP_JSON_PATH = Path(__file__).resolve().parent / "mcp.json"


def load_servers(file_path: str | Path | None = None) -> dict:
    """
    加载 MCP 服务器配置。
    :param file_path: 配置文件路径，默认使用同目录下的 mcp.json
    :return: 完整配置字典，如 {"mcpServers": {"weather": {...}, "fetch": {...}}}

    这里读取的是“客户端如何连接服务”的约定配置，而不是协议本体。
    """
    path = Path(file_path) if file_path else _MCP_JSON_PATH
    if not path.exists():
        logger.warning(f"未找到 mcp 配置文件: {path}")
        return {"mcpServers": {}}
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    logger.info(
        f"已加载 mcp 配置: {path}，共 {len(config.get('mcpServers', {}))} 个服务"
    )
    return config


def _to_adapter_config(config: dict) -> dict:
    """
    把 mcp.json 转换为 langchain.mcp 的 MCPAdapter 配置形态。

    - 新 API 的传输类型由 command/args（stdio）或 url（streamable-http）自动推断，
      不再需要（且不再支持）旧式的 `transport` 字段，这里统一剥离它。
    - 旧 mcp.json 里 weather 用的 `sse` 端点已不被支持，需改成 streamable-http
      的默认端点 /mcp（详见 mcp.json 与 McpServerWeatherByFastMCP.py）。
    """
    servers = config.get("mcpServers", {})
    cleaned = {
        name: {k: v for k, v in srv.items() if k != "transport"}
        for name, srv in servers.items()
    }
    return {"mcpServers": cleaned}


async def run_chat_loop(config_path: str | Path | None = None) -> None:
    """
    启动并运行一个基于 MCP 工具的聊天 Agent 循环。
    该函数会：1）加载 MCP 服务器配置；2）用 MCPAdapter 建立连接并获取工具；
    3）创建基于 DeepSeek 的语言模型和 Agent；4）启动命令行聊天循环；5）退出时清理资源。
    """
    from langchain.mcp import MCPAdapter
    from langchain_openai import ChatOpenAI
    from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    config = load_servers(config_path)
    servers = config.get("mcpServers", {})
    if not servers:
        logger.warning("mcp.json 中未配置任何服务，无法获取 MCP 工具")
        return

    adapter_config = _to_adapter_config(config)

    # MCPAdapter 是异步上下文管理器：进入时连接所有服务并准备会话，退出时统一关闭。
    # 整个 Agent 运行期都必须保持在上下文内，因为工具调用依赖底层连接。
    async with MCPAdapter(adapter_config) as adapter:
        tools = await adapter.list_tools()
        if not tools:
            logger.warning(
                "未从 MCP 服务获取到任何工具，请确认服务已启动且 mcp.json 配置正确"
            )
            return

        logger.info(f"已获取 {len(tools)} 个 MCP 工具: {[t.name for t in tools]}")

        # 大模型：用于根据「工具返回 + 用户问题」生成回答
        llm = ChatOpenAI(
            model="qwen-plus",
            api_key=os.getenv("aliQwen-api"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        # 对话提示：系统提示要求使用工具完成用户请求，agent_scratchpad 供 Executor 填入中间步骤
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个有用的助手，需要使用提供的工具来完成用户请求。"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors="解析用户请求失败，请重新输入清晰的指令",
        )
        logger.info(
            "\n MCP Agent 已启动，请先输入一个提问给(LLM+MCP)，输入 'quit' 退出"
        )

        while True:
            try:
                user_input = input("\n您: ").strip()
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    logger.info("已退出")
                    break
                # 在 async 上下文内使用异步 ainvoke，避免嵌套事件循环冲突
                result = await agent_executor.ainvoke({"input": user_input})
                output = result.get("output", result)
                print(f"\nAgent: {output}")
            except KeyboardInterrupt:
                logger.info("已退出")
                break


def main() -> None:
    asyncio.run(run_chat_loop())


if __name__ == "__main__":
    main()
