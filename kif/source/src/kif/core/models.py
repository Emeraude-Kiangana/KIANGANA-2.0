from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class TaskType(str, Enum):
    CHAT = "chat"
    CODE = "code"
    REASONING = "reasoning"
    SUMMARIZATION = "summarization"


class Quality(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Privacy(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    SECRET = "secret"


class TaskStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class TaskEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str = Field(default_factory=lambda: f"task_{uuid4().hex[:16]}")
    type: TaskType
    input: str = Field(min_length=1)
    quality: Quality = Quality.NORMAL
    privacy: Privacy = Privacy.PRIVATE
    budget_max_usd: float = Field(default=0.10, ge=0.0)


class Usage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class ResponseEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    provider: str
    model: str
    output: str
    status: TaskStatus
    usage: Usage
    estimated_cost: float | None = None
    actual_cost: float | None = None
    latency_ms: int


class CapabilityProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    text: bool = True
    reasoning: bool = False
    code: bool = False
    tools: bool = False
    vision: bool = False
    cost_class: str = "UNKNOWN"


class ProviderErrorCode(str, Enum):
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    TIMEOUT = "TIMEOUT"
    PROVIDER_DOWN = "PROVIDER_DOWN"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNKNOWN_PROVIDER_ERROR = "UNKNOWN_PROVIDER_ERROR"


class ProviderError(Exception):
    def __init__(
        self,
        code: ProviderErrorCode,
        message: str,
        *,
        provider: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{code.value}] {message}")


class UsageRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    estimated_cost: float | None
    actual_cost: float | None
    latency_ms: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
