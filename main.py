import os
import tempfile
import uuid

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Image, Record
from astrbot.api.star import Context, Star, register

from .seed_audio_api import SeedAudioClient, SeedAudioError


@register("seed_audio", "seed-audio", "火山引擎 Seed Audio 语音合成插件", "1.0.0")
class SeedAudioPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    async def initialize(self):
        if not self.config.get("api_key"):
            logger.warning("[seed-audio] 未配置 API Key，/tts 指令将不可用")

    def _build_audio_config(self) -> dict:
        cfg = self.config.get("audio_config") or {}
        audio_config = {}
        for key in ("format", "sample_rate", "speech_rate", "loudness_rate", "pitch_rate", "enable_subtitle"):
            value = cfg.get(key)
            if value is not None and value != "":
                audio_config[key] = value
        return audio_config

    async def _collect_references(self, event: AstrMessageEvent) -> tuple[list[dict], list[str]]:
        """从消息链提取参考资源，返回 (references, warnings)。"""
        references: list[dict] = []
        warnings: list[str] = []
        audio_count = 0
        image_count = 0

        for comp in event.get_messages():
            if isinstance(comp, Record):
                if image_count > 0:
                    warnings.append("图片参考不能与音频参考混用，已忽略后续音频")
                    break
                if audio_count >= 3:
                    warnings.append("最多支持 3 条参考音频，超出部分已忽略")
                    continue
                path = await comp.convert_to_file_path()
                references.append({"audio_data": SeedAudioClient.file_to_base64(path)})
                audio_count += 1
            elif isinstance(comp, Image):
                if audio_count > 0:
                    warnings.append("图片参考不能与音频参考混用，已忽略图片")
                    continue
                if image_count >= 1:
                    warnings.append("最多支持 1 张参考图片，超出部分已忽略")
                    continue
                path = await comp.convert_to_file_path()
                references.append({"image_data": SeedAudioClient.file_to_base64(path)})
                image_count += 1

        speaker = (self.config.get("speaker") or "").strip()
        if not references and speaker:
            references.append({"speaker": speaker})

        return references, warnings

    def _format_subtitle(self, subtitle: dict | None) -> str:
        if not subtitle:
            return ""
        lines = [f"字幕：{subtitle.get('text', '')}"]
        for sentence in subtitle.get("sentences") or []:
            start = sentence.get("start_time", 0)
            end = sentence.get("end_time", 0)
            lines.append(f"[{start}-{end}ms] {sentence.get('text', '')}")
        return "\n".join(lines)

    @filter.command("tts")
    async def tts(self, event: AstrMessageEvent, text: str = ""):
        """使用 Seed Audio 合成语音。支持纯文本、参考音频（@音频N）、参考图片模式。"""
        api_key = (self.config.get("api_key") or "").strip()
        if not api_key:
            yield event.plain_result("请先在插件配置中填写火山引擎 API Key。")
            return

        text_prompt = text.strip()
        if not text_prompt:
            yield event.plain_result(
                "用法：/tts <文本或提示词>\n"
                "参考音频：附带语音并可在文本中使用 @音频1 @音频2\n"
                "参考图片：附带图片，文本为待合成内容\n"
                "纯提示词：直接描述所需音效、音色等"
            )
            return

        references, warnings = await self._collect_references(event)
        model = (self.config.get("model") or "seed-audio-1.0").strip()
        client = SeedAudioClient(
            api_key,
            timeout=float(self.config.get("request_timeout") or 180),
            model=model,
        )

        try:
            result = await client.create(
                text_prompt=text_prompt,
                references=references or None,
                audio_config=self._build_audio_config() or None,
            )
        except SeedAudioError as exc:
            logger.error(f"[seed-audio] 合成失败: {exc}")
            yield event.plain_result(f"语音合成失败：{exc}")
            return
        except Exception as exc:
            logger.error(f"[seed-audio] 请求异常: {exc}")
            yield event.plain_result(f"请求异常：{exc}")
            return

        audio_cfg = self.config.get("audio_config") or {}
        fmt = audio_cfg.get("format") or "wav"
        if fmt == "ogg_opus":
            ext = ".ogg"
        elif fmt == "pcm":
            ext = ".pcm"
        else:
            ext = f".{fmt}"

        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"seed_audio_{uuid.uuid4().hex}{ext}")

        try:
            client.save_audio(result, output_path)
        except SeedAudioError as exc:
            yield event.plain_result(f"音频保存失败：{exc}")
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

        chain.append(Comp.Record(file=output_path, url=output_path, text=text_prompt))
        yield event.chain_result(chain)

    async def terminate(self):
        pass
