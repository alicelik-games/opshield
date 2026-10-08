"""Budget tracker for agent cost control."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class CostEntry:
    """A single cost record."""

    action_id: str
    tool_name: str
    cost: float
    timestamp: float


class BudgetTracker:
    """Tracks cumulative cost and enforces a budget limit."""

    def __init__(self, budget: float | None = None, warn_at: float = 0.8) -> None:
        self._budget = budget
        self._warn_at = warn_at
        self._entries: list[CostEntry] = []

    @property
    def budget(self) -> float | None:
        return self._budget

    @property
    def spent(self) -> float:
        return sum(e.cost for e in self._entries)

    @property
    def remaining(self) -> float | None:
        if self._budget is None:
            return None
        return max(0.0, self._budget - self.spent)

    @property
    def over_budget(self) -> bool:
        if self._budget is None:
            return False
        return self.spent >= self._budget

    @property
    def warning(self) -> bool:
        if self._budget is None:
            return False
        return self.spent >= self._budget * self._warn_at

    def would_exceed(self, cost: float) -> bool:
        if self._budget is None:
            return False
        return self.spent + cost > self._budget

    def record(self, action_id: str, tool_name: str, cost: float) -> CostEntry:
        entry = CostEntry(
            action_id=action_id,
            tool_name=tool_name,
            cost=cost,
            timestamp=time.time(),
        )
        self._entries.append(entry)
        return entry

    def summary(self) -> dict:
        return {
            "budget": self._budget,
            "spent": round(self.spent, 4),
            "remaining": round(self.remaining, 4) if self.remaining is not None else None,
            "entries": len(self._entries),
            "over_budget": self.over_budget,
            "warning": self.warning,
        }
