from __future__ import annotations

from collections.abc import Iterable

from .models import CharterRule
from ..contracts import (
    ActionRequest,
    AutonomyMode,
    PermissionLevel,
    PolicyDecision,
    PolicyDisposition,
)


class PolicyEngine:
    """Deterministic authority gate. Model output never bypasses this class."""

    SAFE_WHILE_STOPPED = frozenset({"system.status.read", "audit.read"})

    def __init__(self, rules: Iterable[CharterRule]):
        self._rules = tuple(rules)
        if not any(rule.action_type == "*" for rule in self._rules):
            raise ValueError("A fail-closed wildcard charter rule is required")

    @property
    def rules(self) -> tuple[CharterRule, ...]:
        return self._rules

    def matching_rule(self, action_type: str) -> CharterRule:
        matches = [rule for rule in self._rules if rule.matches(action_type)]
        if not matches:
            raise RuntimeError("Charter has no matching or fallback rule")
        return max(matches, key=lambda rule: rule.specificity)

    def evaluate(self, request: ActionRequest, mode: AutonomyMode) -> PolicyDecision:
        rule = self.matching_rule(request.action_type)
        level = rule.level

        if mode is AutonomyMode.STOPPED and request.action_type not in self.SAFE_WHILE_STOPPED:
            return self._decision(request, mode, level, PolicyDisposition.DENY,
                                  "Hard kill switch is active.", rule)

        if level is PermissionLevel.PROHIBITED:
            return self._decision(request, mode, level, PolicyDisposition.DENY,
                                  "The charter prohibits this action.", rule)

        constraint_failure = self._check_constraints(request, rule)
        if constraint_failure:
            return self._decision(request, mode, level, PolicyDisposition.DENY,
                                  constraint_failure, rule)

        if mode is AutonomyMode.PAUSED and level > PermissionLevel.OBSERVE:
            return self._decision(request, mode, level, PolicyDisposition.DENY,
                                  "Autonomy is paused; only observation is allowed.", rule)

        if mode is AutonomyMode.OBSERVE_ONLY and level > PermissionLevel.OBSERVE:
            return self._decision(request, mode, level, PolicyDisposition.OBSERVE_ONLY,
                                  "Shadow mode recorded the proposal without executing it.", rule)

        dispositions = {
            PermissionLevel.OBSERVE: PolicyDisposition.ALLOW,
            PermissionLevel.DO_FREELY: PolicyDisposition.ALLOW,
            PermissionLevel.DO_AND_TELL: PolicyDisposition.ALLOW_AND_NOTIFY,
            PermissionLevel.ASK_FIRST: PolicyDisposition.REQUIRE_APPROVAL,
        }
        return self._decision(request, mode, level, dispositions[level],
                              "Authorized by the active charter rule.", rule)

    @staticmethod
    def _check_constraints(request: ActionRequest, rule: CharterRule) -> str | None:
        constraints = rule.constraints
        if constraints.get("reversible") and not request.reversible:
            return "The charter requires this action to be reversible."
        minimum = constraints.get("confidence_min")
        if minimum is not None and request.confidence < float(minimum):
            return f"Confidence {request.confidence:.2f} is below the required {float(minimum):.2f}."
        return None

    @staticmethod
    def _decision(request, mode, level, disposition, reason, rule) -> PolicyDecision:
        return PolicyDecision(
            action_type=request.action_type,
            mode=mode,
            level=level,
            disposition=disposition,
            reason=reason,
            matched_rule=rule.action_type,
        )
