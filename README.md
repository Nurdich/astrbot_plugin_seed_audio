# astrbot_plugin_seed_audio

基于火山引擎 [Seed Audio](https://www.volcengine.com/docs/6561) 非流式语音合成 API 的 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。

开发文档：

- [AstrBot 插件开发指南](https://docs.astrbot.app/dev/star/plugin-new.html)
- [AstrBot AI / Tool 开发指南](https://docs.astrbot.app/dev/star/guides/ai.html)

## 功能

- **指令合成**：`/seedtts <文本>` 直接生成语音
- **Agent 工具**：注册 `seed_audio_synthesize` 工具，对话中说「帮我生成一段语音」时 Agent 可主动调用
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
/seedtts 你好，欢迎来到有声书世界
/seedtts 请用@音频1的音色朗读：今天天气真好
/seedtts 大声说我爱你
```

> **不要用 `/tts`**：AstrBot 内置 `/tts` 用于开关会话级 TTS 功能，与 Seed Audio 合成无关。未匹配到插件指令时，消息会当作普通聊天交给 LLM，就会出现「我没有 TTS 能力」的回复。

### 对话中让 Agent 合成语音

插件按 [AI 指南](https://docs.astrbot.app/dev/star/guides/ai.html) 注册了 LLM 工具 `seed_audio_synthesize`。可直接说：

```
帮我生成一段语音，大声说我爱你
```

Agent 会调用该工具合成并发送语音。可在插件配置中关闭 `enable_llm_tool`。

## 排查指令不生效

1. WebUI → **插件**：确认 `astrbot_plugin_seed_audio` 已启用且无报错
2. WebUI → **指令管理**：搜索 `seedtts`，确认指令已启用
3. WebUI → **控制台**：确认无 `ModuleNotFoundError`，必要时手动安装 `httpx`
4. 插件目录名必须是 `astrbot_plugin_seed_audio`（不能含连字符）
5. 修改代码后点击 **重载插件**

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
| enable_llm_tool | 是否注册 LLM 工具供 Agent 调用（默认开启） |

## 限制

- 单次最长输出 120s 音频
- `text_prompt` 最大 2048 字符
- 建议输出格式使用 `wav`（AstrBot 语音消息兼容性最佳）

## 依赖

见 `requirements.txt`（`httpx`）。AstrBot 安装插件时会自动安装。

## 开发调试

修改代码后，在 WebUI 插件管理页点击「重载插件」即可热重载。
