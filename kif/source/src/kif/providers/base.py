from __future__ import annotations

from abc import ABC, abstractmethod

from kif.core.models import CapabilityProfile, ResponseEnvelope, TaskEnvelope


class ModelProvider(ABC):
    name: str

    @abstractmethod
    async def generate(self, task: TaskEnvelope) -> ResponseEnvelope: ...

    @abstractmethod
    async def health(self) -> bool: ...

    @abstractmethod
    def capabilities(self) -> CapabilityProfile: ...
