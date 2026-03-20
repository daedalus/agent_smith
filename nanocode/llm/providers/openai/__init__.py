"""OpenAI-compatible LLM provider."""

import os
import json
from typing import Any, AsyncIterator

import httpx

from nanocode.llm.base import LLMBase, LLMResponse, ToolCall, Message, LLMBase


class OpenAILLM(LLMBase):
    """OpenAI-compatible LLM provider."""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = "gpt-4", proxy: str = None, **kwargs):
        super().__init__(api_key, base_url, model, proxy=proxy, **kwargs)
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "dummy")

    async def chat(self, messages: list, tools: list[dict] = None, **kwargs) -> LLMResponse:
        """Send a chat completion request."""
        messages = self._normalize_messages(messages)

        headers = {"Authorization": f"Bearer {self.api_key}"}
        if self.base_url and "openai" not in self.base_url:
            headers["Content-Type"] = "application/json"

        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            **kwargs,
        }

        if tools:
            payload["tools"] = tools

        def on_retry(error: Exception, attempt: int):
            print(f"\n  \033[93mRate limited, retrying (attempt {attempt})...\033[0m")

        response = await self._request_with_retry(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            on_retry=on_retry,
        )
        data = response.json()

        choice = data["choices"][0]
        msg_data = choice["message"]

        tool_calls = []
        if tc_data := msg_data.get("tool_calls"):
            for tc in tc_data:
                func = tc.get("function", {})
                tool_calls.append(
                    ToolCall(
                        name=func.get("name", ""), arguments=json.loads(func.get("arguments", "{}"))
                    )
                )

        return LLMResponse(
            content=msg_data.get("content", ""),
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason"),
            thinking=msg_data.get("reasoning"),
        )

    async def chat_stream(
        self, messages: list[Message], tools: list[dict] = None, **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion responses."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if self.base_url and "openai" not in self.base_url:
            headers["Content-Type"] = "application/json"

        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": True,
            **kwargs,
        }

        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(proxies=self.proxy) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=120.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        chunk = json.loads(data)
                        if content := chunk["choices"][0].get("delta", {}).get("content"):
                            yield content

    def get_tool_schema(self) -> list[dict]:
        """Get OpenAI function calling format."""
        return []
