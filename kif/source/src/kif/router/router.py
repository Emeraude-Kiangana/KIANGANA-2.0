from __future__ import annotations

from kif.core.models import (
    CapabilityProfile,
    ProviderError,
    ProviderErrorCode,
    ResponseEnvelope,
    TaskEnvelope,
)
from kif.providers.base import ModelProvider

_FALLBACK_CODES = frozenset(
    {
        ProviderErrorCode.TIMEOUT,
        ProviderErrorCode.PROVIDER_DOWN,
        ProviderErrorCode.RATE_LIMIT,
        ProviderErrorCode.QUOTA_EXHAUSTED,
    }
)


class Router:
    """Deterministic provider router with at most one controlled fallback."""

    def __init__(
        self,
        providers: dict[str, ModelProvider],
        *,
        primary: str | None = None,
        fallback: str | None = None,
    ) -> None:
        if not providers:
            raise ValueError("Router requires at least one provider")
        self._providers = dict(providers)
        names = list(self._providers)
        self._primary = primary or names[0]
        if self._primary not in self._providers:
            raise ValueError(f"Unknown primary provider: {self._primary}")

        if fallback is not None:
            self._fallback = fallback
        elif len(names) > 1:
            self._fallback = names[1]
        else:
            self._fallback = None

        if self._fallback is not None:
            if self._fallback not in self._providers:
                raise ValueError(f"Unknown fallback provider: {self._fallback}")
            if self._fallback == self._primary:
                raise ValueError("Primary and fallback providers must be distinct")

    async def route(self, task: TaskEnvelope) -> ResponseEnvelope:
        primary = self._providers[self._primary]
        try:
            return await primary.generate(task)
        except ProviderError as exc:
            if self._fallback is None or exc.code not in _FALLBACK_CODES:
                raise
            fallback = self._providers[self._fallback]
            return await fallback.generate(task)

    def capabilities(self) -> list[CapabilityProfile]:
        return [p.capabilities() for p in self._providers.values()]
