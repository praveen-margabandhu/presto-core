"""
PRESTO-CORE: NFR Parser
Reads non-functional requirements from YAML and validates completeness.
"""

import yaml
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


VALID_LOAD_PATTERNS = {"linear", "spike", "soak", "stress"}


@dataclass
class SLOSpec:
    p99_response_ms: int
    error_rate_pct: float
    p50_response_ms: Optional[int] = None
    p95_response_ms: Optional[int] = None
    throughput_rps: Optional[int] = None


@dataclass
class LoadSpec:
    peak_users: int
    ramp_duration_seconds: int = 120
    steady_state_seconds: int = 300
    ramp_down_seconds: int = 60
    load_pattern: str = "linear"


@dataclass
class NFRSpec:
    service: str
    endpoint: str
    slo: SLOSpec
    load: LoadSpec
    environment: str = "staging"
    tags: dict = field(default_factory=dict)

    @property
    def test_name(self) -> str:
        safe_service = self.service.replace("-", "_").replace("/", "_")
        safe_endpoint = self.endpoint.replace("/", "_").replace(".", "_").strip("_")
        return f"{safe_service}{safe_endpoint}"


class NFRValidationError(Exception):
    pass


class NFRParser:
    """
    Parses NFR YAML files into NFRSpec objects.
    Validates required fields and acceptable values before generation.
    """

    def parse_file(self, path: str) -> NFRSpec:
        nfr_path = Path(path)
        if not nfr_path.exists():
            raise FileNotFoundError(f"NFR file not found: {path}")
        if nfr_path.suffix not in {".yaml", ".yml"}:
            raise NFRValidationError(f"NFR file must be YAML: {path}")
        with open(nfr_path) as f:
            raw = yaml.safe_load(f)
        return self._parse_dict(raw, source=path)

    def parse_dict(self, raw: dict) -> NFRSpec:
        return self._parse_dict(raw, source="inline")

    def _parse_dict(self, raw: dict, source: str) -> NFRSpec:
        self._require_fields(raw, ["service", "endpoint", "slo", "load"], source)
        slo = self._parse_slo(raw["slo"], source)
        load = self._parse_load(raw["load"], source)
        return NFRSpec(
            service=str(raw["service"]),
            endpoint=str(raw["endpoint"]),
            slo=slo,
            load=load,
            environment=str(raw.get("environment", "staging")),
            tags=raw.get("tags", {}),
        )

    def _parse_slo(self, raw: dict, source: str) -> SLOSpec:
        self._require_fields(raw, ["p99_response_ms", "error_rate_pct"], source)
        p99 = int(raw["p99_response_ms"])
        error_rate = float(raw["error_rate_pct"])
        if p99 <= 0:
            raise NFRValidationError(f"[{source}] p99_response_ms must be > 0, got {p99}")
        if not 0 < error_rate < 100:
            raise NFRValidationError(
                f"[{source}] error_rate_pct must be between 0 and 100, got {error_rate}"
            )
        return SLOSpec(
            p99_response_ms=p99,
            error_rate_pct=error_rate,
            p50_response_ms=int(raw["p50_response_ms"]) if "p50_response_ms" in raw else None,
            p95_response_ms=int(raw["p95_response_ms"]) if "p95_response_ms" in raw else None,
            throughput_rps=int(raw["throughput_rps"]) if "throughput_rps" in raw else None,
        )

    def _parse_load(self, raw: dict, source: str) -> LoadSpec:
        self._require_fields(raw, ["peak_users"], source)
        peak_users = int(raw["peak_users"])
        if peak_users <= 0:
            raise NFRValidationError(
                f"[{source}] peak_users must be > 0, got {peak_users}"
            )
        pattern = str(raw.get("load_pattern", "linear"))
        if pattern not in VALID_LOAD_PATTERNS:
            raise NFRValidationError(
                f"[{source}] load_pattern must be one of {VALID_LOAD_PATTERNS}, got '{pattern}'"
            )
        return LoadSpec(
            peak_users=peak_users,
            ramp_duration_seconds=int(raw.get("ramp_duration_seconds", 120)),
            steady_state_seconds=int(raw.get("steady_state_seconds", 300)),
            ramp_down_seconds=int(raw.get("ramp_down_seconds", 60)),
            load_pattern=pattern,
        )

    @staticmethod
    def _require_fields(d: dict, fields: list, source: str) -> None:
        missing = [f for f in fields if f not in d]
        if missing:
            raise NFRValidationError(
                f"[{source}] Missing required fields: {missing}"
            )
