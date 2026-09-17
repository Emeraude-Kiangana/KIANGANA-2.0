import pytest

from kif.core.models import CapabilityProfile, ResponseEnvelope, TaskEnvelope
from kif.providers.base import ModelProvider
from kif.providers.registry import build_provider_registry


class _Provider(ModelProvider):
    def __init__(self, name: str):
        self.name = name

    async def generate(self, task: TaskEnvelope) -> ResponseEnvelope:
        raise NotImplementedError

    async def health(self) -> bool:
        return True

    def capabilities(self) -> CapabilityProfile:
        return CapabilityProfile(provider=self.name)


def test_registry_preserves_primary_then_fallback_order():
    registry = build_provider_registry(_Provider("deepseek"), _Provider("groq"))
    assert list(registry) == ["deepseek", "groq"]


def test_registry_rejects_duplicate_provider_names():
    with pytest.raises(ValueError):
        build_provider_registry(_Provider("deepseek"), _Provider("deepseek"))
