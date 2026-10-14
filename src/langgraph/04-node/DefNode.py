"""
【案例】节点定义方式与可选参数：普通节点、带额外参数的节点（用 partial 绑定）、以及 add_node 时传入 RetryPolicy 配置重试策略。

对应教程章节：第 24 章 - LangGraph API：节点、边与进阶 → 1、Graph API 之 Node（节点）

知识点速览：
- Node 本质上是被图调度的 Python 函数；本例重点不是业务逻辑，而是理解“节点如何被 add_node 注册进图”。
- 节点常见返回值是对 State 的局部更新 dict，而不是整份完整状态；若节点需要额外参数，可用 functools.partial 预先绑定，再传给 add_node。
- add_node(name, node_func, retry_policy=RetryPolicy(...)) 说明节点除了函数本身，还能挂执行策略；本例顺手演示了 retry_policy 的挂法。
"""

from functools import partial
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from requests import RequestException, Timeout


class GraphState(TypedDict):
    process_data: dict


def input_node(state: GraphState) -> dict:
    print(f"input_node 收到的初始值:{state}")
    return {"process_data": {"input": "input_value"}}


# 节点可带额外参数，用 partial 绑定后传给 add_node
def process_node(state: dict, param1: int, param2: str) -> dict:
    print(state, param1, param2)
    return {"process_data": {"process": "process_value"}}


# 重试策略：仅对 RequestException、Timeout 重试，最多 3 次
retry_policy = RetryPolicy(
    max_attempts=3,
    initial_interval=1,
    jitter=True,
    backoff_factor=2,
    retry_on=[RequestException, Timeout],
)

stateGraph = StateGraph(GraphState)
stateGraph.add_node("input", input_node)
process_with_params = partial(process_node, param1=100, param2="test")

stateGraph.add_node("process", process_with_params, retry_policy=retry_policy)
stateGraph.add_edge(START, "input")
stateGraph.add_edge("input", "process")
stateGraph.add_edge("process", END)

graph = stateGraph.compile()

print(stateGraph.edges)
print(stateGraph.nodes)
print(graph.get_graph().print_ascii())
print()

initial_state = {"process_data": 5}
result = graph.invoke(initial_state)
print(f"最后的结果是:{result}")
