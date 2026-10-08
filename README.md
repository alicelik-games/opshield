<p align="center">
  <img src="https://raw.githubusercontent.com/alicelik-games/opshield/main/assets/logo.png" alt="OpShield Logo" width="180"/>
</p>

<h1 align="center">OpShield</h1>

<p align="center">
  <strong>The safety layer between AI agents and the real world.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/opshield/"><img src="https://img.shields.io/pypi/v/opshield?color=blue" alt="PyPI"/></a>
  <a href="https://github.com/alicelik-games/opshield/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-blue" alt="Python"/></a>
  <a href="https://pypi.org/project/opshield/"><img src="https://img.shields.io/pypi/dm/opshield?color=orange" alt="Downloads"/></a>
</p>

OpShield intercepts every tool call your AI agent makes and provides rollback, cost control, rate limiting, circuit breakers, approval workflows, distributed tracing, chaos testing, and compliance reporting — so agents can work autonomously without causing damage.

**Zero mandatory dependencies. One `pip install`. Works with every major agent framework.**

> **Market context:** With Guardrails AI acquired by Harvey (Sept 2026) and the AI agent safety market projected to grow from $610M to $6.85B at 41% CAGR, OpShield fills the gap as a comprehensive, framework-agnostic agent operations platform.

## Why OpShield?

| Problem | OpShield Solution |
|---------|---------------------|
| Agent runs `DROP TABLE` | Auto-blocked by risk classification |
| Agent overspends API budget | Budget limits + cost forecasting |
| Want to test without side effects | Test mode simulates everything |
| Agent made a mistake | One-call rollback via state snapshots |
| Agent spams an API | Rate limiting (RPM/RPH per tool) |
| Tool keeps failing | Circuit breaker auto-disables it |
| Need human approval | Approval workflows with timeout/escalation |
| Different agents, different rules | AgentPool with isolated budgets + capabilities |
| Sensitive data in logs | Automatic PII/secret masking |
| Need audit trail | SQLite logging + Prometheus + compliance reports |
| Test agent resilience | Chaos engineering with fault injection |
| Track every action | OpenTelemetry-compatible distributed tracing |
| Evaluate agent quality | Safety/performance scoring (A-F grades) |

## Install

```bash
pip install opshield
```

With framework integrations:

```bash
pip install opshield[openai]      # OpenAI Agents SDK
pip install opshield[anthropic]   # Anthropic Claude SDK
pip install opshield[langchain]   # LangChain
pip install opshield[crewai]      # CrewAI
pip install opshield[autogen]     # Microsoft AutoGen
pip install opshield[yaml]        # YAML policy files
pip install opshield[all]         # Everything
```

## Quick Start

```python
from opshield import OpShield

shield = OpShield(budget=5.00, auto_snapshot=True)

@shield.tool(cost=0.03)
def query_db(sql: str) -> str:
    return db.execute(sql)

# Normal execution
result = query_db(sql="SELECT * FROM users")
print(result.output)  # Works fine

# Destructive SQL is auto-blocked
result = query_db(sql="DROP TABLE users")
print(result.blocked)       # True
print(result.block_reason)  # "CRITICAL risk blocked: Destructive SQL detected"

# Undo the last action
shield.rollback()
```

## Core Features

### Policy-as-Code

Define rules in JSON or YAML files:

```json
{
  "budget": 25.00,
  "mode": "production",
  "global_rpm": 120,
  "tool_limits": {"send_email": {"rpm": 10, "rph": 100}},
  "rules": [
    {
      "name": "no_prod_access",
      "match": {"args_regex": "production|prod-db"},
      "risk": "critical",
      "reason": "Production database access blocked"
    }
  ],
  "webhooks": [
    {"url": "https://hooks.slack.com/...", "events": ["action_blocked"]}
  ]
}
```

```python
from opshield import load_policy
shield = load_policy("policy.json")
```

### Multi-Agent Support

```python
from opshield import AgentPool

pool = AgentPool(default_budget=5.00)
researcher = pool.register("researcher", budget=3.00)
coder = pool.register("coder", budget=10.00)
reviewer = pool.register("reviewer", budget=1.00, mode="test")

pool.stats()        # Aggregated view across all agents
pool.over_budget()  # ["researcher"] if over budget
```

### Rate Limiting

```python
from opshield import OpShield, ToolLimit

shield = OpShield(
    budget=10.00,
    global_rpm=60,                                    # 60 calls/min globally
    tool_limits={"send_email": ToolLimit(rpm=5)},     # 5 emails/min
)
```

### Retry with Backoff

```python
from opshield import RetryPolicy

policy = RetryPolicy(max_retries=3, backoff_base=1.0, jitter=0.5)

@shield.tool(cost=0.05, retry=policy)
def flaky_api(query: str) -> str:
    return requests.get(f"https://api.example.com?q={query}").text
```

### Sensitive Data Masking

```python
from opshield import DataMasker

masker = DataMasker()
shield.set_masker(masker)

# Emails, API keys, credit cards, SSNs, JWTs are auto-masked in logs
masker.add_pattern("project_id", r"PROJ-\d{6}", "PROJ-******")
```

## Enterprise Safety

### Circuit Breaker

Auto-disable tools that fail repeatedly (CLOSED → OPEN → HALF_OPEN):

```python
from opshield import CircuitBreaker

cb = CircuitBreaker(failure_threshold=5, reset_timeout=60.0)
shield.set_circuit_breaker(cb)
# After 5 consecutive failures, the tool is auto-disabled for 60s
# Then one probe call is allowed (HALF_OPEN) to test recovery
```

### Human-in-the-Loop Approval

```python
from opshield import ApprovalManager

approver = ApprovalManager(default_timeout=30.0)
approver.require_approval("send_email", timeout=60.0)
approver.require_approval_for_risk("HIGH")
shield.set_approval(approver)

# From another thread or webhook handler:
approver.approve(request_id, approver="admin@company.com")
```

### Agent Capabilities / Permissions

Fine-grained tool access control per agent:

```python
from opshield import CapabilityManager

caps = CapabilityManager()
caps.grant("researcher", allow=["search", "read_file"])
caps.grant("intern_bot", deny=["delete_record", "send_email"])
caps.add_constraint("coder", "run_sql", args_deny=["DROP", "TRUNCATE"])
shield.set_capabilities(caps)
```

### Compliance & Audit Reports

```python
from opshield import ComplianceReporter

reporter = ComplianceReporter(db_path="audit.db")
report = reporter.generate_report(start="2026-01-01", end="2026-12-31")
print(report.summary)          # Text summary with anomaly detection
reporter.export_json("audit.json")
html = reporter.to_html()      # Full HTML report
```

## Observability

### Distributed Tracing

OpenTelemetry-compatible span system:

```python
from opshield import Tracer

tracer = Tracer(service_name="my-agent")
shield.set_tracer(tracer)

# Every tool call automatically generates spans
# Nested spans for complex workflows:
with tracer.span("data_pipeline") as parent:
    with tracer.span("extract", parent=parent):
        extract_data()
    with tracer.span("transform", parent=parent):
        transform_data()

tracer.export_json("traces.json")  # JSON export
tracer.export_otlp()               # OTLP-compatible dict
```

### Cost Forecasting

```python
from opshield import CostForecaster

forecaster = CostForecaster(shield)
report = forecaster.forecast()
print(report.burn_rate_per_hour)       # $/hour
print(report.estimated_exhaustion)     # datetime
print(report.estimated_actions_remaining)
print(report.trend)                    # "increasing" / "stable" / "decreasing"
```

### Agent Scoring & Benchmarking

```python
from opshield import AgentScorer, PoolScorer

scorer = AgentScorer(shield, agent_name="my-bot")
report = scorer.score()
print(report.overall_score)    # 0-100
print(report.grade)            # A/B/C/D/F
print(report.safety_score)     # Safety dimension
print(report.reliability_score)

# Rank all agents in a pool
pool_scorer = PoolScorer(pool)
print(pool_scorer.summary())   # Ranked leaderboard
```

### Web Dashboard

```bash
opshield --db audit.db dashboard --port 8080
```

Real-time web UI showing actions, blocks, budget, and rate limits.

### Prometheus Metrics

```python
from opshield.metrics import start_metrics_server
start_metrics_server(shield, port=9090)
# Scrape http://localhost:9090/metrics
```

Exports: `opshield_actions_total`, `opshield_actions_blocked_total`, `opshield_budget_spent_dollars`, per-tool and per-agent labels.

### Webhook Notifications

```python
shield.notifier.add_webhook(
    url="https://hooks.slack.com/services/xxx",
    events={"action_blocked", "budget_exceeded"},
)

shield.notifier.on("action_blocked", lambda event, data: print(f"Alert: {data}"))
```

## Resilience Testing

### Chaos Engineering

Test agent resilience with controlled fault injection:

```python
from opshield import ChaosEngine, FaultType

chaos = ChaosEngine()
shield.set_chaos(chaos)

# Random failures (20% of calls)
chaos.add_fault("search_api", FaultType.ERROR, probability=0.2)

# Latency injection
chaos.add_fault("slow_api", FaultType.LATENCY, latency_ms=2000)

# Conditional faults
chaos.add_fault("db_query", FaultType.ERROR,
                condition=lambda args: "prod" in str(args))

# Wildcard — affect all tools
chaos.add_fault("*", FaultType.LATENCY, latency_ms=500, probability=0.1)
```

### Action Replay

```python
from opshield.replay import ActionReplayer

replayer = ActionReplayer(db_path="audit.db", executors={"run_sql": my_fn})
report = replayer.replay_all(shield)
print(f"Match rate: {report.success_rate:.0%}")
```

### Async Support

```python
from opshield import AsyncOpShield

shield = AsyncOpShield(budget=5.00)

@shield.async_tool(cost=0.05)
async def async_query(sql: str) -> str:
    return await db.execute(sql)
```

## Framework Integrations

| Framework | Module | Pattern |
|-----------|--------|---------|
| OpenAI Agents SDK | `integrations.openai_agents` | Middleware |
| Anthropic Claude | `integrations.anthropic_sdk` | Middleware |
| LangChain | `integrations.langchain` | Tool wrapper |
| CrewAI | `integrations.crewai` | Tool wrapper |
| Microsoft AutoGen | `integrations.autogen` | Function wrapper |

```python
# OpenAI
from opshield.integrations.openai_agents import OpenAIShieldMiddleware
middleware = OpenAIShieldMiddleware(shield=shield, executors={...})

# Anthropic
from opshield.integrations.anthropic_sdk import AnthropicShieldMiddleware
middleware = AnthropicShieldMiddleware(shield=shield, executors={...})

# LangChain
from opshield.integrations.langchain import shield_langchain_tools

# CrewAI
from opshield.integrations.crewai import shield_crewai_tools

# AutoGen
from opshield.integrations.autogen import shield_autogen_functions
```

## CLI

```bash
opshield stats                    # Action statistics
opshield logs                     # View action log
opshield logs --blocked           # Only blocked actions
opshield export audit.json        # Export to JSON
opshield validate policy.json     # Validate a policy file
opshield dashboard --port 8080    # Start web dashboard
```

## Risk Levels

| Level | Behavior | Examples |
|-------|----------|----------|
| LOW | Execute normally | SELECT queries, file reads |
| MEDIUM | Execute with logging | Outbound messages, moderate operations |
| HIGH | Ask user for approval | Bulk operations (>100 items) |
| CRITICAL | Auto-block | DROP TABLE, TRUNCATE, DELETE FROM |

## Architecture

```
Agent → OpShield → Tool
         ├── Capability Check (permissions)
         ├── Circuit Breaker (fail-fast)
         ├── Risk Classification (rules engine)
         ├── Approval Workflow (human-in-the-loop)
         ├── Budget Check + Forecast
         ├── Rate Limit Check
         ├── Snapshot (for rollback)
         ├── Chaos Injection (testing)
         ├── Execute (or simulate in test mode)
         ├── Retry (on failure, with backoff)
         ├── Data Masking (for logs)
         ├── Log to SQLite
         ├── Emit webhook/callback events
         ├── Record span (distributed tracing)
         ├── Agent Scoring
         └── Prometheus metrics
```

## Stats

- **32+ Python modules**, 107+ tests
- **Zero mandatory dependencies**
- **5 framework integrations**
- Works with Python 3.11+

## Author

**Ali Çelik** — [LinkedIn](https://linkedin.com/in/alicelik1980) · [Email](mailto:alicelik1980@gmail.com)

## License

MIT — see [LICENSE](LICENSE) for details.
