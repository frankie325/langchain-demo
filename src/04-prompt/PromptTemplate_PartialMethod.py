"""
【案例】PromptTemplate 的 invoke() 方法

对应教程章节：第 13 章 - 提示词与消息模板 → 6、文本提示词模板（PromptTemplate）

知识点速览：
- `invoke(...)` 返回的不是普通字符串，而是 `PromptValue`，更适合衔接 LangChain 的链式调用。
- 对 `PromptTemplate` 来说，返回值通常是 `StringPromptValue`；你可以继续 `.to_string()`，也可以 `.to_messages()`。
- 其中 `.to_messages()` 常见会转成单条 `HumanMessage`，它是把文本 Prompt 包装成消息的一种统一方式。
"""

from langchain_core.prompts import PromptTemplate

# ---------- 1. 创建模板 ----------
template = PromptTemplate.from_template(
    "你是一个专业的{role}工程师，请回答我的问题给出回答，我的问题是：{question}"
)

# ---------- 2. partial(role="python开发")：固定 role，得到「新模板」----------
# 新模板只剩 {question} 需要填，适合多轮只换问题、不换角色的场景
partial = template.partial(role="python开发")
print(partial)
print(type(partial))
print()

# ---------- 3. 对新模板 format，只传 question 即可 ----------
prompt = partial.format(question="冒泡排序怎么写？")
print(prompt)
print(type(prompt))

"""
【输出示例】
input_variables=['question'] input_types={} partial_variables={'role': 'python开发'} template='你是一个专业的{role}工程师，请回答我的问题给出回答，我的问题是：{question}'
<class 'langchain_core.prompts.prompt.PromptTemplate'>

# 你是一个专业的python开发工程师，请回答我的问题给出回答，我的问题是：冒泡排序怎么写？
# <class 'str'>
"""