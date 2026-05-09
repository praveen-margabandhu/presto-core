# PRESTO Framework

## Performance Resilience Engineering for Systems with Threshold Operations

Every engineering system has a threshold — a point above which failure stops being a business problem and becomes something more serious. Below that threshold, downtime means lost revenue and unhappy users. Above it, failure means people can't access their money during a financial emergency, medical systems go dark during a patient crisis, or energy infrastructure destabilizes during a weather event.

Most performance engineering frameworks were built for systems operating below that threshold. Netflix pioneered chaos engineering for a streaming service. Google developed SRE practices for consumer search. The field's foundational tools and thinking come from environments where failure, while costly, is ultimately recoverable.

PRESTO was built for the other category. Systems where the threshold has been crossed. Where recovery time is measured not in revenue but in consequences.

---

## The six pillars

### P — Predictive Demand Modeling

Standard load testing answers one question: can the system handle today's traffic? Predictive demand modeling asks a different one: what traffic is coming, and is the infrastructure ready before it arrives?

The distinction matters in systems with predictable, correlated demand events. Financial institutions process payroll for millions of accounts on the same days each month. Healthcare systems see coordinated appointment rushes at predictable times. Energy grids face correlated demand spikes during weather events. These are not random load patterns. They are forecastable.

Supply chain management solved this problem decades ago. Demand forecasting, inventory positioning, and constraint-based capacity planning exist precisely because reactive stock management fails when demand is predictable and correlated. PRESTO applies the same logic to infrastructure: treat capacity as inventory, model demand curves from historical patterns, and position headroom before peak arrives.

This pillar borrows directly from operations management theory — specifically the Theory of Constraints and demand forecasting methods common in supply chain graduate education. The insight that software infrastructure capacity problems and inventory management problems share the same mathematical structure is not obvious from within performance engineering. It becomes clear when you look at both fields.

### R — Requirement-Driven Resilience Testing

Performance requirements and performance tests drift apart. It happens on every team. Requirements are defined in tickets at the start of a project. Tests are written by a performance engineer three sprints later based on what they remember the requirements were. By the time the system reaches production, the test is validating something subtly different from the requirement.

Requirement-Driven Resilience Testing closes that gap structurally. Non-functional requirements are defined as machine-readable specifications. Tests are generated directly from those specifications. The test is the requirement. If the requirement changes, the test regenerates. Drift is architecturally impossible.

PRESTO-CORE is the reference implementation of this pillar.

### E — End-to-End Observability Across Four Layers

Standard application performance monitoring answers: is the infrastructure healthy? CPU, memory, network, disk — the infrastructure layer. This is necessary but not sufficient for mission-critical systems.

PRESTO defines observability across four layers simultaneously:

**Infrastructure layer** — the standard APM view. System resource consumption. Necessary baseline, not sufficient signal.

**Pipeline layer** — per-stage latency breakdown across every service boundary. Distributed tracing instrumented at the transaction level, not the system level. This is where you discover that 400ms of your 500ms p99 budget is being consumed by a single internal service call that nobody has profiled.

**Application layer** — business logic performance. Not just "is the service responding" but "is the fraud model completing inference within the latency budget" or "is the authentication policy evaluation adding acceptable overhead."

**Business outcome layer** — the layer most APM frameworks omit entirely. Real-time tracking of business-level metrics alongside technical ones: approval rates, transaction success rates, conversion rates. A fraud detection system can show completely healthy infrastructure metrics while silently degrading in model accuracy. The business outcome layer catches this. The infrastructure layer cannot.

### S — SLO/SLA Governance as Deployment Gates

Performance is typically verified after deployment. A release goes out, someone runs a load test, results are reviewed, issues are filed. The feedback loop is slow and the fix is expensive.

SLO/SLA Governance treats defined service level objectives as deployment gates. A deployment that breaches a defined SLO fails the pipeline before reaching production. This is the performance engineering equivalent of test-driven development. Write the requirement. Define the threshold. Gate deployment on it.

The practical barrier has always been the gap between where SLOs are defined (tickets, wikis, documentation) and where tests run (pipelines, test frameworks). PRESTO-CORE bridges that gap. The SLO lives in a machine-readable NFR specification. The deployment gate reads from that specification.

### T — Threat-Aware Capacity Planning

Capacity planning models normal demand. Threat-aware capacity planning models adversarial demand.

The intersection of cybersecurity and performance engineering is underexplored. A distributed denial-of-service attack is, from a capacity planning perspective, an extreme demand spike. An authentication storm — thousands of simultaneous login attempts from compromised credentials — is a load pattern with specific performance characteristics that differ from legitimate peak traffic. A fraud detection system under active exploitation generates different load patterns than the same system processing normal transaction volume.

Mission-critical systems need performance engineering that accounts for these scenarios. Not because attackers are certain to strike, but because the capacity required to handle adversarial demand gracefully differs from the capacity required to handle legitimate peak demand, and that difference needs to be understood and engineered for in advance.

### O — Operational Continuity Engineering

Chaos engineering was pioneered by Netflix for consumer streaming infrastructure. The original tools were built for an environment where some level of failure was acceptable, graceful degradation was sufficient, and the blast radius of an experiment was naturally bounded.

Mission-critical systems have different requirements. A chaos experiment on a financial transaction processing system cannot simply cause errors and observe how the system recovers. The experiment must have a defined hypothesis, a measurable success criterion, a pre-validated rollback procedure, and a controlled blast radius that prevents real member impact.

Operational Continuity Engineering is chaos engineering with the additional constraints required for zero-tolerance systems. The principles are the same — inject failure, observe behavior, build confidence. The execution discipline is different.

---

## Why these six, in this order

The pillars are ordered by information flow: you cannot gate deployments on requirements (S) before you have machine-readable requirements (R). You cannot model threat-aware capacity (T) before you have baseline observability (E) to measure adversarial load patterns. Operational continuity (O) validation requires that you have defined what continuity means (S) before you can validate it.

The P pillar sits first because the fundamental question — what load is coming — precedes everything else. You cannot generate requirement-driven tests (R), define meaningful SLOs (S), or size chaos experiments (O) without a model of expected demand.

---

## Scope

PRESTO applies to systems where:

- Failure consequences extend beyond business impact
- Demand patterns include predictable, correlated events
- Downtime has human, operational, or safety consequences
- Recovery time is constrained by regulatory, contractual, or mission requirements

This includes financial services, healthcare, energy infrastructure, telecommunications, government services, and defense systems.

---

## PRESTO-CORE

The reference implementation of Pillar R — Requirement-Driven Resilience Testing.

[PRESTO-CORE on GitHub](https://github.com/praveen-margabandhu/presto-core)

---

*PRESTO was developed from 14+ years of performance engineering across energy, healthcare, financial services, telecommunications, education, and military financial infrastructure.*
