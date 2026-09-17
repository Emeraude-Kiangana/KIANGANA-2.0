from kif.core.models import UsageRecord
from kif.usage.store import UsageStore


def _record(task_id: str = "t1") -> UsageRecord:
    return UsageRecord(task_id=task_id, provider="deepseek", model="deepseek-flash", input_tokens=10, output_tokens=20, total_tokens=30, estimated_cost=None, actual_cost=None, latency_ms=123)


def test_store_persists_single_record(tmp_path):
    store = UsageStore(tmp_path / "usage.jsonl")
    store.record(_record("t1"))
    loaded = store.all()
    assert len(loaded) == 1
    assert loaded[0].task_id == "t1"
    assert loaded[0].total_tokens == 30
    assert loaded[0].actual_cost is None


def test_store_appends_multiple_records(tmp_path):
    store = UsageStore(tmp_path / "usage.jsonl")
    store.record(_record("t1")); store.record(_record("t2")); store.record(_record("t3"))
    assert [u.task_id for u in store.all()] == ["t1", "t2", "t3"]


def test_empty_store_returns_empty_list(tmp_path):
    store = UsageStore(tmp_path / "missing.jsonl")
    assert store.all() == []
