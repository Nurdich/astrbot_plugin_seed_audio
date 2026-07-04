# Changelog

## v1.0.7 (2026-07-04)

- 修复 WebChat 下 `/seedtts`、`/seedaudio_ping` 被 Agent 接管的问题
- 通过 `on_llm_request` 钩子在 LLM 请求前拦截指令
- 修正 `should_call_llm(True)` 以禁止默认 Agent 流程

## v1.0.6 (2026-07-04)

- 对齐官方示例：成功判定 `code in (None, 0)`，音频字段兼容 `audio` / `data`
- 请求体默认携带 `watermark: {}`，与官方 payload 结构一致

## v1.0.5 (2026-07-04)

- 修复 `get_api_key` 误读 `X-Api-Key` 导致 WebUI 配置的 `api_key` 始终无效
- 新增高优先级消息拦截器，兜底处理 `/seedtts`、`/seedaudio_ping`（兼容 WebChat）
- 指令处理完成后才 `stop_event()`，避免阻断插件响应
- LLM 工具注册失败时记录错误，不再拖垮整插件加载
- 补充 AstrBot 要求的 `CHANGELOG.md`

## v1.0.4 (2026-07-04)

- LLM 工具更名为 `seed_audio_tts`，注入 TTS 策略提示
- 修复 FunctionTool `parameters` Pydantic 校验错误

## v1.0.3 (2026-07-04)

- 新增 `/seedaudio_ping` 诊断指令与 `seed_audio_service` 共用层
- 使用 `add_llm_tools()` 注册 LLM 工具

## v1.0.2 (2026-07-04)

- 指令更名为 `/seedtts`，避免与内置 `/tts` 冲突

## v1.0.1 (2026-07-04)

- 对齐 AstrBot 官方插件命名与目录规范

## v1.0.0 (2026-07-04)

- 初始版本：Seed Audio 非流式语音合成
