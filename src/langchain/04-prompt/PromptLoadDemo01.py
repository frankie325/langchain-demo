"""
【案例】从 JSON 文件加载提示词模板

对应教程章节：第 13 章 - 提示词与消息模板 → 8、从文件加载提示词（JSON / YAML）

知识点速览：
- 把 Prompt 放到 JSON / YAML 里，有助于版本管理、多人协作和 A/B 测试，也能避免长提示词把业务代码挤得很乱。
- `load_prompt(...)` 会根据文件内容加载出模板对象；对于本案例的 `_type: "prompt"`，它会得到一个 `PromptTemplate` 风格的对象。
- 通过 `Path(__file__)` 从脚本所在目录定位 `prompt.json`，不依赖运行命令时的工作目录。
"""

from pathlib import Path

# 从 langchain_core 引入 load_prompt，用于从 JSON/YAML 加载模板
from langchain_core.prompts import load_prompt

# 从脚本所在目录加载 prompt.json，得到与 PromptTemplate 用法相同的模板对象
# encoding="utf-8" 保证中文等字符正常显示
prompt_path = Path(__file__).resolve().with_name("prompt.json")
template = load_prompt(prompt_path, encoding="utf-8")

# 用 .format() 填入占位符变量，得到最终字符串（与第 6 节 PromptTemplate.format 的使用方式一致）
print(template.format(name="张三", what="搞笑的"))
"""
【输出示例】
请张三讲一个搞笑的的故事
"""
# 从 YAML 加载提示词模板，API 与 load_prompt("prompt.json") 一致
prompt_path = Path(__file__).resolve().with_name("prompt.yaml")
template = load_prompt(prompt_path, encoding="utf-8")
print(template.format(name="年轻人", what="滑稽"))
"""
【输出示例】
请年轻人讲一个滑稽的故事
"""
