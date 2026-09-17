import pytest
from pydantic import ValidationError
from kif.core.models import ProviderError, ProviderErrorCode, Privacy, Quality, ResponseEnvelope, TaskEnvelope, TaskStatus, TaskType, Usage, UsageRecord


def test_task_envelope_defaults():
    t = TaskEnvelope(type=TaskType.CHAT, input="hi")
    assert t.task_id.startswith("task_")
    assert t.quality == Quality.NORMAL
    assert t.privacy == Privacy.PRIVATE
    assert t.budget_max_usd == 0.10


def test_task_envelope_rejects_empty_input():
    with pytest.raises(ValidationError):
        TaskEnvelope(type=TaskType.CHAT, input="")


def test_task_envelope_forbids_extra():
    with pytest.raises(ValidationError):
        TaskEnvelope(type=TaskType.CHAT, input="hi", rogue="x")


def test_response_envelope_costs_can_be_null():
    r = ResponseEnvelope(task_id="t", provider="p", model="m", output="o", status=TaskStatus.COMPLETED, usage=Usage(), latency_ms=5)
    assert r.estimated_cost is None
    assert r.actual_cost is None


def test_usage_record_roundtrip():
    u = UsageRecord(task_id="t", provider="p", model="m", input_tokens=1, output_tokens=2, total_tokens=3, estimated_cost=None, actual_cost=None, latency_ms=10)
    assert UsageRecord.model_validate_json(u.model_dump_json()) == u


def test_provider_error_carries_normalized_code():
    err = ProviderError(ProviderErrorCode.RATE_LIMIT, "slow down", provider="p", status_code=429)
    assert err.code == ProviderErrorCode.RATE_LIMIT
    assert err.status_code == 429
    assert "RATE_LIMIT" in str(err)
