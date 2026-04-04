import logging
from dataclasses import dataclass
from typing import Iterable

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMResponse:
    content: str


class LLMClient:
    def __init__(self) -> None:
        self.base_url = settings.llm_base_url.rstrip("/")
        self.model = settings.llm_model
        self.timeout = settings.llm_timeout_sec

    def generate(self, prompt: str) -> LLMResponse:
        if settings.llm_provider != "ollama":
            raise LLMError("サポートしていないLLMプロバイダーです")

        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.exception("LLM呼び出しに失敗")
            raise LLMError("LLM呼び出しに失敗しました。ローカル実行基盤を確認してください") from exc

        content = data.get("response", "")
        if not content:
            raise LLMError("LLMからの応答が空です")
        return LLMResponse(content=content)

    def generate_with_context(self, messages: Iterable[dict]) -> LLMResponse:
        if settings.llm_provider != "ollama":
            raise LLMError("サポートしていないLLMプロバイダーです")

        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "messages": list(messages), "stream": False}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.exception("LLMチャット呼び出しに失敗")
            raise LLMError("LLMチャット呼び出しに失敗しました。ローカル実行基盤を確認してください") from exc

        message = data.get("message", {})
        content = message.get("content", "") if isinstance(message, dict) else ""
        if not content:
            raise LLMError("LLMからの応答が空です")
        return LLMResponse(content=content)
