# Changelog

All notable changes to WarderBox (formerly OpShield) are documented here.

## [0.3.1] - 2026-10-16

### Added — FinOps & Agent Cost Optimization
- **Smart Model Routing** (`routing.py`): Auto-routes tasks to cheapest capable LLM model, complexity classification (LOW/MEDIUM/HIGH), tool overrides, 60-90% cost savings
- **Cost Anomaly Detection** (`anomaly.py`): Z-score based cost spike detection, infinite loop detection, rate spike monitoring, burn rate alerts, per-tool tracking, callbacks
- **FinOps Dashboard**: 4-tab real-time web UI (Overview, FinOps, Routing, Alerts) with cost charts, model distribution, alert severity
- **100 integration tests**: Comprehensive tests exercising all 36 modules simultaneously
- Total test count: **255 tests**

## [0.3.0] - 2026-10-15

### Changed — Rename
- **Project renamed from OpShield to WarderBox** to avoid trademark conflict with GE Digital's OpShield
- All imports: `from warderbox import WarderBox` (was `from opshield import OpShield`)
- CLI command: `warderbox` (was `opshield`)
- PyPI package: `pip install warderbox`

## [0.2.0] - 2026-10-08

### Added — Phase 7: Enterprise Safety
- **Circuit Breaker** (`circuitbreaker.py`): CLOSED/OPEN/HALF_OPEN states, configurable failure threshold, reset timeout, success threshold for recovery, on_open/on_close callbacks
- **Approval Workflows** (`approval.py`): Human-in-the-loop with configurable timeout, auto-deny, callback-based approve/deny, risk-based approval, escalation chains
- **Agent Capabilities** (`capabilities.py`): Per-agent allowlist/denylist, argument constraints (args_deny/args_require), max cost per tool, max calls per hour, time-based schedules
- **Compliance Reports** (`compliance.py`): Structured audit reports from SQLite logs, anomaly detection (high block/error rate, CRITICAL attempts), risk breakdown, JSON/HTML export

### Added — Phase 8: Observability & Resilience
- **Distributed Tracing** (`tracing.py`): OpenTelemetry-compatible spans with trace/span IDs, nested spans via context manager, JSON and OTLP export, trace grouping
- **Chaos Engineering** (`chaos.py`): Fault injection (ERROR, LATENCY, TIMEOUT, CORRUPT_OUTPUT), probability control, conditional triggers, wildcard rules, max injection limits
- **Cost Forecasting** (`forecast.py`): Burn rate analysis (per minute/hour), budget exhaustion prediction, trend detection (increasing/decreasing/stable), cost-by-tool breakdown
- **Agent Scoring** (`scoring.py`): Safety/reliability/efficiency/risk dimensions (0-100), A-F grading, configurable weights, multi-agent pool ranking via PoolScorer

### Added — Phase 9: Polish & Market Readiness
- Full README rewrite covering all 32+ modules
- Landing page (`site/index.html`) with feature showcase and market data
- Comprehensive end-to-end demo (`examples/demo_full.py`)
- This CHANGELOG

### Changed
- `shield.py`: Integrated circuit breaker, capabilities, chaos, and tracing into execution pipeline
- `__init__.py`: Added exports for all new modules (ApprovalManager, CapabilityManager, CircuitBreaker, ChaosEngine, ComplianceReporter, CostForecaster, AgentScorer, PoolScorer, Tracer, FaultType, CircuitState)

## [0.1.0] - 2026-10-08

### Added — Phase 1: Core
- `WarderBox` main class with tool decorator
- Risk classification engine (LOW/MEDIUM/HIGH/CRITICAL)
- Budget tracking with per-action cost
- State snapshots and rollback
- Test/simulation mode

### Added — Phase 2: Infrastructure
- Dict-based configuration system
- SQLite-backed action logging
- OpenAI Agents SDK integration
- LangChain integration
- CLI tool (stats, logs, export, validate, dashboard)
- pip install support via pyproject.toml

### Added — Phase 3: Rate Limiting & Events
- Sliding-window rate limiter (global RPM/RPH, per-tool limits)
- Webhook/event notification system (HTTP + callbacks)
- Anthropic Claude SDK integration
- AsyncOpShield with async_tool decorator

### Added — Phase 4: Policy & Dashboard
- Policy-as-code (JSON/YAML files)
- Retry with exponential backoff and conditional retry
- CrewAI integration
- Web dashboard (dark theme, auto-refresh, stats cards)

### Added — Phase 5: Multi-Agent & Metrics
- AgentPool for multi-agent management with isolated budgets
- Microsoft AutoGen integration
- Prometheus-compatible metrics export (OpenMetrics text format)

### Added — Phase 6: Privacy & Debug
- DataMasker with 10 built-in PII/secret patterns
- Custom masking patterns support
- ActionReplayer for debugging/audit from SQLite logs
- Dry-run and single-action replay
