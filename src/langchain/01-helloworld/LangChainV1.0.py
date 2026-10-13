"""
【案例】LangChain 1.0 写法：init_chat_model 统一入口调用大模型

对应教程章节：第 10 章 - LangChain 快速上手与 HelloWorld → 4、实战：基于阿里百炼的 HelloWorld

知识点速览：
- 1.0 推荐用 init_chat_model 作为统一入口，通过 model_provider（如 "openai"）指定厂商，同一套写法可切换模型。
- 接国内平台（阿里百炼、通义等）时需显式写 model_provider="openai"，否则会报错无法推断 provider。
- 调用三件套：API Key、模型名、Base URL；invoke(问题) 返回消息对象，.content 取正文。
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import (
    init_chat_model,
)

load_dotenv(encoding="utf-8")

# ========== 2. 实例化模型并调用 ==========
# 关键字参数：k1=v1, k2=v2 的形式（比如这种写法：model="qwen-plus"，就是关键字参数），顺序可打乱，可读性更好
model = init_chat_model(
    model="gpt-6-luna",  # 模型 ID，与平台模型广场一致
    model_provider="openai",  # 表示使用「OpenAI 兼容」的 API（阿里百炼、通义等均兼容，阿里百炼不支持直接调用，需要通过OpenAI 兼容的 API 调用）
    api_key=os.getenv("OPENAI_API_KEY"),  # 需事先 export 或在下面 load_dotenv 之后再用
    base_url=os.getenv("BASE_URL"),
)

print(model.invoke("你是谁").content)