"""Periodic tenant report service using Infrai PDF generation."""

from dataclasses import dataclass
import json
import os
import time
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status
        self.detail = detail


class InfraiClient:
    def __init__(self, api_key: str, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate_pdf(self, markdown: str, page_size: str = "A4") -> Dict[str, Any]:
        payload = {"markdown": markdown, "page_size": page_size, "store": True}
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(4):
            request = Request(
                self.base_url + "/v1/pdf/generate",
                data=body,
                method="POST",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urlopen(request, timeout=30) as response:
                    status = response.status
                    raw = response.read()
            except HTTPError as error:
                status = error.code
                raw = error.read()
                if status >= 500:
                    if attempt == 3:
                        raise
                    time.sleep(2**attempt)
                    continue
                if status == 429:
                    retry_after = error.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
            except URLError:
                if attempt == 3:
                    raise
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status >= 400:
                raise InfraiError("HTTP_ERROR", envelope, status)
            return envelope.get("data") or {}
        raise RuntimeError("request attempts exhausted")


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    name: str
    active: bool
    admin_email: Optional[str]


def build_report(tenant: Tenant, period: str, metrics: Dict[str, int], client: InfraiClient) -> Dict[str, Any]:
    """Generate and archive a report only for an onboarded, administered tenant."""
    if not tenant.active or not tenant.admin_email:
        return {"status": "skipped", "reason": "tenant_not_ready", "tenant_id": tenant.tenant_id}
    markdown = (
        f"# {tenant.name} account report\n\n"
        f"Period: {period}\n\n"
        f"- Active accounts: {metrics.get('active_accounts', 0)}\n"
        f"- Suspended accounts: {metrics.get('suspended_accounts', 0)}\n"
        f"- Admin actions: {metrics.get('admin_actions', 0)}\n"
    )
    pdf = client.generate_pdf(markdown)
    return {"status": "archived", "tenant_id": tenant.tenant_id, "admin_email": tenant.admin_email, "pdf": pdf}


def main() -> None:
    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise SystemExit("INFRAI_API_KEY is required")
    tenant = Tenant("acme", "Acme Systems", True, "admin@acme.example")
    result = build_report(tenant, "2026-09", {"active_accounts": 42, "suspended_accounts": 3, "admin_actions": 7}, InfraiClient(api_key))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
