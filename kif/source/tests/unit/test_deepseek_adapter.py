import httpx

from kif.core.models import TaskEnvelope, TaskStatus, TaskType
from kif.providers.deepseek import DeepSeekAdapter


class _FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, *, json, headers):
        return httpx.Response(200, json={"model": "deepseek-flash", "choices": [{"message": {"content": "pong"}}], "usage": {"prompt_tokens": 7, "completion_tokens": 1, "total_tokens": 8}}, request=httpx.Request("POST", url))


async def test_successful_provider_response_is_normalized(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)
    adapter = DeepSeekAdapter(api_key="test-key-not-real")
    task = TaskEnvelope(type=TaskType.CHAT, input="Reply with pong")
    response = await adapter.generate(task)
    assert response.task_id == task.task_id
    assert response.provider == "deepseek"
    assert response.model == "deepseek-flash"
    assert response.output == "pong"
    assert response.status == TaskStatus.COMPLETED
    assert response.usage.input_tokens == 7
    assert response.usage.output_tokens == 1
    assert response.usage.total_tokens == 8
    assert response.estimated_cost is None
    assert response.actual_cost is None
    assert response.latency_ms >= 0
