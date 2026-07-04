import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.core.star.filter.command import GreedyStr

from .seed_audio_service import collect_references, get_api_key, synthesize_text
from .tools.seed_audio_tool import SeedAudioSynthesizeTool


@register(
    "astrbot_plugin_seed_audio",
    "seed-audio",
    "火山引擎 Seed Audio 语音合成插件",
    "1.0.3",
)
class SeedAudioPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        if self.config.get("enable_llm_tool", True):
            tool = SeedAudioSynthesizeTool()
            tool.plugin = self
            self.context.add_llm_tools(tool)

    async def initialize(self):
        if not get_api_key(self.config):
            logger.warning("[seed-audio] 未配置 API Key，语音合成功能将不可用")
            return
        logger.info("[seed-audio] 插件已加载：/seedtts /seedaudio_ping")
        if self.config.get("enable_llm_tool", True):
            logger.info("[seed-audio] LLM 工具 seed_audio_synthesize 已通过 add_llm_tools 注册")

    def _format_subtitle(self, subtitle: dict | None) -> str:
        if not subtitle:
            return ""
        lines = [f"字幕：{subtitle.get('text', '')}"]
        for sentence in subtitle.get("sentences") or []:
            start = sentence.get("start_time", 0)
            end = sentence.get("end_time", 0)
            lines.append(f"[{start}-{end}ms] {sentence.get('text', '')}")
        return "\n".join(lines)

    async def _reply_audio(self, event: AstrMessageEvent, text_prompt: str):
        references, warnings = await collect_references(event, self.config)
        try:
            output_path, result = await synthesize_text(
                self.config,
                text_prompt,
                references=references or None,
            )
        except ValueError as exc:
            yield event.plain_result(str(exc))
            return

        duration = result.get("duration")
        original_duration = result.get("original_duration")
        info_parts = []
        if duration is not None:
            info_parts.append(f"时长 {duration:.1f}s")
        if original_duration is not None and original_duration != duration:
            info_parts.append(f"原始时长 {original_duration:.1f}s")

        chain: list = []
        if warnings:
            chain.append(Comp.Plain("\n".join(warnings)))
        if info_parts:
            chain.append(Comp.Plain("，".join(info_parts)))

        subtitle_text = self._format_subtitle(result.get("subtitle"))
        if subtitle_text:
            chain.append(Comp.Plain(subtitle_text))

        chain.append(Comp.Record.fromFileSystem(output_path, text=text_prompt))
        yield event.chain_result(chain)

    @filter.command("seedaudio_ping", priority=10)
    async def seedaudio_ping(self, event: AstrMessageEvent):
        """检查 Seed Audio 插件是否已正确加载。"""
        event.stop_event()
        api_status = "已配置" if get_api_key(self.config) else "未配置"
        tool_status = "已注册" if self.config.get("enable_llm_tool", True) else "已关闭"
        yield event.plain_result(
            "Seed Audio 插件运行正常 (v1.0.3)\n"
            f"API Key：{api_status}\n"
            f"LLM 工具：{tool_status} (seed_audio_synthesize)\n"
            "合成指令：/seedtts <文本>"
        )

    @filter.command("seedtts", alias={"seed_tts", "seedaudio"}, priority=10)
    async def seedtts(self, event: AstrMessageEvent, text: GreedyStr = ""):
        """使用 Seed Audio 合成语音。支持纯文本、参考音频（@音频N）、参考图片模式。"""
        event.stop_event()
        if not text.strip():
            yield event.plain_result(
                "用法：/seedtts <文本或提示词>\n"
                "诊断：/seedaudio_ping\n"
                "参考音频：附带语音并可在文本中使用 @音频1 @音频2\n"
                "参考图片：附带图片，文本为待合成内容\n"
                "也可直接说「帮我生成语音」，由 Agent 调用 seed_audio_synthesize 工具\n"
                "注意：/tts 是 AstrBot 内置 TTS 开关，与本插件无关"
            )
            return
        async for result in self._reply_audio(event, text):
            yield result

    async def terminate(self):
        pass
