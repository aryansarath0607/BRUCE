from __future__ import annotations

from bruce.planner import Planner
from bruce.recovery import RecoveryLoop

def test_planner_generates_steps():
    class FakeProvider:
        def complete(self, user_text, tools, context):
            return type("Reply", (), {"message": "I will do it.", "actions": [{"tool": "remember", "arguments": {"fact": "user likes concise answers"}}]})()

    plan = Planner(FakeProvider()).build("remember my preference", [], "")
    assert len(plan.steps) == 1
    assert plan.steps[0].tool == "remember"


def test_recovery_loop_handles_failure():
    class FakeProvider:
        def complete(self, user_text, tools, context):
            return type("Reply", (), {"message": "Retrying with a safer step.", "actions": [{"tool": "remember", "arguments": {"fact": "fallback"}}]})()

    class FakeToolRegistry:
        def descriptions(self):
            return []
        tools = {"remember": type("Tool", (), {"handler": lambda self, args: None})()}

    loop = RecoveryLoop(FakeProvider(), FakeToolRegistry(), None)
    outcome = loop.recover("test", {"tool": "open_application"}, "failed")
    assert outcome.message
