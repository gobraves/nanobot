# 01 Agent Loop 阅读笔记

- 主类：`AgentLoop`
- 核心方法：
  - `run()`：从 bus 持续消费 inbound 消息
  - `_process_message()`：单条消息处理（session、context、slash command、memory consolidation）
  - `_run_agent_loop()`：模型-工具迭代核心

关键点：
- 通过 `self.tools.get_definitions()` 把工具 schema 交给模型
- 模型返回 `tool_calls` 后，逐个 `tools.execute(...)`
- 每次工具结果都用 `context.add_tool_result(...)` 回填消息序列
- 直至模型返回无工具调用的 final content

