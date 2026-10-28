#!/usr/bin/env python3
"""Read-only Langfuse observability report for EcoPredict & NLQ.

This utility deliberately queries only Langfuse Metrics API v2 aggregates.  It
does not request observation I/O, prompts, outputs, users, sessions, or trace
identifiers.  ``--observe-only`` means observed metric values never cause a
quality-policy failure; connectivity and configuration errors still return a
non-zero status so they can be fixed rather than silently hidden.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://us.cloud.langfuse.com"
METRICS_PATH = "/api/public/v2/metrics"


class LangfuseError(RuntimeError):
    """A sanitized error safe to report in CI logs and artifacts."""


class ConfigurationError(LangfuseError):
    """Required local configuration was not provided."""


class LangfuseClient:
    """Small stdlib-only client for read-only, aggregate Langfuse metrics."""

    def __init__(self, base_url: str, public_key: str, secret_key: str, timeout: int = 20):
        if not public_key or not secret_key:
            raise ConfigurationError(
                "Langfuse credentials are not configured. Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        credential = f"{public_key}:{secret_key}".encode("utf-8")
        self.authorization = "Basic " + base64.b64encode(credential).decode("ascii")

    def metrics(self, query: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        """Return metric rows without logging requests, headers, or response bodies."""
        url = f"{self.base_url}{METRICS_PATH}?{urlencode({'query': json.dumps(query, separators=(',', ':'))})}"
        request = Request(
            url,
            headers={"Authorization": self.authorization, "Accept": "application/json"},
            method="GET",
        )

        # A short, bounded retry is useful for transient 429/5xx conditions and
        # prevents an observation workflow from running indefinitely.
        for attempt in range(3):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                data = payload.get("data") if isinstance(payload, dict) else None
                if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
                    raise LangfuseError("Langfuse returned an unexpected Metrics API response shape.")
                return data
            except HTTPError as exc:
                if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    try:
                        delay = min(max(int(retry_after), 1), 10) if retry_after else attempt + 1
                    except ValueError:
                        delay = attempt + 1
                    time.sleep(delay)
                    continue
                raise LangfuseError(f"Langfuse Metrics API returned HTTP {exc.code}.") from None
            except URLError as exc:
                if attempt < 2:
                    time.sleep(attempt + 1)
                    continue
                reason = type(exc.reason).__name__ if exc.reason else "network error"
                raise LangfuseError(f"Unable to reach Langfuse Metrics API ({reason}).") from None
            except json.JSONDecodeError:
                raise LangfuseError("Langfuse returned invalid JSON from the Metrics API.") from None

        raise LangfuseError("Unable to query Langfuse Metrics API.")


def iso_utc(value: str) -> str:
    """Validate and normalize an ISO-8601 instant to UTC."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ConfigurationError("Time values must be valid ISO-8601 timestamps.") from exc
    if parsed.tzinfo is None:
        raise ConfigurationError("Time values must include a UTC offset or Z suffix.")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def metric_query(start: str, end: str, environment: str, *, errors_only: bool = False) -> dict[str, Any]:
    filters: list[dict[str, Any]] = [
        {"column": "environment", "operator": "=", "value": environment, "type": "string"}
    ]
    if errors_only:
        filters.append({"column": "level", "operator": "=", "value": "ERROR", "type": "string"})

    metrics: list[dict[str, str]] = [{"measure": "count", "aggregation": "count"}]
    if not errors_only:
        metrics.extend(
            [
                {"measure": "latency", "aggregation": "p95"},
                {"measure": "totalUsage", "aggregation": "sum"},
                {"measure": "totalCost", "aggregation": "sum"},
            ]
        )

    return {
        "view": "observations",
        "metrics": metrics,
        "dimensions": [],
        "filters": filters,
        "fromTimestamp": start,
        "toTimestamp": end,
        "config": {"row_limit": 1},
    }


def value(row: Mapping[str, Any], name: str) -> int | float | None:
    """Use an API value only if it is numeric; never manufacture a value."""
    candidate = row.get(name)
    if isinstance(candidate, bool) or not isinstance(candidate, (int, float)):
        return None
    return candidate


def build_summary(
    overall_rows: list[Mapping[str, Any]],
    error_rows: list[Mapping[str, Any]],
    start: str,
    end: str,
    environment: str,
) -> dict[str, Any]:
    overall = overall_rows[0] if overall_rows else {}
    errors = error_rows[0] if error_rows else {}
    return {
        "status": "observed",
        "mode": "observe-only",
        "api": "Langfuse Metrics API v2",
        "period": {"from": start, "to": end, "environment": environment},
        "metrics": {
            "observations": value(overall, "count_count"),
            "error_observations": value(errors, "count_count"),
            "p95_latency_ms": value(overall, "p95_latency"),
            "total_tokens": value(overall, "sum_totalUsage"),
            "total_cost_usd": value(overall, "sum_totalCost"),
        },
        "notes": [
            "No policy thresholds are evaluated in observe-only mode.",
            "Missing traces are not inferred because no trusted expected-execution source is configured.",
            "The report intentionally excludes prompts, outputs, trace IDs, users, sessions, and API credentials.",
        ],
    }


def write_summary(summary: Mapping[str, Any], output: Path, github_summary: Path | None = None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if github_summary:
        if summary["status"] == "observed":
            metrics = summary["metrics"]
            content = (
                "## LLMOps observability — observe-only\n\n"
                f"- Estado: `{summary['status']}`\n"
                f"- Periodo: `{summary['period']['from']}` a `{summary['period']['to']}`\n"
                f"- Entorno: `{summary['period']['environment']}`\n"
                f"- Observaciones: `{metrics['observations']}`\n"
                f"- Observaciones con error: `{metrics['error_observations']}`\n"
                f"- Latencia p95 (ms): `{metrics['p95_latency_ms']}`\n"
                f"- Tokens totales: `{metrics['total_tokens']}`\n"
                f"- Costo total USD: `{metrics['total_cost_usd']}`\n\n"
                "No se evaluaron umbrales y no se incluyeron datos de prompts, outputs ni identificadores de trazas.\n"
            )
        else:
            content = (
                "## LLMOps observability — observe-only\n\n"
                f"- Estado: `{summary['status']}`\n"
                f"- Consulta: `{summary['message']}`\n\n"
                "No se expusieron datos de Langfuse en este resumen.\n"
            )
        github_summary.write_text(content, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a sanitized observe-only Langfuse report.")
    parser.add_argument("--base-url", default=os.getenv("LANGFUSE_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--environment", default=os.getenv("LANGFUSE_ENVIRONMENT", "produccion"))
    parser.add_argument("--from", dest="start")
    parser.add_argument("--to", dest="end")
    parser.add_argument("--window-hours", type=int, default=24)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--github-summary", type=Path)
    parser.add_argument("--observe-only", action="store_true", required=True)
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.window_hours <= 0:
        raise ConfigurationError("--window-hours must be greater than zero.")
    end = iso_utc(args.end) if args.end else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    start = (
        iso_utc(args.start)
        if args.start
        else (datetime.fromisoformat(end.replace("Z", "+00:00")) - timedelta(hours=args.window_hours))
        .isoformat()
        .replace("+00:00", "Z")
    )
    if start >= end:
        raise ConfigurationError("The start of the period must precede its end.")

    client = LangfuseClient(
        args.base_url,
        os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        os.getenv("LANGFUSE_SECRET_KEY", ""),
    )
    overall = client.metrics(metric_query(start, end, args.environment))
    errors = client.metrics(metric_query(start, end, args.environment, errors_only=True))
    return build_summary(overall, errors, start, end, args.environment)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = run(args)
    except LangfuseError as exc:
        # Never include exception bodies, endpoint query strings, or credentials.
        summary = {
            "status": "query_error",
            "mode": "observe-only",
            "message": str(exc),
            "notes": ["No Langfuse data was included in this report."],
        }
        write_summary(summary, args.output, args.github_summary)
        print(f"LLMOps observation unavailable: {exc}", file=sys.stderr)
        return 2

    write_summary(summary, args.output, args.github_summary)
    print("LLMOps observation completed; sanitized summary created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
