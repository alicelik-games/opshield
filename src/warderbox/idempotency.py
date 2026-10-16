"""Idempotency guard for agent tool calls.

Prevents duplicate execution of the same logical operation,
so retries of send_email or payment calls don't double-fire.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DedupeResult(Enum):
    ALLOWED = "allowed"
    DUPLICATE = "duplicate"


@dataclass
class IdempotencyRecord:
    """A record of a previously executed action."""

    key: str
    tool_name: str
    args_hash: str
    result: Any = None
    timestamp: float = field(default_factory=time.time)
    ttl: float = 3600.0


class IdempotencyGuard:
    """Detects and blocks duplicate tool calls.

    An idempotency key is computed from the tool name and its arguments.
    If the same key appears within the TTL window, the call is blocked
    and the cached result is returned instead.

    Usage:
        guard = IdempotencyGuard(default_ttl=3600)
        guard.add_protected_tool("send_email")

        status, cached = guard.check("send_email", {"to": "a@b.com", "body": "hi"})
        if status == DedupeResult.DUPLICATE:
            return cached  # don't execute again
    """

    def __init__(
        self,
        default_ttl: float = 3600.0,
        protected_tools: set[str] | None = None,
    ) -> None:
        self._default_ttl = default_ttl
        self._protected_tools: set[str] = protected_tools or set()
        self._records: dict[str, IdempotencyRecord] = {}
        self._lock = threading.Lock()
        self._duplicates_blocked = 0

    def add_protected_tool(self, tool_name: str, ttl: float | None = None) -> None:
        self._protected_tools.add(tool_name)

    def remove_protected_tool(self, tool_name: str) -> None:
        self._protected_tools.discard(tool_name)

    def is_protected(self, tool_name: str) -> bool:
        return tool_name in self._protected_tools

    @staticmethod
    def _hash_args(args: dict) -> str:
        serialized = json.dumps(args, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    @staticmethod
    def _make_key(tool_name: str, args_hash: str) -> str:
        return f"{tool_name}:{args_hash}"

    def check(
        self, tool_name: str, args: dict
    ) -> tuple[DedupeResult, Any | None]:
        """Check if this call is a duplicate.

        Returns (ALLOWED, None) for new calls, or
        (DUPLICATE, cached_result) for repeated ones.
        """
        if tool_name not in self._protected_tools:
            return DedupeResult.ALLOWED, None

        args_hash = self._hash_args(args)
        key = self._make_key(tool_name, args_hash)
        now = time.time()

        with self._lock:
            self._cleanup(now)
            record = self._records.get(key)
            if record is not None:
                self._duplicates_blocked += 1
                return DedupeResult.DUPLICATE, record.result
            return DedupeResult.ALLOWED, None

    def record(
        self,
        tool_name: str,
        args: dict,
        result: Any = None,
        ttl: float | None = None,
    ) -> str:
        """Record a completed execution for deduplication."""
        args_hash = self._hash_args(args)
        key = self._make_key(tool_name, args_hash)
        entry = IdempotencyRecord(
            key=key,
            tool_name=tool_name,
            args_hash=args_hash,
            result=result,
            ttl=ttl or self._default_ttl,
        )
        with self._lock:
            self._records[key] = entry
        return key

    def invalidate(self, tool_name: str, args: dict) -> bool:
        """Remove a specific idempotency record (allow re-execution)."""
        args_hash = self._hash_args(args)
        key = self._make_key(tool_name, args_hash)
        with self._lock:
            return self._records.pop(key, None) is not None

    def clear(self, tool_name: str | None = None) -> int:
        """Clear all records, or only for a specific tool."""
        with self._lock:
            if tool_name is None:
                count = len(self._records)
                self._records.clear()
                return count
            keys = [k for k, v in self._records.items() if v.tool_name == tool_name]
            for k in keys:
                del self._records[k]
            return len(keys)

    def _cleanup(self, now: float) -> None:
        expired = [
            k for k, v in self._records.items()
            if now - v.timestamp > v.ttl
        ]
        for k in expired:
            del self._records[k]

    def stats(self) -> dict:
        with self._lock:
            self._cleanup(time.time())
            return {
                "protected_tools": sorted(self._protected_tools),
                "active_records": len(self._records),
                "duplicates_blocked": self._duplicates_blocked,
                "default_ttl": self._default_ttl,
            }
