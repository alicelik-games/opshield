"""OpShield — rollback, cost control, and testing for AI agents."""

from opshield.shield import OpShield
from opshield.action import Action, ActionResult, RiskLevel
from opshield.approval import ApprovalManager
from opshield.async_shield import AsyncOpShield
from opshield.capabilities import CapabilityManager
from opshield.chaos import ChaosEngine, FaultType
from opshield.circuitbreaker import CircuitBreaker, CircuitState
from opshield.compliance import ComplianceReporter
from opshield.forecast import CostForecaster
from opshield.logger import ActionLogger
from opshield.masking import DataMasker
from opshield.multiagent import AgentPool
from opshield.policy import load_policy, validate_policy
from opshield.ratelimit import RateLimiter, ToolLimit
from opshield.replay import ActionReplayer
from opshield.retry import RetryPolicy
from opshield.scoring import AgentScorer, PoolScorer
from opshield.tracing import Tracer
from opshield.webhooks import EventNotifier
from opshield.config import rules_from_config

__all__ = [
    "OpShield",
    "AsyncOpShield",
    "AgentPool",
    "AgentScorer",
    "ApprovalManager",
    "Action",
    "ActionResult",
    "CapabilityManager",
    "ChaosEngine",
    "CircuitBreaker",
    "CircuitState",
    "ComplianceReporter",
    "CostForecaster",
    "FaultType",
    "PoolScorer",
    "RiskLevel",
    "ActionLogger",
    "ActionReplayer",
    "DataMasker",
    "RateLimiter",
    "ToolLimit",
    "RetryPolicy",
    "Tracer",
    "EventNotifier",
    "load_policy",
    "validate_policy",
    "rules_from_config",
]
__version__ = "0.2.1"
