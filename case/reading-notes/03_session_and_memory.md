# 03 Session 与 Memory 阅读笔记

## Session
- 文件：`session/manager.py`
- 存储：`workspace/sessions/*.jsonl`
- 特点：append-only、易审计、易迁移

## Memory
- 文件：`agent/memory.py`
- 双层：
  - `MEMORY.md`：长期结构化记忆
  - `HISTORY.md`：时序日志，便于 grep
- consolidation：把旧对话压缩入记忆文件，减少上下文负担

