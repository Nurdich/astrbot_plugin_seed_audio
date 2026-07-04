# astrbot_plugin_seed_audio

基于火山引擎 [Seed Audio](https://www.volcengine.com/docs/6561) 非流式语音合成 API 的 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。

开发文档：[AstrBot 插件开发指南](https://docs.astrbot.app/dev/star/plugin-new.html)

## 功能

- **纯文本生成**：用自然语言描述所需音效、音色等
- **参考音频生成**：附带语音消息，文本中可用 `@音频1`、`@音频2` 引用
- **参考图片生成**：附带图片，文本为待合成内容
- **音色 ID**：在插件配置中设置默认 `speaker`

## 安装

```bash
git clone https://github.com/AstrBotDevs/AstrBot
mkdir -p AstrBot/data/plugins
cd AstrBot/data/plugins
git clone <本仓库地址> astrbot_plugin_seed_audio
```

然后在 AstrBot WebUI 插件管理中重载插件，并填写 **API Key**（[控制台获取](https://console.volcengine.com/speech/new/setting/apikeys)）。

> 插件目录名须为合法 Python 标识符（推荐 `astrbot_plugin_seed_audio`），不要使用 `seed-audio` 这类带连字符的名称。

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

见 `requirements.txt`（`httpx`）。AstrBot 安装插件时会自动安装。

## 开发调试

修改代码后，在 WebUI 插件管理页点击「重载插件」即可热重载。
