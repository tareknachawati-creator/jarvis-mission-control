from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..contracts import PermissionLevel


@dataclass(frozen=True)
class CharterRule:
    action_type: str
    level: PermissionLevel
    constraints: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    description: str = ""

    def matches(self, requested_action: str) -> bool:
        if not self.enabled:
            return False
        if self.action_type == "*":
            return True
        if self.action_type.endswith(".*"):
            return requested_action.startswith(self.action_type[:-1])
        return self.action_type == requested_action

    @property
    def specificity(self) -> tuple[int, int]:
        if self.action_type == "*":
            return (0, 0)
        if self.action_type.endswith(".*"):
            return (1, len(self.action_type))
        return (2, len(self.action_type))
