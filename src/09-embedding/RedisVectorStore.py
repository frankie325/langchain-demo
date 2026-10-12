"""
【案例】使用 langchain_redis 将文本写入 Redis 向量库（add_texts）

对应教程章节：第 19 章 - RAG 检索增强生成 → 2.1.1 from_documents 与 add_texts；也可与第 18 章向量库写入案例对照阅读

知识点速览：
- 这个案例展示的是纯文本流驱动的入库路线：先创建 `RedisVectorStore`，再通过 `add_texts()` 把字符串列表写入向量库。
- `add_texts(texts, metadata)` 会在内部调用 `embed_documents(texts)` 做批量向量化，然后把文本、向量和 metadata 一起写入 Redis。
- 这条路线和 `from_documents(...)` 并不冲突：前者更适合你手里已经是纯文本列表，后者更适合你已经有 `Document` 列表。
- 本例里额外手动执行了一次 `embed_documents`，目的是先观察“向量长什么样、维度是多少”；真正做存储时，这一步不是必须的。
- 返回的 ids 可用于后续更新、删除或追踪；index_name 需要和后续检索端保持一致。
"""

from langchain_redis import RedisConfig, RedisVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# 1. 初始化嵌入模型
embeddingsModel = DashScopeEmbeddings(
    model="text-embedding-v3", dashscope_api_key=os.getenv("aliQwen-api")
)

# 2. 待写入的文本及（可选）元数据
texts = [
    "我喜欢吃苹果",
    "苹果是我最喜欢吃的水果",
    "我喜欢用苹果手机",
]

# 批量转成向量：这里只是为了先观察向量维度和内容；真正写入时 add_texts 内部会再次完成向量化
embeddings = embeddingsModel.embed_documents(texts)
for i, vec in enumerate(embeddings, 1):
    print(f"文本 {i}: {texts[i-1]}")
    print(f"向量长度: {len(vec)}")
    print(f"前5个向量值: {vec[:10]}\n")


# 定义每条文本对应的元数据信息
# metadata = [{"segment_id": "1"}, {"segment_id": "2"}, {"segment_id": "3"}]
# 定义每条文本对应的元数据信息；真实 RAG 中这些 metadata 往往来自 Document.metadata，也可作为来源展示或过滤条件
metadata = [{"segment_id": str(i)} for i in range(1, len(texts) + 1)]


# 3. Redis 连接与索引名（需与检索案例一致）
config = RedisConfig(
    index_name="newsgroups",
    redis_url=os.getenv("REDIS_STACK_URL"),
)

# 创建 Redis 向量存储实例：此时只是“连上库 + 指定索引配置”，还没真正写入文本；真正写入发生在 add_texts()
vector_store = RedisVectorStore(embeddingsModel, config=config)

# 4. 将文本与元数据写入向量库（add_texts 内部会调 embed_documents，无需先算向量）
ids = vector_store.add_texts(texts, metadata)

# 打印前5个存储记录的ID
print(ids[0:5])