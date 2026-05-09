"""
PRESTO-CORE CLI
Commands:
  presto generate --nfr <path> --output <path>
  presto generate --nfr-dir <dir> --output-dir <dir>
  presto validate --results <json> --nfr <path>
"""

import argparse
import json
import sys
from pathlib import Path

from parser.nfr_parser import NFRParser, NFRValidationError
from generator.k6_generator import K6Generator


def cmd_generate(args):
    parser = NFRParser()
    generator = K6Generator()

    if args.nfr:
        nfr = parser.parse_file(args.nfr)
        script = generator.generate(nfr)
        output_path = args.output or f"{nfr.test_name}_load_test.js"
        Path(output_path).write_text(script)
        print(f"Generated: {output_path}")
        print(f"  Service:   {nfr.service}")
        print(f"  Endpoint:  {nfr.endpoint}")
        print(f"  Pattern:   {nfr.load.load_pattern}")
        print(f"  Peak VUs:  {nfr.load.peak_users}")
        print(f"  p99 SLO:   <{nfr.slo.p99_response_ms}ms")
        print(f"  Error SLO: <{nfr.slo.error_rate_pct}%")

    elif args.nfr_dir:
        nfr_dir = Path(args.nfr_dir)
        output_dir = Path(args.output_dir or "perf-tests")
        output_dir.mkdir(parents=True, exist_ok=True)

        nfr_files = list(nfr_dir.glob("*.yaml")) + list(nfr_dir.glob("*.yml"))
        if not nfr_files:
            print(f"No NFR YAML files found in {nfr_dir}", file=sys.stderr)
            sys.exit(1)

        for nfr_file in nfr_files:
            nfr = parser.parse_file(str(nfr_file))
            script = generator.generate(nfr)
            output_path = output_dir / f"{nfr.test_name}_load_test.js"
            output_path.write_text(script)
            print(f"Generated: {output_path} ({nfr.load.load_pattern}, {nfr.load.peak_users} VUs)")

        print(f"\n{len(nfr_files)} test(s) generated in {output_dir}/")


def cmd_validate(args):
    results_path = Path(args.results)
    if not results_path.exists():
        print(f"Results file not found: {args.results}", file=sys.stderr)
        sys.exit(1)

    with open(results_path) as f:
        results = json.load(f)

    parser = NFRParser()
    nfr = parser.parse_file(args.nfr)
    metrics = results.get("metrics", {})
    failures = []

    p99 = metrics.get("http_req_duration", {}).get("values", {}).get("p(99)")
    if p99 and p99 > nfr.slo.p99_response_ms:
        failures.append(
            f"p99 BREACHED: {p99:.0f}ms > {nfr.slo.p99_response_ms}ms"
        )

    error_rate = metrics.get("http_req_failed", {}).get("values", {}).get("rate", 0)
    error_pct = error_rate * 100
    if error_pct > nfr.slo.error_rate_pct:
        failures.append(
            f"Error rate BREACHED: {error_pct:.3f}% > {nfr.slo.error_rate_pct}%"
        )

    if failures:
        print("SLO VIOLATIONS DETECTED")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)
    else:
        print(f"All SLOs passed for {nfr.service}{nfr.endpoint}")


def main():
    parser = argparse.ArgumentParser(
        prog="presto",
        description="PRESTO-CORE: NFR-driven performance test generation",
    )
    subparsers = parser.add_subparsers(dest="command")

    gen = subparsers.add_parser("generate", help="Generate K6 tests from NFR YAML")
    gen.add_argument("--nfr", help="Path to single NFR YAML file")
    gen.add_argument("--nfr-dir", help="Directory of NFR YAML files")
    gen.add_argument("--output", help="Output path for single test")
    gen.add_argument("--output-dir", help="Output directory for multiple tests")

    val = subparsers.add_parser("validate", help="Validate K6 results against NFR SLOs")
    val.add_argument("--results", required=True, help="Path to K6 results JSON")
    val.add_argument("--nfr", required=True, help="Path to NFR YAML file")

    args = parser.parse_args()

    if args.command == "generate":
        if not args.nfr and not args.nfr_dir:
            print("Error: provide --nfr or --nfr-dir", file=sys.stderr)
            sys.exit(1)
        try:
            cmd_generate(args)
        except (NFRValidationError, FileNotFoundError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "validate":
        cmd_validate(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
