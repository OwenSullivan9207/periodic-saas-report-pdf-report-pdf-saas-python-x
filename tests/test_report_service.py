import pytest

from src.report_service import Tenant, build_report


class StubClient:
    def __init__(self):
        self.markdown = None

    def generate_pdf(self, markdown):
        self.markdown = markdown
        return {"job_id": "job-123"}


def test_inactive_tenant_is_not_archived():
    client = StubClient()
    result = build_report(Tenant("t1", "Northwind", False, "ops@example.com"), "2026-Q3", {}, client)
    assert result["status"] == "skipped"
    assert client.markdown is None


def test_ready_tenant_report_contains_operational_metrics():
    client = StubClient()
    result = build_report(Tenant("t1", "Northwind", True, "ops@example.com"), "2026-Q3", {"active_accounts": 8}, client)
    assert result["status"] == "archived"
    assert "Active accounts: 8" in client.markdown
    assert result["pdf"]["job_id"] == "job-123"
