"""
【案例】并行链：同时运行多条子链，汇总结果

对应教程章节：第 15 章 - LCEL 与链式调用 → 4.4 RunnableParallel（并行链）

知识点速览：
- `RunnableParallel` 解决的是“同一输入，要同时跑多条子链”的问题。
- 结果会以 `dict` 形式汇总返回，键名对应并行结构里的键，值对应每条子链的输出。
- 除了显式写 `RunnableParallel({...})`，LCEL 里也常直接用字典表达并行结构；并行完成后，还可以继续把这个字典交给后续链做总结或比较。
"""

import os

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from loguru import logger

from dotenv import load_dotenv

load_dotenv(encoding="utf-8")

model = init_chat_model(
    model="gpt-6-luna",  # 模型 ID，与平台模型广场一致
    model_provider="openai",  # 表示使用「OpenAI 兼容」的 API（阿里百炼、通义等均兼容，阿里百炼不支持直接调用，需要通过OpenAI 兼容的 API 调用）
    api_key=os.getenv("OPENAI_API_KEY"),  # 需事先 export 或在下面 load_dotenv 之后再用
    base_url=os.getenv("BASE_URL"),
)

# 子链 1：中文简短介绍
prompt1 = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个知识渊博的计算机专家，请用中文简短回答"),
        ("human", "请简短介绍什么是{topic}"),
    ]
)
parser1 = StrOutputParser()
chain1 = prompt1 | model | parser1

# 子链 2：英文简短介绍（与 chain1 同结构，仅提示词语言不同）
prompt2 = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个知识渊博的计算机专家，请用英文简短回答"),
        ("human", "请简短介绍什么是{topic}"),
    ]
)
parser2 = StrOutputParser()
chain2 = prompt2 | model | parser2

# RunnableParallel：同一输入会同时喂给多个子链，结果按键汇总为 dict
parallel_chain = RunnableParallel({"chinese": chain1, "english": chain2})

# 一次 invoke，返回 {"chinese": "...", "english": "..."}
result = parallel_chain.invoke({"topic": "langchain"})
logger.info(result)

# 可选：打印并行链的 ASCII 图结构，便于理解“并行节点 + 汇总输出”的数据流
parallel_chain.get_graph().print_ascii()
