from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from kif.core.models import Privacy, Quality, TaskEnvelope, TaskType, UsageRecord
from kif.providers.deepseek import DeepSeekAdapter
from kif.providers.groq import GroqAdapter
from kif.providers.registry import build_provider_registry
from kif.router.router import Router
from kif.usage.store import UsageStore

_DEFAULT_USAGE_PATH = Path("tests/data/usage.jsonl")


async def _run_ask(prompt: str) -> int:
    load_dotenv()
    primary = DeepSeekAdapter()
    fallback = GroqAdapter() if os.environ.get("GROQ_API_KEY") else None
    router = Router(build_provider_registry(primary, fallback))
    store = UsageStore(_DEFAULT_USAGE_PATH)
    task = TaskEnvelope(
        type=TaskType.CHAT,
        input=prompt,
        quality=Quality.NORMAL,
        privacy=Privacy.PRIVATE,
    )
    resp = await router.route(task)
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
    print(resp.output)
    print(
        f"\n[provider={resp.provider} model={resp.model} latency_ms={resp.latency_ms} usage={resp.usage.model_dump()}]",
        file=sys.stderr,
    )
    print(f"[usage_record appended to {_DEFAULT_USAGE_PATH}]", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kif", description="KIF V0.2 CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask", help="Send a prompt through KIF")
    ask.add_argument("prompt", help="Prompt text")
    args = parser.parse_args(argv)
    if args.command == "ask":
        return asyncio.run(_run_ask(args.prompt))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
