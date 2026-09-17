from __future__ import annotations

from kif.core.models import CapabilityProfile, ResponseEnvelope, TaskEnvelope
from kif.providers.base import ModelProvider


class Router:
    """Gate Zero router: single-provider, no scoring, no fallback."""

    def __init__(self, providers: dict[str, ModelProvider]) -> None:
        if not providers:
            raise ValueError("Router requires at least one provider")
        self._providers = dict(providers)

    async def route(self, task: TaskEnvelope) -> ResponseEnvelope:
        provider = next(iter(self._providers.values()))
        return await provider.generate(task)

    def capabilities(self) -> list[CapabilityProfile]:
        return [p.capabilities() for p in self._providers.values()]
