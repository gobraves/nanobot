# nanobot 项目深入阅读总结

## 项目定位
nanobot 是一个“超轻量”的个人 AI Agent 框架，目标是以较少代码实现可运行的 Agent 系统（多渠道、工具调用、会话、记忆、定时任务）。

## 核心特点（代码层）

1. **Agent Loop 清晰、可读性高**
   - 入口：`nanobot/agent/loop.py`
   - 机制：LLM 生成 tool_calls -> 执行工具 -> 把 tool result 回填消息 -> 再调用 LLM。
   - 通过 `max_iterations` 防止无限循环。

2. **总线化解耦（Bus）**
   - `nanobot/bus/queue.py` + `bus/events.py`。
   - Channel 只负责收/发消息，AgentLoop 专注推理与工具，降低耦合。

3. **多渠道适配统一接口**
   - `nanobot/channels/base.py` 定义统一 Channel 抽象。
   - 各平台（telegram/discord/slack/whatsapp/...）实现 `start/stop/send`。
   - `ChannelManager` 负责按配置装配和分发 outbound。

4. **Provider 抽象层规范**
   - `nanobot/providers/base.py` 定义 `LLMProvider` 与统一响应 `LLMResponse`。
   - 方便替换后端（OpenAI / LiteLLM / 自定义 provider）。

5. **会话持久化简单直接**
   - `nanobot/session/manager.py` 使用 JSONL 存储，便于审计与排障。
   - `Session` append-only，保留工具相关元信息（tool_calls/tool_call_id/name）。

6. **双层记忆设计（Memory + History）**
   - `nanobot/agent/memory.py`
   - `MEMORY.md` 存长期事实，`HISTORY.md` 存可 grep 的事件日志。
   - 通过 LLM 工具调用 `save_memory` 完成 consolidation。

7. **MCP、Subagent、Cron 能力可选接入**
   - `agent/tools/mcp.py`, `agent/subagent.py`, `cron/service.py`。
   - 保持核心最小闭环，同时支持能力扩展。

## 适合人群
- 想研究 Agent Loop 基本机制的开发者/研究者
- 想快速做“可跑”的 Agent 原型
- 需要较低认知负担的教学或 demo 场景

## 可能的限制
- 轻量化带来“治理能力”相对有限（复杂权限、企业级审计、分布式调度等需要自行增强）
- 高并发/多租户场景需要补充更多工程化组件

## 建议阅读顺序
1. `nanobot/agent/loop.py`
2. `nanobot/agent/context.py`
3. `nanobot/agent/tools/registry.py` + 常用 tools
4. `nanobot/session/manager.py`
5. `nanobot/channels/base.py` + `channels/manager.py`
6. `nanobot/providers/base.py`
7. `nanobot/agent/memory.py`

