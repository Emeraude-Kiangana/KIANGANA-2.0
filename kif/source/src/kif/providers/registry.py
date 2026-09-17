from __future__ import annotations

from kif.providers.base import ModelProvider


def build_provider_registry(
    primary: ModelProvider,
    fallback: ModelProvider | None = None,
) -> dict[str, ModelProvider]:
    """Build the deterministic V0.2 provider order: primary, then optional fallback."""
    registry: dict[str, ModelProvider] = {primary.name: primary}
    if fallback is not None:
        if fallback.name == primary.name:
            raise ValueError("Primary and fallback providers must be distinct")
        registry[fallback.name] = fallback
    return registry
