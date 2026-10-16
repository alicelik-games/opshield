"""Tests for idempotency guard."""

import time
from warderbox.idempotency import IdempotencyGuard, DedupeResult


def test_unprotected_tool_always_allowed():
    guard = IdempotencyGuard()
    status, cached = guard.check("tool_a", {"x": 1})
    assert status == DedupeResult.ALLOWED
    assert cached is None


def test_protected_tool_first_call_allowed():
    guard = IdempotencyGuard()
    guard.add_protected_tool("send_email")
    status, cached = guard.check("send_email", {"to": "a@b.com"})
    assert status == DedupeResult.ALLOWED


def test_duplicate_blocked():
    guard = IdempotencyGuard()
    guard.add_protected_tool("send_email")
    args = {"to": "a@b.com", "body": "hi"}
    guard.record("send_email", args, result="sent")
    status, cached = guard.check("send_email", args)
    assert status == DedupeResult.DUPLICATE
    assert cached == "sent"


def test_different_args_not_duplicate():
    guard = IdempotencyGuard()
    guard.add_protected_tool("send_email")
    guard.record("send_email", {"to": "a@b.com"}, result="sent_1")
    status, _ = guard.check("send_email", {"to": "c@d.com"})
    assert status == DedupeResult.ALLOWED


def test_ttl_expiry():
    guard = IdempotencyGuard(default_ttl=0.1)
    guard.add_protected_tool("pay")
    guard.record("pay", {"amount": 100}, result="ok")
    time.sleep(0.15)
    status, _ = guard.check("pay", {"amount": 100})
    assert status == DedupeResult.ALLOWED


def test_invalidate():
    guard = IdempotencyGuard()
    guard.add_protected_tool("send_email")
    args = {"to": "a@b.com"}
    guard.record("send_email", args, result="sent")
    assert guard.invalidate("send_email", args) is True
    status, _ = guard.check("send_email", args)
    assert status == DedupeResult.ALLOWED


def test_invalidate_nonexistent():
    guard = IdempotencyGuard()
    assert guard.invalidate("nope", {"x": 1}) is False


def test_clear_all():
    guard = IdempotencyGuard()
    guard.add_protected_tool("a")
    guard.add_protected_tool("b")
    guard.record("a", {"x": 1})
    guard.record("b", {"y": 2})
    cleared = guard.clear()
    assert cleared == 2


def test_clear_specific_tool():
    guard = IdempotencyGuard()
    guard.add_protected_tool("a")
    guard.add_protected_tool("b")
    guard.record("a", {"x": 1})
    guard.record("b", {"y": 2})
    cleared = guard.clear("a")
    assert cleared == 1
    status, _ = guard.check("b", {"y": 2})
    assert status == DedupeResult.DUPLICATE


def test_remove_protected_tool():
    guard = IdempotencyGuard()
    guard.add_protected_tool("send_email")
    assert guard.is_protected("send_email") is True
    guard.remove_protected_tool("send_email")
    assert guard.is_protected("send_email") is False


def test_stats():
    guard = IdempotencyGuard()
    guard.add_protected_tool("send_email")
    guard.record("send_email", {"to": "a@b.com"}, result="sent")
    guard.check("send_email", {"to": "a@b.com"})
    stats = guard.stats()
    assert stats["active_records"] == 1
    assert stats["duplicates_blocked"] == 1
    assert "send_email" in stats["protected_tools"]


def test_hash_deterministic():
    h1 = IdempotencyGuard._hash_args({"a": 1, "b": 2})
    h2 = IdempotencyGuard._hash_args({"b": 2, "a": 1})
    assert h1 == h2


def test_custom_ttl_per_record():
    guard = IdempotencyGuard(default_ttl=3600)
    guard.add_protected_tool("pay")
    guard.record("pay", {"amount": 50}, result="ok", ttl=0.1)
    time.sleep(0.15)
    status, _ = guard.check("pay", {"amount": 50})
    assert status == DedupeResult.ALLOWED
