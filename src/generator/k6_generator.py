"""
PRESTO-CORE: K6 Test Generator
Converts validated NFRSpec objects into ready-to-run K6 load test scripts.
"""

from datetime import date


class K6Generator:
    """
    Generates K6 JavaScript load test scripts from NFR specifications.
    Thresholds come directly from the NFR — the test is the requirement.
    """

    def generate(self, nfr) -> str:
        stages = self._build_stages(nfr.load)
        thresholds = self._build_thresholds(nfr)
        checks = self._build_checks(nfr)
        header = self._build_header(nfr)

        return f"""{header}
import http from 'k6/http';
import {{ check, sleep }} from 'k6';
import {{ Trend, Rate, Counter }} from 'k6/metrics';

const responseTime = new Trend('response_time_ms');
const errorRate = new Rate('error_rate');
const requestCount = new Counter('total_requests');

export const options = {{
  stages: [
{stages}
  ],
  thresholds: {{
{thresholds}
  }},
  tags: {{
    service: '{nfr.service}',
    environment: '{nfr.environment}',
    presto_nfr: 'true',
  }},
}};

export default function () {{
  const res = http.get(
    `${{__ENV.BASE_URL}}{nfr.endpoint}`,
    {{
      headers: {{
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }},
      tags: {{ name: '{nfr.endpoint}' }},
    }}
  );

  const success = check(res, {{
{checks}
  }});

  errorRate.add(!success);
  responseTime.add(res.timings.duration);
  requestCount.add(1);

  sleep(0.1);
}}

export function handleSummary(data) {{
  const p99 = data.metrics.http_req_duration.values['p(99)'];
  const errRate = (data.metrics.http_req_failed.values.rate * 100).toFixed(3);
  const passed = data.metrics.http_req_failed.values.rate < {nfr.slo.error_rate_pct / 100};

  return {{
    'presto-results-summary.json': JSON.stringify(data, null, 2),
    stdout: `
PRESTO-CORE Results
===================
Service:     {nfr.service}
Endpoint:    {nfr.endpoint}
Environment: {nfr.environment}
Pattern:     {nfr.load.load_pattern}
Peak users:  {nfr.load.peak_users}

SLO Results
-----------
p99 response: ${{p99?.toFixed(0) ?? 'N/A'}}ms  (target: <{nfr.slo.p99_response_ms}ms)
Error rate:   ${{errRate}}%  (target: <{nfr.slo.error_rate_pct}%)

Result: ${{passed ? 'PASS' : 'FAIL'}}
`,
  }};
}}
"""

    def _build_stages(self, load) -> str:
        p = load.load_pattern

        if p == "linear":
            return (
                f"    {{ duration: '{load.ramp_duration_seconds}s', target: {load.peak_users} }},\n"
                f"    {{ duration: '{load.steady_state_seconds}s', target: {load.peak_users} }},\n"
                f"    {{ duration: '{load.ramp_down_seconds}s', target: 0 }},"
            )

        if p == "spike":
            hold = max(load.steady_state_seconds, 60)
            return (
                f"    {{ duration: '10s', target: {load.peak_users} }},\n"
                f"    {{ duration: '{hold}s', target: {load.peak_users} }},\n"
                f"    {{ duration: '10s', target: 0 }},"
            )

        if p == "soak":
            soak_users = int(load.peak_users * 0.6)
            soak_duration = max(load.steady_state_seconds, 3600)
            return (
                f"    {{ duration: '{load.ramp_duration_seconds}s', target: {soak_users} }},\n"
                f"    {{ duration: '{soak_duration}s', target: {soak_users} }},\n"
                f"    {{ duration: '{load.ramp_down_seconds}s', target: 0 }},"
            )

        if p == "stress":
            stage = load.peak_users // 4
            dur = load.ramp_duration_seconds // 4
            return (
                f"    {{ duration: '{dur}s', target: {stage} }},\n"
                f"    {{ duration: '{dur}s', target: {stage * 2} }},\n"
                f"    {{ duration: '{dur}s', target: {stage * 3} }},\n"
                f"    {{ duration: '{dur}s', target: {load.peak_users} }},\n"
                f"    {{ duration: '{load.steady_state_seconds}s', target: {load.peak_users} }},\n"
                f"    {{ duration: '{load.ramp_down_seconds}s', target: 0 }},"
            )

        return (
            f"    {{ duration: '{load.ramp_duration_seconds}s', target: {load.peak_users} }},\n"
            f"    {{ duration: '{load.steady_state_seconds}s', target: {load.peak_users} }},\n"
            f"    {{ duration: '{load.ramp_down_seconds}s', target: 0 }},"
        )

    def _build_thresholds(self, nfr) -> str:
        error_fraction = nfr.slo.error_rate_pct / 100
        lines = [
            f"    'http_req_duration': ['p(99)<{nfr.slo.p99_response_ms}'],",
            f"    'http_req_failed': ['rate<{error_fraction}'],",
        ]
        if nfr.slo.p95_response_ms:
            lines.append(f"    'http_req_duration': ['p(95)<{nfr.slo.p95_response_ms}'],")
        if nfr.slo.throughput_rps:
            lines.append(f"    'http_reqs': ['rate>{nfr.slo.throughput_rps}'],")
        return "\n".join(lines)

    def _build_checks(self, nfr) -> str:
        return (
            f"    'status is 2xx': (r) => r.status >= 200 && r.status < 300,\n"
            f"    'p99 under {nfr.slo.p99_response_ms}ms': (r) => r.timings.duration < {nfr.slo.p99_response_ms},"
        )

    def _build_header(self, nfr) -> str:
        return (
            f"// Generated by PRESTO-CORE\n"
            f"// Service: {nfr.service} | Endpoint: {nfr.endpoint}\n"
            f"// Pattern: {nfr.load.load_pattern} | Peak users: {nfr.load.peak_users}\n"
            f"// SLO: p99 < {nfr.slo.p99_response_ms}ms | error rate < {nfr.slo.error_rate_pct}%\n"
            f"// Generated: {date.today().isoformat()}\n"
            f"// Edit the NFR YAML to change thresholds — do not edit this file directly\n"
        )
