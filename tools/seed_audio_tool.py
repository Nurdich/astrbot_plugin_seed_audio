"""Seed Audio LLM 工具。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field
from pydantic.dataclasses import dataclass

from astrbot.api import logger
from astrbot.core.agent.run_context import ContextWrapper
from astrbot.core.agent.tool import FunctionTool, ToolExecResult
from astrbot.core.astr_agent_context import AstrAgentContext

import astrbot.api.message_components as Comp

from ..seed_audio_service import collect_references, synthesize_text

if TYPE_CHECKING:
    from ..main import SeedAudioPlugin


@dataclass
class SeedAudioSynthesizeTool(FunctionTool[AstrAgentContext]):
    """按 AstrBot AI 指南通过 add_llm_tools 注册。"""

    name: str = "seed_audio_synthesize"
    description: str = (
        "使用火山引擎 Seed Audio 将文本合成为语音并发送给用户。"
        "当用户要求生成语音、朗读文字、TTS、文字转语音时调用此工具。"
    )
    parameters: dict = Field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "待合成文本，或描述音效、音色、语气的提示词",
                },
            },
            "required": ["text"],
        }
    )

    def __post_init__(self):
        self.plugin: SeedAudioPlugin | None = None

    async def call(
        self,
        context: ContextWrapper[AstrAgentContext],
        **kwargs,
    ) -> ToolExecResult:
        plugin = self.plugin
        if plugin is None:
            return "Seed Audio 插件未正确初始化"

        if not plugin.config.get("enable_llm_tool", True):
            return "插件未启用 LLM 工具，请使用 /seedtts 指令"

        text = (kwargs.get("text") or "").strip()
        if not text:
            return "合成文本不能为空"

        event = context.context.event
        references, warnings = await collect_references(event, plugin.config)

        try:
            output_path, result = await synthesize_text(
                plugin.config,
                text,
                references=references or None,
            )
        except ValueError as exc:
            return str(exc)

        duration = result.get("duration")
        info = f"已合成语音：{text}"
        if duration is not None:
            info += f"（时长 {duration:.1f}s）"
        if warnings:
            info += "\n" + "\n".join(warnings)

        chain = [Comp.Record.fromFileSystem(output_path, text=text)]
        await event.send(event.chain_result(chain))
        logger.info(f"[seed-audio] LLM 工具已发送语音: {text[:50]}")
        return info
