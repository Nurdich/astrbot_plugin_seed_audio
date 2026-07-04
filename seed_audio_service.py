"""Seed Audio 合成服务，供指令与 LLM 工具共用。"""

from __future__ import annotations

import os
import uuid
from typing import Any

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent
from astrbot.api.message_components import Image, Record
from astrbot.core.utils.astrbot_path import get_astrbot_temp_path

from .seed_audio_api import SeedAudioClient, SeedAudioError


def get_api_key(config: AstrBotConfig) -> str:
    return (config.get("X-Api-Key") or "").strip()


def build_client(config: AstrBotConfig) -> SeedAudioClient:
    return SeedAudioClient(
        get_api_key(config),
        timeout=float(config.get("request_timeout") or 180),
        model=(config.get("model") or "seed-audio-1.0").strip(),
    )


def build_audio_config(config: AstrBotConfig) -> dict:
    cfg = config.get("audio_config") or {}
    audio_config = {}
    for key in ("format", "sample_rate", "speech_rate", "loudness_rate", "pitch_rate", "enable_subtitle"):
        value = cfg.get(key)
        if value is not None and value != "":
            audio_config[key] = value
    return audio_config


def output_ext(config: AstrBotConfig) -> str:
    fmt = (config.get("audio_config") or {}).get("format") or "wav"
    if fmt == "ogg_opus":
        return ".ogg"
    if fmt == "pcm":
        return ".pcm"
    return f".{fmt}"


async def collect_references(
    event: AstrMessageEvent,
    config: AstrBotConfig,
) -> tuple[list[dict], list[str]]:
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

    speaker = (config.get("speaker") or "").strip()
    if not references and speaker:
        references.append({"speaker": speaker})

    return references, warnings


async def synthesize_to_file(
    config: AstrBotConfig,
    text_prompt: str,
    *,
    references: list[dict] | None = None,
) -> tuple[str, dict[str, Any]]:
    client = build_client(config)
    result = await client.create(
        text_prompt=text_prompt,
        references=references or None,
        audio_config=build_audio_config(config) or None,
    )
    temp_dir = get_astrbot_temp_path()
    os.makedirs(temp_dir, exist_ok=True)
    output_path = os.path.join(temp_dir, f"seed_audio_{uuid.uuid4().hex}{output_ext(config)}")
    client.save_audio(result, output_path)
    return output_path, result


async def synthesize_text(
    config: AstrBotConfig,
    text_prompt: str,
    *,
    references: list[dict] | None = None,
) -> tuple[str, dict[str, Any]]:
    text_prompt = text_prompt.strip()
    if not text_prompt:
        raise ValueError("合成文本不能为空")
    if not get_api_key(config):
        raise ValueError("请先在插件配置中填写火山引擎 API Key")

    try:
        return await synthesize_to_file(config, text_prompt, references=references)
    except SeedAudioError as exc:
        logger.error(f"[seed-audio] 合成失败: {exc}")
        raise ValueError(f"语音合成失败：{exc}") from exc
    except Exception as exc:
        logger.error(f"[seed-audio] 请求异常: {exc}")
        raise ValueError(f"请求异常：{exc}") from exc
