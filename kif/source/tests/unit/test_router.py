import pytest
from kif.core.models import CapabilityProfile, ResponseEnvelope, TaskEnvelope, TaskStatus, TaskType, Usage
from kif.providers.base import ModelProvider
from kif.router.router import Router


class _StubProvider(ModelProvider):
    name = "stub"
    def __init__(self) -> None: self.calls = 0
    async def generate(self, task: TaskEnvelope) -> ResponseEnvelope:
        self.calls += 1
        return ResponseEnvelope(task_id=task.task_id, provider=self.name, model="stub-1", output="ok", status=TaskStatus.COMPLETED, usage=Usage(), latency_ms=1)
    async def health(self) -> bool: return True
    def capabilities(self) -> CapabilityProfile: return CapabilityProfile(provider=self.name)


async def test_router_routes_valid_task_to_single_provider():
    provider = _StubProvider()
    router = Router({"deepseek": provider})
    task = TaskEnvelope(type=TaskType.CHAT, input="hello")
    resp = await router.route(task)
    assert resp.provider == "stub"
    assert resp.task_id == task.task_id
    assert provider.calls == 1


def test_router_rejects_empty_provider_map():
    with pytest.raises(ValueError): Router({})
