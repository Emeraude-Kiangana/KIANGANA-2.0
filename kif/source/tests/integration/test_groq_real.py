import os

import pytest
from dotenv import load_dotenv

from kif.core.models import TaskEnvelope, TaskType, UsageRecord
from kif.providers.groq import GroqAdapter
from kif.router.router import Router
from kif.usage.store import UsageStore

load_dotenv()
pytestmark = pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set; skipping real integration test",
)


async def test_real_groq_roundtrip(tmp_path):
    adapter = GroqAdapter()
    router = Router({adapter.name: adapter})
    task = TaskEnvelope(
        type=TaskType.CHAT,
        input="Reply with exactly one word: pong",
    )
    resp = await router.route(task)
    assert resp.provider == "groq"
    assert isinstance(resp.model, str) and resp.model
    assert resp.task_id == task.task_id
    assert isinstance(resp.output, str) and resp.output.strip()
    if resp.usage.total_tokens is not None:
        assert resp.usage.total_tokens > 0
    assert resp.actual_cost is None

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
    persisted = store.all()
    assert len(persisted) == 1
    assert persisted[0].provider == "groq"
    assert persisted[0].task_id == resp.task_id
