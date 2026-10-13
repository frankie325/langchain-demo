"""
【案例】文本提示词模板：partial_variables 与 partial()

对应教程章节：第 13 章 - 提示词与消息模板 → 6、文本提示词模板（PromptTemplate）

知识点速览：
- `partial_variables` 用于“创建模板时就固定一部分变量”，`partial()` 用于“已有模板上再固定一部分变量”。
- 两者都能实现“先固定公共部分，后续只传变化部分”，只是发生的时机不同。
- 真实项目里，这类写法很适合沉淀稳定角色、固定规则、时间戳等公共上下文。
"""

from langchain_core.prompts import PromptTemplate
from datetime import datetime
import time

# ---------- 1. 创建时用 partial_variables 固定「时间」----------
# 写法一：构造函数。input_variables 只写「后续 format 还要传」的变量（这里只剩 question；time 已用 partial_variables 固定）
template1 = PromptTemplate(
    template="现在时间是：{time},请对我的问题给出答案，我的问题是：{question}",
    input_variables=["question"],
    partial_variables={"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
)

# 写法二（等价）：from_template(..., partial_variables={...})
# template1 = PromptTemplate.from_template(
#     "现在时间是：{time},请对我的问题给出答案，我的问题是：{question}",
#     partial_variables={"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# )

prompt1 = template1.format(question="今天是几号？")
print(prompt1)

time.sleep(2)

# 现在时间是：2026-10-10 17:42:27,请对我的问题给出答案，我的问题是：今天是几号？