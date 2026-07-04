# 更新日志

## 2026-07-04

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
- 提供 `/tts` 指令，合成后返回语音消息
- 插件配置：API Key、默认音色、音频输出参数、请求超时
- 可选开启字级别字幕并在回复中附带文本

### 文件结构

- `main.py` — AstrBot 插件主逻辑
- `seed_audio_api.py` — API 客户端封装
- `_conf_schema.json` — 插件配置 Schema
- `requirements.txt` — 依赖（httpx）
