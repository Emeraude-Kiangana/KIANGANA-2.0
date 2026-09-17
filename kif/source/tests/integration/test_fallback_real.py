import os

import pytest
from dotenv import load_dotenv

from kif.core.models import TaskEnvelope, TaskType, UsageRecord
from kif.providers.deepseek import DeepSeekAdapter
from kif.providers.groq import GroqAdapter
from kif.providers.registry import build_provider_registry
from kif.router.router import Router
from kif.usage.store import UsageStore

load_dotenv()
pytestmark = pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set; skipping real fallback integration test",
)


async def test_controlled_primary_unavailable_falls_back_to_real_groq(tmp_path):
    primary = DeepSeekAdapter(
        api_key="controlled-unavailable",
        base_url="http://127.0.0.1:9",
        timeout_s=0.5,
    )
    fallback = GroqAdapter()
    router = Router(build_provider_registry(primary, fallback))
    task = TaskEnvelope(
        type=TaskType.CHAT,
        input="Reply with exactly one word: pong",
    )
    resp = await router.route(task)

    assert resp.provider == "groq"
    assert resp.task_id == task.task_id
    assert isinstance(resp.output, str) and resp.output.strip()
    if resp.usage.total_tokens is not None:
        assert resp.usage.total_tokens > 0

    store = UsageStore(tmp_path / "usage.jsonl")
    store.record(
        UsageRecord(
            task_id=resp.task_id,
            provider=resp.provider,
            model=resp.model,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            total_tokens=resp.usage.total_tokens,
            estimated_cost=resp.estimated_cost,
            actual_cost=resp.actual_cost,
            latency_ms=resp.latency_ms,
        )
    )
    record = store.all()[0]
    assert record.provider == "groq"
    assert record.task_id == task.task_id
