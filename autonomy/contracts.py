from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from typing import Any
from uuid import uuid4


class AutonomyMode(StrEnum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    OBSERVE_ONLY = "OBSERVE_ONLY"
    STOPPED = "STOPPED"


class PermissionLevel(IntEnum):
    OBSERVE = 0
    DO_FREELY = 1
    DO_AND_TELL = 2
    ASK_FIRST = 3
    PROHIBITED = 4


class PolicyDisposition(StrEnum):
    ALLOW = "allow"
    ALLOW_AND_NOTIFY = "allow_and_notify"
    REQUIRE_APPROVAL = "require_approval"
    OBSERVE_ONLY = "observe_only"
    DENY = "deny"


class EventState(StrEnum):
    PENDING = "pending"
    LEASED = "leased"
    COMPLETED = "completed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Event:
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 50
    source: str = "local"
    dedupe_key: str | None = None
    correlation_id: str | None = None
    causation_id: str | None = None
    schema_version: int = 1
    event_id: str = field(default_factory=lambda: "evt_" + uuid4().hex)

    def __post_init__(self) -> None:
        if not self.event_type or not self.event_type.strip():
            raise ValueError("event_type is required")
        if not 0 <= self.priority <= 100:
            raise ValueError("priority must be between 0 and 100")
        if self.schema_version < 1:
            raise ValueError("schema_version must be positive")


@dataclass(frozen=True)
class ActionRequest:
    action_type: str
    arguments: dict[str, Any] = field(default_factory=dict)
    reversible: bool = False
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not self.action_type or not self.action_type.strip():
            raise ValueError("action_type is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class PolicyDecision:
    action_type: str
    mode: AutonomyMode
    level: PermissionLevel
    disposition: PolicyDisposition
    reason: str
    matched_rule: str | None = None

    @property
    def permits_execution(self) -> bool:
        return self.disposition in {
            PolicyDisposition.ALLOW,
            PolicyDisposition.ALLOW_AND_NOTIFY,
        }
