"""
=====================================================================
asyncio 学习笔记：async / await / 事件循环 / 协程 vs 线程
（本脚本为教学演示，可直接 `python demo_asyncio.py` 运行）
=====================================================================

【1. 核心概念】
- 协程(coroutine)：用 async def 定义，调用它不立即执行，返回一个协程对象。
- 事件循环(event loop)：单线程调度器，负责在多个协程之间切换。
- await：唯一的交接点。遇到 await 时当前协程挂起，控制权交还事件循环，
         事件循环转去跑其他就绪任务，等结果就绪再回来继续。
  => 一句话：await 是"等结果 + 让出控制权"，不是"启动任务"。

【2. 事件循环的三大组件】（一次迭代大致流程）
- 就绪队列(ready)：call_soon / create_task 把"现在就能跑"的回调塞这里。
- 定时器堆(scheduled)：call_later / asyncio.sleep 这类延时任务。
- I/O 多路复用(selector)：操作系统同时盯多个 socket（epoll/kqueue/IOCP）。
循环流程：把到点的定时器移入就绪队列 → 执行就绪回调 → 空闲时
selector.select 等待 I/O / 最近的定时器 → 重复。全程单线程。

【3. create_task 的语义（最重要，易误解）】
- create_task 不是"冻结"任务，而是把它"排进事件循环的就绪队列"，
  事件循环一转动就会运行它（通过 call_soon 安排第一步）。
- 因此：即使 main 里不显式 await 任务，asyncio.run 退出前也会驱动
  事件循环去取消/清理这些"挂着"的任务 —— 任务的第一步仍会被执行
  （如打印"A 开始"），随后在 await 处让出并被取消，不会打印"结束"。
- 这是【反模式】：结果会丢失，且可能告警。务必把 task await 掉。

【4. 串行 vs 并发：区别只在"任务何时进入循环"】
- 串行：await 在前、fetch 在后 → 每个任务必须等上一个完整跑完才进入循环。
- 并发：create_task 在前、await 在后 → 所有任务先进入循环，再统一等待 → 一起开始。
铁律：想并发，就先把所有任务 create_task "发射"出去，最后再 await。

【5. 协程 vs 线程】
- 线程：操作系统内核抢占式调度，开销大（MB 级栈），共享内存需加锁，受 GIL 限制。
- 协程：用户态事件循环协作式调度（只在 await 处让出），开销极小，
  单线程内"并发"而非"并行"，一般不需锁。
- 结论：协程解决 I/O 并发，线程/多进程解决 CPU 并行。

【6. Python await vs JS await】
- 语义一致：都是"异步等待点，不阻塞线程，结果就绪后继续"。
- 差异：JS 绑 Promise(thenable)，Python 绑 coroutine/Future(__await__ 协议)；
  Python 必须显式 asyncio.run（无顶层 await）；超时 JS 用 AbortController、
  Python 用 asyncio.wait_for；取消 Python 是语言级 Task.cancel()。

【7. 常见陷阱】
- 文件名不能用标准库名（如 asyncio.py 会遮蔽标准库，导致循环导入）。
- 忘了 await → 拿到 coroutine 对象，函数实际没执行。
- 协程里写 time.sleep / requests → 卡死整个事件循环（要用 asyncio.sleep / aiohttp）。
- 创建 task 却不 await → 反模式，结果丢失、可能告警。
- 纯 CPU 计算不会因 async 变快（要并行得用多进程 multiprocessing）。
=====================================================================
"""

import asyncio


async def fetch(name, delay):
    """模拟一次 I/O 任务：打印开始 → 等待 → 打印结束 → 返回结果。"""
    print(f"{name} 开始")
    # 关键：await 让出控制权；事件循环在此期间转去跑其他就绪任务（如 task_b）
    await asyncio.sleep(delay)
    print(f"{name} 结束")
    return name


async def main():
    # ===================== 演示一：串行（顺序 await）=====================
    # !与任务不同，直接等待协程（await fetch）并不会将控制权交还给事件循环
    # await 在前、fetch 在后：A 必须完整跑完（开始→结束），B 才有机会开始。
    # 输出：A 开始 / A 结束 / B 开始 / B 结束
    await fetch("A", 1)
    await fetch("B", 2)

    # ===================== 演示二：并发（先 create_task 再 await）=====================
    # ① create_task：把 A、B 都"登记"进事件循环的就绪队列（已发射，待调度）。
    #    注意：此时它们还没真正运行，只是排进队列，等事件循环转动才会跑。
    task_a = asyncio.create_task(fetch("A", 1))
    task_b = asyncio.create_task(fetch("B", 2))

    # ② 这期间（main 还没 await）A、B 已进入队列，事件循环一有机会就并发运行。
    #    下面这句打印会夹在 A/B 的"开始"之间或之前，取决于调度顺序。
    print("任务已创建，主协程暂停前先做点别的")

    # ③ 显式 await：让 main 让出控制权并等待结果（正确做法）。
    #    由于 A、B 早已并发进入队列，这里 await 时它们一起跑。
    #    输出（接上面）：A 开始 / B 开始 / A 结束 / B 结束 / A B
    result_a = await task_a
    result_b = await task_b
    print(result_a, result_b)

    # ===================== 演示三（反模式，已注释）：create_task 后不 await =====================
    # 如果只创建任务却从不 await：
    #     task_x = asyncio.create_task(fetch("X", 1))
    # main 会一口气同步跑完，asyncio.run 收尾时驱动事件循环去取消这些任务，
    # 于是任务第一步被执行（打印"X 开始"），但在 await sleep 处被取消，
    # 不会打印"结束"，结果也拿不到。这是不可依赖的行为，务必 await！


async def coro_a():
    print("I am coro_a(). Hi!")


async def coro_b():
    print("I am coro_b(). I sure hope no one hogs the event loop...")


async def main2():
    task_b = asyncio.create_task(coro_b())
    num_repeats = 3
    for _ in range(num_repeats):
        # !与任务不同，直接等待协程（await fetch）并不会将控制权交还给事件循环
        # await coro_a()
        """
        I am coro_a(). Hi!
        I am coro_a(). Hi!
        I am coro_a(). Hi!
        I am coro_b(). I sure hope no one hogs the event loop...
        """
        await asyncio.create_task(coro_a())
        """
        I am coro_b(). I sure hope no one hogs the event loop...
        I am coro_a(). Hi!
        I am coro_a(). Hi!
        I am coro_a(). Hi!
         """
    await task_b


# asyncio.run(main())

asyncio.run(main2())
