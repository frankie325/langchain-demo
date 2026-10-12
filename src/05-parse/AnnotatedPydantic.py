"""
【案例】Python 入门：Pydantic + Annotated 实现带范围的运行时校验

对应教程章节：第 14 章 - 输出解析器 → 3、结构化输出（TypedDict / Pydantic / Annotated）

知识点速览：
一、和 AnnotatedTypedDict 的区别？
  - AnnotatedTypedDict.py：用 typing.Annotated 只加了「描述」元数据，**运行时不会**按「0–150」校验。
  - 本文件：用 **Pydantic** 的 Field(ge=0, le=150) 放在 Annotated 里，即 Annotated[int, Field(ge=0, le=150, ...)]，Pydantic 会在**运行时**校验数值是否在 0–150，超出则抛 ValidationError。

二、适用场景：需要「强类型 + 取值范围校验」时，用 Pydantic 模型 + Field 约束；LangChain 的结构化输出也可用这类模型做解析与校验。
"""

from typing import Annotated
from pydantic import BaseModel, Field, ValidationError

# 用 Annotated 结合 Pydantic 的 Field：ge=0, le=150 会在运行时校验，不在范围内会触发 ValidationError
Age = Annotated[int, Field(ge=0, le=150, description="年龄，范围0-150")]


class Person(BaseModel):
    name: str
    age: int
    age2: Age  # 这里 age2 会被 Pydantic 按 Field(ge=0, le=150) 校验


try:
    person = Person(
        name="z3", age=11, age2=188
    )  # age2=188 超出 0–150，会抛 ValidationError
    print(person)
except ValidationError as e:
    print("数据校验失败：")
    print(e)

"""
【输出示例】
数据校验失败：
1 validation error for Person
age2
  Input should be less than or equal to 150 [type=less_than_equal, input_value=188, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
from pydantic import BaseModel, Field, field_validator

load_dotenv(encoding="utf-8")


class Product(BaseModel):
    """产品信息：名称、类别、简介。简介长度需 ≥ 10，由下方 validator 校验。"""

    name: str = Field(description="产品名称")
    category: str = Field(description="产品类别")
    description: str = Field(description="产品简介")

    @field_validator("description")
    def validate_description(cls, value):
        """Pydantic 校验器：description 长度必须 ≥ 10，否则抛 ValueError。"""
        if len(value) < 10:
            raise ValueError("产品简介长度必须大于等于10")
        return value


# 创建 Pydantic 输出解析器：解析结果会转成 Product 实例并做校验
parser = PydanticOutputParser(pydantic_object=Product)

# 生成「格式说明」字符串，拼进 Prompt，引导模型按 Product 的字段输出 JSON
format_instructions = parser.get_format_instructions()
logger.info(format_instructions)


# 在 system 里放入 {format_instructions}，human 里放 {topic}
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个AI助手，你只能输出结构化的json数据\n{format_instructions}"),
        ("human", "请你输出标题为：{topic}的新闻内容"),
    ]
)

prompt = prompt_template.format_messages(
    topic="华为Mate X7", format_instructions=format_instructions
)
logger.info(prompt)


model = init_chat_model(
    model="gpt-6-luna",  # 模型 ID，与平台模型广场一致
    model_provider="openai",  # 表示使用「OpenAI 兼容」的 API（阿里百炼、通义等均兼容，阿里百炼不支持直接调用，需要通过OpenAI 兼容的 API 调用）
    api_key=os.getenv("OPENAI_API_KEY"),  # 需事先 export 或在下面 load_dotenv 之后再用
    base_url=os.getenv("BASE_URL"),
)


result = model.invoke(prompt)
logger.info(f"模型原始输出:\n{result.content}")

# 解析：把 result 转成 Product 实例，若格式或校验不通过会抛错
response = parser.invoke(result)
logger.info(f"解析后的结构化结果:\n{response}")
logger.info(f"结果类型: {type(response)}")  # <class 'Product'>

"""
【输出示例】
2026-02-27 15:02:47.018 | INFO     | __main__:<module>:53 - [SystemMessage(content='你是一个AI助手，你只能输出结构化的json数据\nThe output should be formatted as a JSON instance that conforms to the JSON schema below.\n\nAs an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}\nthe object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.\n\nHere is the output schema:\n```\n{"description": "产品信息：名称、类别、简介。简介长度需 ≥ 10，由下方 validator 校验。", "properties": {"name": {"description": "产品名称", "title": "Name", "type": "string"}, "category": {"description": "产品类别", "title": "Category", "type": "string"}, "description": {"description": "产品简介", "title": "Description", "type": "string"}}, "required": ["name", "category", "description"]}\n```', additional_kwargs={}, response_metadata={}), HumanMessage(content='请你输出标题为：华为Mate X7的新闻内容', additional_kwargs={}, response_metadata={})]
2026-02-27 15:02:51.175 | INFO     | __main__:<module>:63 - 模型原始输出:
{"name": "华为Mate X7", "category": "智能手机", "description": "华为Mate X7是一款全新折叠屏旗舰手机，搭载麒麟9010芯片与HarmonyOS 4.2系统，配备8英寸内屏与6.5英寸外屏，支持5G网络与超高速充电技术。"}
2026-02-27 15:02:51.175 | INFO     | __main__:<module>:67 - 解析后的结构化结果:
name='华为Mate X7' category='智能手机' description='华为Mate X7是一款全新折叠屏旗舰手机，搭载麒麟9010芯片与HarmonyOS 4.2系统，配备8英寸内屏与6.5英寸外屏，支持5G网络与超高速充电技术。'
2026-02-27 15:02:51.175 | INFO     | __main__:<module>:68 - 结果类型: <class '__main__.Product'>
"""
