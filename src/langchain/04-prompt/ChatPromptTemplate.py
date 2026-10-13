"""
【案例】用「元组 (role, content)」定义 ChatPromptTemplate 的消息

对应教程章节：第 13 章 - 提示词与消息模板 → 7、对话提示词模板（ChatPromptTemplate）

知识点速览：
- 元组写法是 `ChatPromptTemplate` 中最简洁、最常见的一种参数形式：`("角色", "内容")`。
- 它适合快速表达 system / human / ai 等角色关系，也很接近 `from_messages([...])` 的官方示例风格。
- 和字典、Message 类写法本质等价，更多是“表达风格不同”，不是“能力不同”。


- 字典写法最贴近 OpenAI 风格的消息结构：`{"role": "...", "content": "..."}`。
- 它特别适合和 JSON 配置、接口透传数据、日志回放等场景对齐。
- 从教学角度看，字典、元组、Message 类三种写法都成立；本文件重点让你看懂“数据结构长什么样”


- `SystemMessage`、`HumanMessage`、`AIMessage` 是 LangChain 最直观的消息表示方式。
- 当你希望角色语义一眼可见，或者后续可能扩展到工具调用、元数据时，Message 类写法通常更稳妥。
- 从学习路径上看：先理解元组与字典，再看 Message 类，会更容易把“角色”和“对象”对应起来。
"""

from langchain_core.prompts import ChatPromptTemplate

# 用「(role, content) 元组」的列表定义对话：system、human、ai、再一条 human（带占位符）
chatPromptTemplate = ChatPromptTemplate(
    [
        ("system", "你是一个AI开发工程师，你的名字是{name}。"),
        ("human", "你能帮我做什么?"),
        ("ai", "我能开发很多{thing}。"),
        ("human", "{user_input}"),
    ]
)

# 传入占位符变量，得到消息列表
prompt = chatPromptTemplate.format_messages(
    name="小谷AI", thing="AI", user_input="7 + 5等于多少"
)

print(prompt)


chat_prompt = ChatPromptTemplate.from_messages(
    [
        {"role": "system", "content": "你是AI助手，你的名字叫{name}。"},
        {"role": "user", "content": "请问：{question}"},
    ]
)
message = chat_prompt.format_messages(name="小问", question="什么是LangChain")
print("from_messages:", message)


from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate(
    [
        SystemMessage(content="你是AI助手，你的名字叫{name}。"),
        HumanMessage(content="请问：{question}"),
    ]
)

# 传入占位符变量，得到消息列表
message = chat_prompt.format_messages(name="亮仔", question="什么是LangChain")
print(message)
