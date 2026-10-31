
#!/usr/bin/env python3
"""Read-only Langfuse observability report and informational Quality Gate."""

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
    """Sanitized error safe for CI logs."""


class ConfigurationError(LangfuseError):
    """Configuration error."""


class LangfuseClient:
    """Read-only client for Langfuse Metrics API v2."""

    def __init__(
        self,
        base_url: str,
        public_key: str,
        secret_key: str,
        timeout: int = 20,
    ):
        if not public_key or not secret_key:
            raise ConfigurationError(
                "Langfuse credentials are missing. "
                "Configure LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY."
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        credentials = f"{public_key}:{secret_key}".encode("utf-8")
        encoded = base64.b64encode(credentials).decode("ascii")
        self.authorization = f"Basic {encoded}"

    def metrics(
        self,
        query: Mapping[str, Any],
    ) -> list[Mapping[str, Any]]:

        encoded_query = urlencode({
            "query": json.dumps(query, separators=(",", ":"))
        })

        url = f"{self.base_url}{METRICS_PATH}?{encoded_query}"

        request = Request(
            url,
            headers={
                "Authorization": self.authorization,
                "Accept": "application/json",
            },
            method="GET",
        )

        for attempt in range(3):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                if not isinstance(payload, dict):
                    raise LangfuseError(
                        "Unexpected Langfuse response format."
                    )

                data = payload.get("data")

                if (
                    not isinstance(data, list)
                    or any(not isinstance(row, dict) for row in data)
                ):
                    raise LangfuseError(
                        "Langfuse returned an unexpected Metrics API response shape."
                    )

                return data

            except HTTPError as exc:
                if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                    retry_after = (
                        exc.headers.get("Retry-After")
                        if exc.headers else None
                    )

                    try:
                        delay = (
                            min(max(int(retry_after), 1), 10)
                            if retry_after else attempt + 1
                        )
                    except (ValueError, TypeError):
                        delay = attempt + 1

                    time.sleep(delay)
                    continue

                if exc.code == 400:
                    raise LangfuseError(
                        "Langfuse Metrics API returned HTTP 400. "
                        "Check the query schema, metric names, "
                        "aggregations and filters."
                    ) from None

                raise LangfuseError(
                    f"Langfuse Metrics API returned HTTP {exc.code}."
                ) from None

            except URLError as exc:
                if attempt < 2:
                    time.sleep(attempt + 1)
                    continue

                reason = (
                    type(exc.reason).__name__
                    if exc.reason else "network error"
                )

                raise LangfuseError(
                    f"Unable to reach Langfuse API ({reason})."
                ) from None

            except json.JSONDecodeError:
                raise LangfuseError(
                    "Langfuse returned invalid JSON."
                ) from None

        raise LangfuseError(
            "Unable to query Langfuse Metrics API."
        )


def iso_utc(value: str) -> str:
    """Validate and normalize an ISO-8601 timestamp."""

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        raise ConfigurationError(
            "Time values must be valid ISO-8601 timestamps."
        ) from None

    if parsed.tzinfo is None:
        raise ConfigurationError(
            "Time values must include a UTC offset or Z suffix."
        )

    return (
        parsed.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def metric_query(
    start: str,
    end: str,
    environment: str,
    *,
    errors_only: bool = False,
) -> dict[str, Any]:
    """Build a Langfuse Metrics API v2 query."""

    filters = []

    if environment:
        filters.append({
            "column": "environment",
            "operator": "=",
            "value": environment,
            "type": "string",
        })

    if errors_only:
        filters.append({
            "column": "level",
            "operator": "=",
            "value": "ERROR",
            "type": "string",
        })

    metrics = [
        {
            "measure": "count",
            "aggregation": "count",
        }
    ]

    if not errors_only:
        metrics.extend([
            {
                "measure": "latency",
                "aggregation": "p95",
            },
            {
                "measure": "totalUsage",
                "aggregation": "sum",
            },
            {
                "measure": "totalCost",
                "aggregation": "sum",
            },
        ])

    return {
        "view": "observations",
        "metrics": metrics,
        "dimensions": [],
        "filters": filters,
        "fromTimestamp": start,
        "toTimestamp": end,
        "config": {
            "row_limit": 1,
        },
    }


def value(
    row: Mapping[str, Any],
    name: str,
) -> int | float | None:
    """Read a numeric metric safely."""

    candidate = row.get(name)

    if candidate is None or isinstance(candidate, bool):
        return None

    if isinstance(candidate, (int, float)):
        return candidate

    if isinstance(candidate, str):
        try:
            return float(candidate)
        except ValueError:
            return None

    return None


def configured_threshold(
    name: str,
    default: float,
) -> float:
    """Read and validate a configurable numeric threshold."""

    raw = os.getenv(name)

    if raw is None or not raw.strip():
        return default

    try:
        result = float(raw)
    except ValueError:
        raise ConfigurationError(
            f"{name} must be a valid number."
        ) from None

    if result < 0:
        raise ConfigurationError(
            f"{name} must not be negative."
        )

    return result


def evaluate_quality_gate(
    metrics: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate LLMOps thresholds without blocking CI/CD."""

    thresholds = {
        "max_cost_usd": configured_threshold(
            "LLMOPS_MAX_COST_USD", 5.0
        ),
        "max_p95_latency_ms": configured_threshold(
            "LLMOPS_MAX_P95_LATENCY_MS", 3000.0
        ),
        "max_error_rate_percent": configured_threshold(
            "LLMOPS_MAX_ERROR_RATE_PERCENT", 5.0
        ),
    }

    observations = metrics.get("observations")
    errors = metrics.get("error_observations")
    latency = metrics.get("p95_latency_ms")
    cost = metrics.get("total_cost_usd")

    warnings = []
    checks = {}

    # Error rate
    if (
        observations is None
        or observations <= 0
        or errors is None
    ):
        warnings.append(
            "Error rate could not be evaluated with available observations."
        )
        checks["error_rate"] = {
            "status": "UNKNOWN",
            "value_percent": None,
            "threshold_percent": thresholds[
                "max_error_rate_percent"
            ],
        }
    else:
        error_rate = (errors / observations) * 100
        passed = error_rate <= thresholds[
            "max_error_rate_percent"
        ]

        checks["error_rate"] = {
            "status": "PASS" if passed else "WARNING",
            "value_percent": round(error_rate, 2),
            "threshold_percent": thresholds[
                "max_error_rate_percent"
            ],
        }

        if not passed:
            warnings.append(
                "Error rate exceeds the configured threshold."
            )

    # P95 latency
    if latency is None:
        warnings.append(
            "P95 latency metric is unavailable."
        )
        checks["latency"] = {
            "status": "UNKNOWN",
            "value_ms": None,
            "threshold_ms": thresholds[
                "max_p95_latency_ms"
            ],
        }
    else:
        passed = latency <= thresholds["max_p95_latency_ms"]

        checks["latency"] = {
            "status": "PASS" if passed else "WARNING",
            "value_ms": latency,
            "threshold_ms": thresholds[
                "max_p95_latency_ms"
            ],
        }

        if not passed:
            warnings.append(
                "P95 latency exceeds the configured threshold."
            )

    # AI cost
    if cost is None:
        warnings.append(
            "Cost metric is unavailable; cost threshold was not evaluated."
        )
        checks["cost"] = {
            "status": "UNKNOWN",
            "value_usd": None,
            "threshold_usd": thresholds["max_cost_usd"],
        }
    else:
        passed = cost <= thresholds["max_cost_usd"]

        checks["cost"] = {
            "status": "PASS" if passed else "WARNING",
            "value_usd": cost,
            "threshold_usd": thresholds["max_cost_usd"],
        }

        if not passed:
            warnings.append(
                "AI cost exceeds the configured threshold."
            )

    return {
        "status": "PASS" if not warnings else "WARNING",
        "blocking": False,
        "thresholds": thresholds,
        "checks": checks,
        "warnings": warnings,
    }


def build_summary(
    overall_rows: list[Mapping[str, Any]],
    error_rows: list[Mapping[str, Any]],
    start: str,
    end: str,
    environment: str,
) -> dict[str, Any]:

    overall = overall_rows[0] if overall_rows else {}
    errors = error_rows[0] if error_rows else {}

    metrics = {
        "observations": value(overall, "count_count"),
        "error_observations": value(errors, "count_count"),
        "p95_latency_ms": value(overall, "p95_latency"),
        "total_tokens": value(overall, "sum_totalUsage"),
        "total_cost_usd": value(overall, "sum_totalCost"),
    }

    return {
        "status": "observed",
        "mode": "observe-only",
        "api": "Langfuse Metrics API v2",
        "period": {
            "from": start,
            "to": end,
            "environment": environment or "all",
        },
        "metrics": metrics,
        "quality_gate": evaluate_quality_gate(metrics),
        "notes": [
            "Quality Gate is informational and does not block CI/CD.",
            "Missing traces are not inferred.",
            "Prompts, outputs, trace IDs, users and sessions are excluded.",
        ],
    }


def write_summary(
    summary: Mapping[str, Any],
    output: Path,
    github_summary: Path | None = None,
) -> None:

    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if not github_summary:
        return

    if summary["status"] == "observed":
        metrics = summary["metrics"]
        gate = summary["quality_gate"]

        warning_lines = "\n".join(
            f"- WARNING: {warning}"
            for warning in gate["warnings"]
        ) or "- No threshold violations detected."

        check_lines = "\n".join(
            f"- {name}: `{check['status']}`"
            for name, check in gate["checks"].items()
        )

        content = (
            "## LLMOps Observability — Quality Gate\n\n"
            f"- Estado de observación: `{summary['status']}`\n"
            f"- Quality Gate: **{gate['status']}**\n"
            f"- Desde: `{summary['period']['from']}`\n"
            f"- Hasta: `{summary['period']['to']}`\n"
            f"- Entorno: `{summary['period']['environment']}`\n\n"
            "### Métricas\n"
            f"- Observaciones: `{metrics['observations']}`\n"
            f"- Errores: `{metrics['error_observations']}`\n"
            f"- Latencia p95 (ms): `{metrics['p95_latency_ms']}`\n"
            f"- Tokens: `{metrics['total_tokens']}`\n"
            f"- Costo USD: `{metrics['total_cost_usd']}`\n\n"
            "### Evaluación de umbrales\n"
            f"{check_lines}\n\n"
            "### Advertencias\n"
            f"{warning_lines}\n\n"
            "El Quality Gate es informativo y no bloquea CI/CD.\n"
        )
    else:
        content = (
            "## LLMOps Observability — observe-only\n\n"
            f"- Estado: `{summary['status']}`\n"
            f"- Error: `{summary['message']}`\n"
        )

    github_summary.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    github_summary.write_text(
        content,
        encoding="utf-8",
    )


def parse_args(
    argv: list[str] | None = None,
) -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description="Create a sanitized Langfuse observability report."
    )

    parser.add_argument(
        "--base-url",
        default=os.getenv(
            "LANGFUSE_BASE_URL",
            DEFAULT_BASE_URL,
        ),
    )

    parser.add_argument(
        "--environment",
        default=os.getenv(
            "LANGFUSE_ENVIRONMENT",
            "produccion",
        ),
    )

    parser.add_argument("--from", dest="start")
    parser.add_argument("--to", dest="end")

    parser.add_argument(
        "--window-hours",
        type=int,
        default=24,
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--github-summary",
        type=Path,
    )

    parser.add_argument(
        "--observe-only",
        action="store_true",
        required=True,
    )

    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, Any]:

    if args.window_hours <= 0:
        raise ConfigurationError(
            "--window-hours must be greater than zero."
        )

    end = (
        iso_utc(args.end)
        if args.end
        else datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )

    start = (
        iso_utc(args.start)
        if args.start
        else (
            datetime.fromisoformat(
                end.replace("Z", "+00:00")
            ) - timedelta(hours=args.window_hours)
        )
        .isoformat()
        .replace("+00:00", "Z")
    )

    if start >= end:
        raise ConfigurationError(
            "The start of the period must precede its end."
        )

    client = LangfuseClient(
        args.base_url,
        os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        os.getenv("LANGFUSE_SECRET_KEY", ""),
    )

    overall = client.metrics(
        metric_query(
            start,
            end,
            args.environment,
        )
    )

    errors = client.metrics(
        metric_query(
            start,
            end,
            args.environment,
            errors_only=True,
        )
    )

    return build_summary(
        overall,
        errors,
        start,
        end,
        args.environment,
    )


def main(argv: list[str] | None = None) -> int:

    args = parse_args(argv)

    try:
        summary = run(args)

    except LangfuseError as exc:
        summary = {
            "status": "query_error",
            "mode": "observe-only",
            "message": str(exc),
            "notes": [
                "No Langfuse data was included in this report."
            ],
        }

        write_summary(
            summary,
            args.output,
            args.github_summary,
        )

        print(
            f"LLMOps observation unavailable: {exc}",
            file=sys.stderr,
        )

        return 2

    write_summary(
        summary,
        args.output,
        args.github_summary,
    )

    print(
        "LLMOps observation completed; sanitized summary created."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
