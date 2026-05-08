# PRESTO-CORE

**NFR-driven performance test generation for mission-critical systems**

---

Most teams write performance tests after the fact. Requirements get defined, code gets written, and somewhere near the end of the sprint someone runs a load test and hopes for the best. PRESTO-CORE flips that sequence.

You define your non-functional requirements — response time, throughput, error rate — and PRESTO-CORE generates the load test. The test is the requirement. If it fails, the requirement failed. No interpretation required.

This is the core tooling behind the PRESTO framework (Performance Resilience Engineering for Systems with Threshold Operations), built from 13 years of performance engineering across financial services, telecommunications, healthcare, energy, and military financial infrastructure.

---

## The problem it solves

Performance requirements live in tickets. Load tests live in scripts. The connection between them is manual, inconsistent, and usually wrong by the time anyone checks.

A ticket says: *"The payment API must handle 100,000 concurrent users at under 500ms p99 with error rate below 0.5%."*

Someone translates that into a load test script three weeks later. The script tests 10,000 users because that's what fits on the test server. The threshold is 800ms because that's what was passing last sprint. The requirement and the test are no longer the same thing.

PRESTO-CORE removes that gap. Parse the NFR, generate the test, run it in the pipeline. The test is always current because it comes directly from the requirement.

---

## How it works
NFR Definition (YAML)
↓
PRESTO-CORE Parser
— reads thresholds, load profile, SLOs
— validates NFR completeness
— selects appropriate load pattern
↓
Test Generator
— produces K6 script with correct VUs, ramp pattern, thresholds
— embeds pass/fail assertions from NFR
— generates test summary template
↓
K6 Script (ready to run or embed in CI/CD pipeline)
---

## Quick start

```bash
pip install presto-core
```

Define your NFR:

```yaml
# nfrs/payment-api.yaml
service: payment-api
endpoint: /v1/payments/process
slo:
  p99_response_ms: 500
  error_rate_pct: 0.5
load:
  peak_users: 100000
  ramp_duration_seconds: 120
  steady_state_seconds: 300
  load_pattern: spike
environment: staging
```

Generate the test:

```bash
presto generate --nfr nfrs/payment-api.yaml --output tests/payment-api-load.js
```

Run it:

```bash
k6 run tests/payment-api-load.js
```

The test passes or fails based on the thresholds in the NFR — not based on what someone decided was good enough last sprint.

---

## NFR specification

```yaml
service: string
endpoint: string
slo:
  p99_response_ms: int     # required
  error_rate_pct: float    # required
  p95_response_ms: int     # optional
  p50_response_ms: int     # optional
  throughput_rps: int      # optional
load:
  peak_users: int          # required
  ramp_duration_seconds: int
  steady_state_seconds: int
  ramp_down_seconds: int
  load_pattern: string     # linear | spike | soak | stress
environment: string
tags:
  team: string
  priority: string
```

---

## Load patterns

**linear** — Standard ramp to peak, hold, ramp down. Baseline validation and regression testing.

**spike** — Instantaneous jump to peak load. Built for correlated demand events: financial paydays, product launches, benefit disbursements — scenarios where load doesn't arrive gradually but hits simultaneously.

**soak** — Extended steady-state at moderate load. Surfaces memory leaks, connection pool exhaustion, and gradual degradation that only appears after hours of continuous operation.

**stress** — Progressive load increase past peak until failure. Finds the breaking point and validates graceful degradation behavior.

---

## CI/CD integration

Azure DevOps:

```yaml
- script: presto generate --nfr-dir ./nfrs --output-dir ./perf-tests
  displayName: Generate performance tests from NFRs

- script: k6 run ./perf-tests/*.js -e BASE_URL=$(STAGING_URL)
  displayName: Run performance tests

- script: presto validate --results results.json --nfr ./nfrs/service.yaml
  displayName: Validate SLO thresholds
```

GitHub Actions:

```yaml
- name: Generate and run performance tests
  run: |
    presto generate --nfr-dir ./nfrs --output-dir ./perf-tests
    k6 run ./perf-tests/*.js -e BASE_URL=${{ secrets.STAGING_URL }}
```

---

## Examples

Three example NFRs are included covering common mission-critical scenarios:

- `examples/payment-api.yaml` — High-volume payment processing with spike pattern
- `examples/fraud-detection-api.yaml` — Real-time fraud evaluation with strict latency SLO
- `examples/auth-api.yaml` — Authentication baseline for migration parity validation

---

## The PRESTO framework

PRESTO-CORE implements the **Requirement-Driven Resilience Testing** pillar of the PRESTO framework.

PRESTO (Performance Resilience Engineering for Systems with Threshold Operations) is a six-pillar methodology for performance engineering in systems where failure consequences extend beyond business impact:

- **P** — Predictive Demand Modeling
- **R** — Requirement-Driven Resilience Testing ← this tool
- **E** — End-to-End Observability Across Four Layers
- **S** — SLO/SLA Governance as Deployment Gates
- **T** — Threat-Aware Capacity Planning
- **O** — Operational Continuity Engineering

Full framework documentation: [docs/presto-framework.md](docs/presto-framework.md)

---

## Roadmap

- [x] NFR YAML parser
- [x] K6 test generator
- [x] Linear and spike load patterns
- [x] CI/CD pipeline templates (Azure DevOps, GitHub Actions)
- [ ] Soak and stress load patterns
- [ ] JMeter output generator
- [ ] NeoLoad output generator
- [ ] Results validator with SLO drift detection
- [ ] VS Code extension for NFR authoring

---

## License

MIT

---

*Built on 13 years of performance engineering across financial services, telecommunications, healthcare, energy, and military financial infrastructure.*
