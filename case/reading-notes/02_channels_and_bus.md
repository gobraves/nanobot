# 02 Channels 与 Bus 阅读笔记

- 统一抽象：`channels/base.py` 中 `BaseChannel`
- 管理器：`channels/manager.py` 根据 config 初始化渠道
- outbound 分发：`ChannelManager._dispatch_outbound()`

理解方式：
- Channel = I/O 适配层
- Bus = 解耦中间层
- AgentLoop = 业务核心层

这样做能让平台接入和 agent 行为互不污染。

