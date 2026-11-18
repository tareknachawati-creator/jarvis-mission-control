import unittest

from autonomy.contracts import (
    ActionRequest,
    AutonomyMode,
    PermissionLevel,
    PolicyDisposition,
)
from autonomy.charter.models import CharterRule
from autonomy.charter.policy_engine import PolicyEngine


class PolicyEngineTests(unittest.TestCase):

    def setUp(self):
        self.engine = PolicyEngine([
            CharterRule("*", PermissionLevel.PROHIBITED),
            CharterRule("system.status.read", PermissionLevel.OBSERVE),
            CharterRule("system.restart", PermissionLevel.ASK_FIRST),
        ])

    def test_unknown_action_is_denied(self):
        decision = self.engine.evaluate(
            ActionRequest("unknown.action"),
            AutonomyMode.ACTIVE,
        )
        self.assertEqual(decision.disposition, PolicyDisposition.DENY)

    def test_read_action_is_allowed(self):
        decision = self.engine.evaluate(
            ActionRequest("system.status.read"),
            AutonomyMode.ACTIVE,
        )
        self.assertEqual(decision.disposition, PolicyDisposition.ALLOW)

    def test_restart_requires_approval(self):
        decision = self.engine.evaluate(
            ActionRequest("system.restart"),
            AutonomyMode.ACTIVE,
        )
        self.assertEqual(
            decision.disposition,
            PolicyDisposition.REQUIRE_APPROVAL,
        )

    def test_stopped_mode_denies_restart(self):
        decision = self.engine.evaluate(
            ActionRequest("system.restart"),
            AutonomyMode.STOPPED,
        )
        self.assertEqual(decision.disposition, PolicyDisposition.DENY)


if __name__ == "__main__":
    unittest.main()
