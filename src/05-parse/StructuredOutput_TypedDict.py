"""
【案例】用 TypedDict + Annotated 做结构化输出

对应教程章节：第 14 章 - 输出解析器 → 3、结构化输出（TypedDict / Pydantic / Annotated）

知识点速览：
一、什么是「结构化输出」？
  - 希望模型返回的不是随便一段话，而是固定结构的数据（如指定字段的 dict），方便程序后续处理。
  - LangChain 支持用 TypedDict（Python 标准库）或 Pydantic 定义结构，再由模型按该结构生成并解析。

二、with_structured_output 做什么？
  - 在模型上调用 llm.with_structured_output(某个类型)，会返回一个「带了结构化输出能力」的可调用对象。
  - 调用 .invoke(messages) 时，模型会被引导输出符合该结构的 JSON，并自动解析成 Python 的 dict（或对应类型），无需再手写 Parser。

三、本案例：用 typing.TypedDict 定义 Animal（动物名 + emoji）、AnimalList（动物列表）；用 Annotated 给字段加描述，便于模型理解各字段含义；最后用 llm.with_structured_output(AnimalList) 一次得到结构化结果。
"""

import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv(encoding="utf-8")

model = init_chat_model(
    model="gpt-6-luna",  # 模型 ID，与平台模型广场一致
    model_provider="openai",  # 表示使用「OpenAI 兼容」的 API（阿里百炼、通义等均兼容，阿里百炼不支持直接调用，需要通过OpenAI 兼容的 API 调用）
    api_key=os.getenv("OPENAI_API_KEY"),  # 需事先 export 或在下面 load_dotenv 之后再用
    base_url=os.getenv("BASE_URL"),
)


class Animal(TypedDict):
    animal: Annotated[str, "动物"]
    emoji: Annotated[str, "表情"]


# 定义「动物列表」：一个字段 animals，类型是 Animal 的列表
class AnimalList(TypedDict):
    animals: Annotated[list[Animal], "动物与表情列表"]


# 普通对话消息
messages = [{"role": "user", "content": "任意生成三种动物，以及他们的 emoji 表情"}]

resp = model.with_structured_output(AnimalList).invoke(messages)

print(
    resp
)  # 得到符合 AnimalList 的 dict，如 {"animals": [{"animal": "猫", "emoji": "🐱"}, ...]}

"""
【输出示例】
{'animals': [{'animal': '狗', 'emoji': '🐶'}, {'animal': '猫', 'emoji': '🐱'}, {'animal': '鸟', 'emoji': '🐦'}]}
"""
