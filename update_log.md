# 更新日志

## 2026-07-04

### 修复插件与 Agent 均未生效的问题

- LLM 工具改为官方推荐的 `FunctionTool` + `add_llm_tools()` 注册
- 新增 `/seedaudio_ping` 诊断指令，用于确认插件是否加载
- 抽取 `seed_audio_service.py` 供指令与工具共用

- 按 [AI 开发指南](https://docs.astrbot.app/dev/star/guides/ai.html) 注册 `seed_audio_synthesize` 工具
- Agent 可在对话中主动调用语音合成，无需记忆 `/seedtts` 指令
- 新增配置项 `enable_llm_tool`（默认开启）
- 抽取 `_synthesize()` 复用指令与工具逻辑

### 修复 /tts 被 LLM 接管的问题

- 指令更名为 `/seedtts`（别名 `seed_tts`、`seedaudio`），避免与 AstrBot 内置 `/tts`（会话 TTS 开关）冲突
- 文本参数改用 `GreedyStr`，支持带空格的合成内容
- 指令执行时调用 `event.stop_event()`，防止继续走 LLM 流程
- README 补充排查步骤

### 对齐 AstrBot 官方插件规范

- `metadata.yaml` 插件名改为 `astrbot_plugin_seed_audio`（推荐 `astrbot_plugin_` 前缀）
- 临时音频文件改存 `data/temp`（`get_astrbot_temp_path()`）
- 语音消息改用 `Comp.Record.fromFileSystem()` 发送
- README 安装步骤与[官方开发指南](https://docs.astrbot.app/dev/star/plugin-new.html)一致

### 新增模型配置

- 插件配置增加 `model` 字段，默认 `seed-audio-1.0`

### 修复导入错误

- 修复 AstrBot 加载时 `No module named 'seed_audio_api'`：改用相对导入 `from .seed_audio_api`

### 新增 Seed Audio 语音合成插件

- 集成火山引擎 `POST /api/v3/tts/create` 非流式接口
- 支持纯文本、参考音频（`@音频N`）、参考图片三种生成模式
- 提供 `/seedtts` 指令（`/tts` 与 AstrBot 内置 TTS 开关冲突，已更名）
- 插件配置：API Key、默认音色、音频输出参数、请求超时
- 可选开启字级别字幕并在回复中附带文本

### 文件结构

- `main.py` — AstrBot 插件主逻辑
- `seed_audio_api.py` — API 客户端封装
- `_conf_schema.json` — 插件配置 Schema
- `requirements.txt` — 依赖（httpx）
