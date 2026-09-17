from __future__ import annotations

import os
import time

import httpx

from kif.core.models import (
    CapabilityProfile,
    ProviderError,
    ProviderErrorCode,
    ResponseEnvelope,
    TaskEnvelope,
    TaskStatus,
    Usage,
)
from kif.providers.base import ModelProvider

_DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
_DEFAULT_MODEL = "openai/gpt-oss-20b"


class GroqAdapter(ModelProvider):
    name = "groq"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_s: float = 60.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("GROQ_API_KEY")
        self._base_url = (
            base_url or os.environ.get("GROQ_BASE_URL") or _DEFAULT_BASE_URL
        ).rstrip("/")
        self._model = model or os.environ.get("GROQ_MODEL") or _DEFAULT_MODEL
        self._timeout = timeout_s

        if not self._api_key:
            raise ProviderError(
                ProviderErrorCode.AUTH_ERROR,
                "GROQ_API_KEY is not set in the environment",
                provider=self.name,
            )

    def capabilities(self) -> CapabilityProfile:
        return CapabilityProfile(
            provider=self.name,
            text=True,
            reasoning=True,
            code=True,
            tools=False,
            vision=False,
            cost_class="LOW",
        )

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self._base_url}/models",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def generate(self, task: TaskEnvelope) -> ResponseEnvelope:
        started = time.perf_counter()
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": task.input}],
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
        except httpx.TimeoutException as exc:
            raise ProviderError(
                ProviderErrorCode.TIMEOUT, str(exc), provider=self.name
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(
                ProviderErrorCode.PROVIDER_DOWN, str(exc), provider=self.name
            ) from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        self._raise_normalized(resp)

        try:
            data = resp.json()
        except ValueError as exc:
            raise ProviderError(
                ProviderErrorCode.INVALID_RESPONSE,
                f"Groq returned non-JSON body: {exc}",
                provider=self.name,
                status_code=resp.status_code,
            ) from exc

        try:
            output = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                ProviderErrorCode.INVALID_RESPONSE,
                f"Unexpected Groq response shape: {exc}",
                provider=self.name,
                status_code=resp.status_code,
            ) from exc

        raw_usage = data.get("usage") or {}
        usage = Usage(
            input_tokens=raw_usage.get("prompt_tokens"),
            output_tokens=raw_usage.get("completion_tokens"),
            total_tokens=raw_usage.get("total_tokens"),
        )
        return ResponseEnvelope(
            task_id=task.task_id,
            provider=self.name,
            model=data.get("model", self._model),
            output=output,
            status=TaskStatus.COMPLETED,
            usage=usage,
            estimated_cost=None,
            actual_cost=None,
            latency_ms=latency_ms,
        )

    def _raise_normalized(self, resp: httpx.Response) -> None:
        if resp.is_success:
            return
        status = resp.status_code
        detail: str | None = None
        try:
            body = resp.json()
            if isinstance(body, dict):
                err = body.get("error")
                if isinstance(err, dict):
                    detail = err.get("message")
                elif isinstance(err, str):
                    detail = err
        except ValueError:
            detail = resp.text[:200] if resp.text else None

        code_map = {
            400: ProviderErrorCode.INVALID_REQUEST,
            401: ProviderErrorCode.AUTH_ERROR,
            402: ProviderErrorCode.QUOTA_EXHAUSTED,
            403: ProviderErrorCode.AUTH_ERROR,
            404: ProviderErrorCode.INVALID_REQUEST,
            408: ProviderErrorCode.TIMEOUT,
            429: ProviderErrorCode.RATE_LIMIT,
        }
        if status in code_map:
            code = code_map[status]
        elif 500 <= status < 600:
            code = ProviderErrorCode.PROVIDER_DOWN
        else:
            code = ProviderErrorCode.UNKNOWN_PROVIDER_ERROR
        raise ProviderError(
            code,
            detail or f"HTTP {status}",
            provider=self.name,
            status_code=status,
        )
