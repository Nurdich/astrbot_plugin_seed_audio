# Seed Audio 语音合成插件

基于火山引擎 [Seed Audio](https://www.volcengine.com/docs/6561) 非流式语音合成 API 的 AstrBot 插件。

支持：

- **纯文本生成**：用自然语言描述所需音效、音色等
- **参考音频生成**：附带语音消息，文本中可用 `@音频1`、`@音频2` 引用
- **参考图片生成**：附带图片，文本为待合成内容
- **音色 ID**：在插件配置中设置默认 `speaker`

## 安装

1. 将本仓库克隆到 `AstrBot/data/plugins/seed-audio`
2. 在 AstrBot WebUI 插件管理中重载插件
3. 在插件配置中填写 **API Key**（[控制台获取](https://console.volcengine.com/speech/new/setting/apikeys)）

## 使用

```
/tts 你好，欢迎来到有声书世界
/tts 请用@音频1的音色朗读：今天天气真好
/tts 这是一段待合成的旁白文本
```

- 附带语音消息 → 参考音频模式（最多 3 条，每条 ≤30s）
- 附带图片消息 → 参考图片模式（最多 1 张）
- 仅文本 → 纯提示词或音色合成（需配置 `speaker`）

## 配置项

| 配置 | 说明 |
|------|------|
| api_key | 火山引擎 X-Api-Key |
| model | 模型版本，默认 `seed-audio-1.0` |
| speaker | 默认音色 ID（可选） |
| audio_config | 输出格式、采样率、语速、音量、音调、字幕 |
| request_timeout | 请求超时（默认 180s） |

## 限制

- 单次最长输出 120s 音频
- `text_prompt` 最大 2048 字符
- 建议输出格式使用 `wav`（AstrBot 语音消息兼容性最佳）

## 依赖

- httpx
