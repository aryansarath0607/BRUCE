from __future__ import annotations

import json
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass


SYSTEM_PROMPT = """You are BRUCE, a careful Windows personal computer agent.
Return ONLY valid JSON with this shape: {\"message\": string, \"actions\": [{\"tool\": string, \"arguments\": object}]}.
Use no more than three actions. Use tools for real-world actions; do not claim an action happened without a tool result.
Available tools are supplied in the user prompt. Ask for clarification when necessary.
"""


@dataclass
class ModelReply:
    message: str
    actions: list[dict]


class Provider(ABC):
    @abstractmethod
    def complete(self, user_text: str, tools: list[dict], context: str = "") -> ModelReply:
        raise NotImplementedError


class OpenAICompatibleProvider(Provider):
    def __init__(self, base_url: str, model: str, api_key: str = ""):
        self.url = f"{base_url}/chat/completions"
        self.model = model
        self.api_key = api_key

    def complete(self, user_text: str, tools: list[dict], context: str = "") -> ModelReply:
        prompt = f"Tools:\n{json.dumps(tools)}\nContext:\n{context}\nUser:\n{user_text}"
        body = json.dumps({"model": self.model, "temperature": 0.1, "messages": [
            {"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}
        ]}).encode()
        request = urllib.request.Request(self.url, data=body, method="POST", headers={"Content-Type": "application/json"})
        if self.api_key:
            request.add_header("Authorization", f"Bearer {self.api_key}")
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RuntimeError(f"LLM request failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Cannot reach LLM provider: {exc.reason}") from exc
        content = payload["choices"][0]["message"]["content"]
        try:
            data = json.loads(content)
            return ModelReply(str(data.get("message", "")), data.get("actions", []))
        except (json.JSONDecodeError, TypeError) as exc:
            raise RuntimeError("Provider returned non-JSON output; no action was executed") from exc


class OllamaProvider(OpenAICompatibleProvider):
    def __init__(self, base_url: str, model: str):
        super().__init__(f"{base_url}/v1", model)


def provider_from_settings(settings) -> Provider:
    if settings.provider == "ollama":
        return OllamaProvider(settings.ollama_base_url, settings.model)
    if settings.provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is required when BRUCE_PROVIDER=groq")
        return OpenAICompatibleProvider(settings.groq_base_url, settings.model, settings.groq_api_key)
    raise ValueError(f"Unsupported BRUCE_PROVIDER: {settings.provider}")
