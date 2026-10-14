"""
【案例】messages 流模式：从图中调用 LLM 的节点逐 token（或片段）推送输出，便于打字机效果。

对应教程章节：第 25 章 - LangGraph 高级特性 → 1、流式处理（Streaming）

知识点速览：
- stream_mode="messages" 时，每次迭代一般为 (message_chunk, metadata)：chunk 为模型输出片段，metadata 标明节点等上下文。
- 这个案例最适合用来建立“LangGraph Streaming 不只流状态，也能流模型输出”这层认知。
- 流式消费侧通常关心 `chunk.content` 和 `metadata`；前者是输出片段，后者帮助你知道这些片段来自哪个节点。
- 需配置环境变量（如 aliQwen-api）与网络；模型、base_url 按你本地教程为准。
"""

import os
from typing import TypedDict

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START

from dotenv import load_dotenv

load_dotenv(encoding="utf-8")


class State(TypedDict):
    query: str
    answer: str


def node(state: State):
    print("开始调用 node 节点")

    model = init_chat_model(
        model="gpt-6-luna",  # 模型 ID，与平台模型广场一致
        model_provider="openai",  # 表示使用「OpenAI 兼容」的 API（阿里百炼、通义等均兼容，阿里百炼不支持直接调用，需要通过OpenAI 兼容的 API 调用）
        api_key=os.getenv(
            "OPENAI_API_KEY"
        ),  # 需事先 export 或在下面 load_dotenv 之后再用
        base_url=os.getenv("BASE_URL"),
    )

    llm_result = model.invoke([("user", state["query"])])
    print("llm invoke 结束", end="\n\n")

    return {"answer": llm_result}


def main():
    graph = (
        StateGraph(state_schema=State).add_node(node).add_edge(START, "node").compile()
    )

    inputs = {"query": "帮我生成一个200字的小学生作文，主题为我的一天"}

    # messages：从图内触发的大模型调用处流式输出；(chunk, metadata) 见官方文档
    for chunk, _metadata in graph.stream(inputs, stream_mode="messages"):
        # print(f"type of chunk:{type(chunk)}")  # 调试时可打开
        print(chunk.content, end="")
        # print(chunk, end="")


if __name__ == "__main__":
    main()
