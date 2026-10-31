"""Local, network-free tests for the observe-only Langfuse report utility."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from urllib.error import HTTPError

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPOSITORY_ROOT / ".github" / "scripts" / "langfuse_quality_gate.py"
SPEC = importlib.util.spec_from_file_location("langfuse_quality_gate", SCRIPT_PATH)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_metric_query_uses_approved_aggregate_measures_only():
    query = gate.metric_query("2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "produccion")
    assert query["view"] == "observations"
    assert query["metrics"] == [
        {"measure": "count", "aggregation": "count"},
        {"measure": "latency", "aggregation": "p95"},
        {"measure": "totalTokens", "aggregation": "sum"},
        {"measure": "totalCost", "aggregation": "sum"},
    ]
    assert query["dimensions"] == []
    assert query["filters"][0]["column"] == "environment"


def test_summary_preserves_only_available_aggregate_values():
    summary = gate.build_summary(
        [{"count_count": 12, "p95_latency": 941, "sum_totalTokens": 2900}],
        [{"count_count": 2}],
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
        "produccion",
    )
    assert summary["metrics"] == {
        "observations": 12,
        "error_observations": 2,
        "p95_latency_ms": 941,
        "total_tokens": 2900,
        "total_cost_usd": None,
    }
    assert "Missing traces are not inferred" in summary["notes"][1]


def test_client_sends_basic_auth_but_does_not_expose_it(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["authorization"] = request.get_header("Authorization")
        captured["timeout"] = timeout
        return FakeResponse({"data": [{"count_count": 1}]})

    monkeypatch.setattr(gate, "urlopen", fake_urlopen)
    client = gate.LangfuseClient("https://us.cloud.langfuse.com", "public-test", "secret-test")
    rows = client.metrics({"view": "observations"})
    assert rows == [{"count_count": 1}]
    assert "/api/public/v2/metrics?query=" in captured["url"]
    assert captured["authorization"].startswith("Basic ")
    assert "secret-test" not in captured["authorization"]


def test_client_rejects_unexpected_response_shape(monkeypatch):
    monkeypatch.setattr(gate, "urlopen", lambda *_args, **_kwargs: FakeResponse({"data": {}}))
    client = gate.LangfuseClient("https://us.cloud.langfuse.com", "public", "secret")
    with pytest.raises(gate.LangfuseError, match="unexpected Metrics API response shape"):
        client.metrics({"view": "observations"})


def test_client_reports_http_error_without_response_body(monkeypatch):
    def fail(*_args, **_kwargs):
        raise HTTPError("https://example.test", 401, "Unauthorized", {}, None)

    monkeypatch.setattr(gate, "urlopen", fail)
    client = gate.LangfuseClient("https://us.cloud.langfuse.com", "public", "secret")
    with pytest.raises(gate.LangfuseError) as error:
        client.metrics({"view": "observations"})
    assert str(error.value) == "Langfuse Metrics API returned HTTP 401."


def test_missing_credentials_create_sanitized_error_report(monkeypatch, tmp_path):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    output = tmp_path / "summary.json"
    exit_code = gate.main(["--observe-only", "--output", str(output)])
    report = json.loads(output.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert report["status"] == "query_error"
    assert "No Langfuse data" in report["notes"][0]
    assert "LANGFUSE_SECRET_KEY" in report["message"]


def test_error_summary_can_be_written_to_github_summary(tmp_path):
    output = tmp_path / "report.json"
    github_summary = tmp_path / "summary.md"
    gate.write_summary(
        {"status": "query_error", "mode": "observe-only", "message": "HTTP 401", "notes": []},
        output,
        github_summary,
    )
    assert "HTTP 401" in github_summary.read_text(encoding="utf-8")
