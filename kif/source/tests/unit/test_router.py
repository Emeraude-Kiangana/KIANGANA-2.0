import pytest

from kif.core.models import (
    CapabilityProfile,
    ProviderError,
    ProviderErrorCode,
    ResponseEnvelope,
    TaskEnvelope,
    TaskStatus,
    TaskType,
    Usage,
)
from kif.providers.base import ModelProvider
from kif.router.router import Router


class _StubProvider(ModelProvider):
    def __init__(
        self,
        name: str = "stub",
        *,
        error: ProviderError | None = None,
        output: str = "ok",
    ) -> None:
        self.name = name
        self.error = error
        self.output = output
        self.calls = 0

    async def generate(self, task: TaskEnvelope) -> ResponseEnvelope:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return ResponseEnvelope(
            task_id=task.task_id,
            provider=self.name,
            model=f"{self.name}-1",
            output=self.output,
            status=TaskStatus.COMPLETED,
            usage=Usage(),
            latency_ms=1,
        )

    async def health(self) -> bool:
        return True

    def capabilities(self) -> CapabilityProfile:
        return CapabilityProfile(provider=self.name)


async def test_router_routes_valid_task_to_single_provider():
    provider = _StubProvider()
    router = Router({"deepseek": provider})
    task = TaskEnvelope(type=TaskType.CHAT, input="hello")
    resp = await router.route(task)
    assert resp.provider == "stub"
    assert resp.task_id == task.task_id
    assert provider.calls == 1


def test_router_rejects_empty_provider_map():
    with pytest.raises(ValueError):
        Router({})


async def test_primary_success_does_not_call_fallback():
    primary = _StubProvider("deepseek")
    fallback = _StubProvider("groq")
    router = Router({"deepseek": primary, "groq": fallback})
    task = TaskEnvelope(type=TaskType.CHAT, input="hello")
    resp = await router.route(task)
    assert resp.provider == "deepseek"
    assert primary.calls == 1
    assert fallback.calls == 0


@pytest.mark.parametrize(
    "code",
    [
        ProviderErrorCode.TIMEOUT,
        ProviderErrorCode.PROVIDER_DOWN,
        ProviderErrorCode.RATE_LIMIT,
        ProviderErrorCode.QUOTA_EXHAUSTED,
    ],
)
async def test_allowed_primary_failure_calls_fallback_once(code):
    primary = _StubProvider(
        "deepseek",
        error=ProviderError(code, "primary unavailable", provider="deepseek"),
    )
    fallback = _StubProvider("groq")
    router = Router({"deepseek": primary, "groq": fallback})
    task = TaskEnvelope(type=TaskType.CHAT, input="hello")
    resp = await router.route(task)
    assert resp.provider == "groq"
    assert resp.task_id == task.task_id
    assert primary.calls == 1
    assert fallback.calls == 1


@pytest.mark.parametrize(
    "code",
    [ProviderErrorCode.AUTH_ERROR, ProviderErrorCode.INVALID_REQUEST],
)
async def test_non_fallback_errors_are_propagated(code):
    primary = _StubProvider(
        "deepseek",
        error=ProviderError(code, "bad request", provider="deepseek"),
    )
    fallback = _StubProvider("groq")
    router = Router({"deepseek": primary, "groq": fallback})
    task = TaskEnvelope(type=TaskType.CHAT, input="hello")
    with pytest.raises(ProviderError) as exc:
        await router.route(task)
    assert exc.value.code == code
    assert fallback.calls == 0


async def test_fallback_failure_is_propagated():
    primary = _StubProvider(
        "deepseek",
        error=ProviderError(
            ProviderErrorCode.PROVIDER_DOWN,
            "primary unavailable",
            provider="deepseek",
        ),
    )
    fallback = _StubProvider(
        "groq",
        error=ProviderError(
            ProviderErrorCode.RATE_LIMIT,
            "fallback unavailable",
            provider="groq",
        ),
    )
    router = Router({"deepseek": primary, "groq": fallback})
    task = TaskEnvelope(type=TaskType.CHAT, input="hello")
    with pytest.raises(ProviderError) as exc:
        await router.route(task)
    assert exc.value.provider == "groq"
    assert primary.calls == 1
    assert fallback.calls == 1
