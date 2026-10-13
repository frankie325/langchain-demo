"""
【案例】模型标准化参数：temperature、max_tokens 等

对应教程章节：第 11 章 - Model I/O 与模型接入 → 2.5 常用模型参数、2.6 Token、max_tokens 与计费的关系、2.9 调用后的返回信息

知识点速览：
- 这是一个“观察型案例”，重点不是业务功能，而是帮助你理解模型参数与返回对象结构。
- 演示 `temperature` 如何影响输出随机性，以及 `max_tokens` 与回复长度 / 成本控制的关系。
- 也适合配合第 11 章里关于 `AIMessage`、`response.content`、`response_metadata`、`usage_metadata` 的讲解一起看。
- 依赖 `langchain`、`langchain-openai`，运行前在 `.env` 中配置 `deepseek-api`。
"""

import os
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv

load_dotenv(encoding="utf-8")


model = init_chat_model(
    model="gpt-6-luna",  # 模型 ID，与平台模型广场一致
    model_provider="openai",  # 表示使用「OpenAI 兼容」的 API（阿里百炼、通义等均兼容，阿里百炼不支持直接调用，需要通过OpenAI 兼容的 API 调用）
    api_key=os.getenv("OPENAI_API_KEY"),  # 需事先 export 或在下面 load_dotenv 之后再用
    base_url=os.getenv("BASE_URL"),
    temperature=0,  # 0～1，越高越随机；此处略高便于看到多次输出差异
    # max_tokens=256,  # 可选：限制单次回复长度
)

message = model.invoke('"写一句关于春天的词，14 字以内"')
print(message)

# <class 'langchain_openai.chat_models.base.ChatOpenAI'>
print(type(model))
# <class 'langchain_core.messages.ai.AIMessage'>
print(type(message))


"""
【输出示例】温度为 2.0 时，输出如下结果
春风拂柳，繁花满枝。
"""

"""
【输出示例】温度为 0 时，输出如下结果
风软一溪云，花明两岸春。
"""
print(message.content)
