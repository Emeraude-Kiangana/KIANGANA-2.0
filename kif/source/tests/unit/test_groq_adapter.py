import httpx
import pytest

from kif.core.models import ProviderError, ProviderErrorCode, TaskEnvelope, TaskStatus, TaskType
from kif.providers.groq import GroqAdapter


class _FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, *, json, headers):
        return httpx.Response(
            200,
            json={
                "model": "openai/gpt-oss-20b",
                "choices": [{"message": {"content": "pong"}}],
                "usage": {
                    "prompt_tokens": 9,
                    "completion_tokens": 2,
                    "total_tokens": 11,
                },
            },
            request=httpx.Request("POST", url),
        )


async def test_successful_groq_response_is_normalized(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)
    adapter = GroqAdapter(api_key="test-key-not-real")
    task = TaskEnvelope(type=TaskType.CHAT, input="Reply with pong")
    response = await adapter.generate(task)
    assert response.task_id == task.task_id
    assert response.provider == "groq"
    assert response.model == "openai/gpt-oss-20b"
    assert response.output == "pong"
    assert response.status == TaskStatus.COMPLETED
    assert response.usage.input_tokens == 9
    assert response.usage.output_tokens == 2
    assert response.usage.total_tokens == 11
    assert response.estimated_cost is None
    assert response.actual_cost is None


def test_missing_groq_key_raises_auth_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ProviderError) as exc:
        GroqAdapter()
    assert exc.value.code == ProviderErrorCode.AUTH_ERROR


@pytest.mark.parametrize(
    "status,expected",
    [
        (400, ProviderErrorCode.INVALID_REQUEST),
        (401, ProviderErrorCode.AUTH_ERROR),
        (402, ProviderErrorCode.QUOTA_EXHAUSTED),
        (429, ProviderErrorCode.RATE_LIMIT),
        (500, ProviderErrorCode.PROVIDER_DOWN),
    ],
)
def test_groq_http_status_normalization(status, expected):
    adapter = GroqAdapter(
        api_key="test-key-not-real",
        base_url="https://example.invalid",
    )
    resp = httpx.Response(
        status,
        json={"error": {"message": "boom"}},
        request=httpx.Request("POST", "https://example.invalid/chat/completions"),
    )
    with pytest.raises(ProviderError) as exc:
        adapter._raise_normalized(resp)
    assert exc.value.code == expected
