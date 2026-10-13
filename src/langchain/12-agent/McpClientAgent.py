"""
【案例】基于 mcp.json + LangChain Agent 的 MCP 客户端（LLM + MCP 工具）

对应教程章节：
- 第 20 章 - MCP 模型上下文协议 → 6、案例实战：本地 MCP 天气服务与客户端
- 第 21 章 - Agent 智能体 → 5、实操与案例（5.4 Agent + MCP）

知识点速览：
- 从同目录的 mcp.json 加载 MCP 服务配置，使用 langchain_mcp_adapters 的 MultiServerMCPClient 连接多台
  MCP 服务器并获取工具列表，再交给 LangChain 的 create_tool_calling_agent + AgentExecutor，形成
  「LLM + MCP 工具」的对话 Agent。这也是第 21 章里“外部工具接入 Agent”的代表案例。
- mcp.json 是“客户端侧的连接配置约定”，不是 MCP 协议本身。它描述的是“有哪些服务、分别怎么连”，
  例如本仓库里既有网络方式的 weather 服务，也有 stdio 方式的 fetch 服务。
- 流程：加载 mcp.json → 初始化 MultiServerMCPClient → 异步获取 MCP Tools → 创建 DeepSeek 模型与
  提示模板 → 组装 Agent 与 AgentExecutor → 启动命令行聊天循环（输入 quit 退出）。
- 本案例重点展示“把 MCP Tools 交给 LangChain Agent”；Resources 和 Prompts 虽然也是 MCP 能力，
  但这里没有作为主线展开。
- 这个文件延续了仓库里更容易教学的 classic Agent 路线；如果改走更偏 1.x 的直接路线，也常见
  `await client.get_tools()` 之后把工具交给 `create_agent`，再配合 `ainvoke()` / `astream()` 使用。
- 依赖：pip install langchain-mcp-adapters langchain-openai langchain-classic loguru；部分适配器要求 Python 3.12 及以下。需配置环境变量 deepseek-api（或改用其他兼容 OpenAI 的 api_key/base_url）。
"""

import asyncio
import json
import os
from pathlib import Path

from loguru import logger

# 默认 mcp.json 路径（与本文件同目录）
_MCP_JSON_PATH = Path(__file__).resolve().parent / "mcp.json"
