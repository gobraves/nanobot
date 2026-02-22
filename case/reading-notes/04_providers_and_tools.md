# 04 Providers 与 Tools 阅读笔记

## Providers
- 抽象接口：`providers/base.py`
- 统一返回：`LLMResponse(content, tool_calls, usage, reasoning_content)`

## Tools
- 注册中心：`agent/tools/registry.py`
- 常见工具：filesystem/shell/web/message/spawn/cron/mcp

设计优点：
- provider 与 tools 通过统一协议接入 loop
- 便于替换模型和扩展能力

