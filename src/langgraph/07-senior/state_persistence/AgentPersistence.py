"""
【案例】高阶 Agent + 短期记忆：create_agent 搭配 InMemorySaver，实现同一 thread_id 下的多轮对话与上下文延续。

对应教程章节：第 25 章 - LangGraph 高级特性 → 2、状态持久化（Persistence）

知识点速览：
- `create_agent(..., checkpointer=...)` 说明高层 Agent 接口底层仍然可以吃到 LangGraph 的持久化能力。
- 同一 `thread_id` 下的多次 invoke 会连续使用同一条线程状态，这也是“多轮对话为什么能续上”的关键。
- 这个案例最值得帮助读者建立的认知是：Persistence 不只服务于手写图，也服务于更高层的 Agent 体系。
"""

import os

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import load_dotenv

load_dotenv(encoding="utf-8")


def main():
    llm = init_chat_model(
        model="gpt-6-luna",  # 模型 ID，与平台模型广场一致
        model_provider="openai",  # 表示使用「OpenAI 兼容」的 API（阿里百炼、通义等均兼容，阿里百炼不支持直接调用，需要通过OpenAI 兼容的 API 调用）
        api_key=os.getenv(
            "OPENAI_API_KEY"
        ),  # 需事先 export 或在下面 load_dotenv 之后再用
        base_url=os.getenv("BASE_URL"),
        temperature=0.0,
    )
    checkpointer = InMemorySaver()
    agent = create_agent(model=llm, checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "user-001"}}

    msg1 = agent.invoke(
        {"messages": [("user", "你好，我叫张三，喜欢足球，60字内简洁回复")]},
        config,
    )
    msg1["messages"][-1].pretty_print()

    msg2 = agent.invoke(
        {"messages": [("user", "我叫什么？我喜欢做什么？")]},
        config,
    )
    msg2["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
