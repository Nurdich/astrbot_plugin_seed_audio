# 更新日志

## 2026-07-04

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
- 修复 AstrBot 加载时 `No module named 'seed_audio_api'`：改用相对导入 `from .seed_audio_api`

### 新增模型配置

- 插件配置增加 `model` 字段，默认 `seed-audio-1.0`
