from langchain_ollama import ChatOllama
import os

from dotenv import load_dotenv

load_dotenv(encoding="utf-8")


# ---------- 第一步：创建“聊天客户端” ----------
# ChatOllama 是 LangChain 中连接本地 Ollama 服务的聊天模型类。
# 你可以把它理解成“本地模型版本的 Chat Model 客户端”：
# - base_url：Ollama 服务根地址（本机默认 http://localhost:11434）
# - model：已通过 ollama pull / ollama run 拉取到本机的模型标签
# - reasoning：是否开启推理/思考模式（是否支持取决于具体模型）
model = ChatOllama(
    model="qwen3.5:4b",
    base_url=os.getenv("OLLAMA_BASE_URL"),
    reasoning=False,
)

# ---------- 第二步：发一条消息并打印回复 ----------
# invoke(问题) 会把输入发给本地模型，并返回一个 LangChain 的消息对象（通常是 AIMessage）。
# 直接 print(response) 适合观察完整对象结构；业务里若只关心正文，一般读取 response.content。
response = model.invoke("什么是LangChain，100字以内回答")
print(response)
print(response.content)

"""
【可选】如果你只想看到模型回复的纯文字，可以这样取：
print(response.content)
"""