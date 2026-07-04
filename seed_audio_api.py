"""火山引擎 Seed Audio TTS API 客户端。"""

from __future__ import annotations

import base64
import uuid
from typing import Any

import httpx

API_URL = "https://openspeech.bytedance.com/api/v3/tts/create"
DEFAULT_MODEL = "seed-audio-1.0"


class SeedAudioError(Exception):
    def __init__(self, code: int, message: str, logid: str | None = None):
        self.code = code
        self.message = message
        self.logid = logid
        super().__init__(f"[{code}] {message}" + (f" (logid={logid})" if logid else ""))


class SeedAudioClient:
    def __init__(self, api_key: str, timeout: float = 180.0, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.timeout = timeout
        self.model = model or DEFAULT_MODEL

    async def create(
        self,
        text_prompt: str,
        references: list[dict[str, Any]] | None = None,
        audio_config: dict[str, Any] | None = None,
        watermark: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "text_prompt": text_prompt,
        }
        if references:
            payload["references"] = references
        if audio_config:
            payload["audio_config"] = audio_config
        if watermark:
            payload["watermark"] = watermark

        headers = {
            "X-Api-Key": self.api_key,
            "X-Api-Request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(API_URL, json=payload, headers=headers)

        logid = response.headers.get("X-Tt-Logid")
        try:
            data = response.json()
        except Exception as exc:
            raise SeedAudioError(
                response.status_code,
                f"响应解析失败: {response.text[:200]}",
                logid,
            ) from exc

        code = data.get("code", response.status_code)
        if code != 0 or response.status_code != 200:
            raise SeedAudioError(code, data.get("message", "未知错误"), logid)

        return data

    @staticmethod
    def file_to_base64(path: str) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def save_audio(data: dict[str, Any], output_path: str) -> str:
        audio_b64 = data.get("audio")
        if not audio_b64:
            raise SeedAudioError(0, "响应中未包含音频数据")
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(audio_b64))
        return output_path
