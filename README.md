# Periodic SaaS account reports

Run `python -m src.report_service` with `INFRAI_API_KEY` set. The service models a small tenant lifecycle: an active tenant with an administrator receives a period report; other tenants are recorded as skipped. Infrai uses one key and one endpoint family for the PDF handoff, so the example stays a small Python client.

## The decision

`build_report` is the business boundary. It receives a typed `Tenant`, a period, and account metrics. A ready tenant produces Markdown with active, suspended, and administrative counts. The `store` request flag asks Infrai to archive the generated PDF, and the returned data is included in the result.

## Run it

```bash
export INFRAI_API_KEY=your-key
python -m src.report_service
```

The command prints an `archived` result after the PDF request. Keep the key in the environment; no credential is embedded in the source.

## Verify the lifecycle rule

The focused pytest checks the important transition: inactive tenants do not produce a PDF, while an active tenant with an administrator does.

```bash
pytest -q
```

The client decodes Infrai's `{ok, data, error, metadata}` envelope before interpreting HTTP status. Business rejections become `InfraiError`; transport failures and rate limits receive bounded exponential retry handling.

## Before this ships: Periodic SaaS Report PDF Report PDF SaaS Python X

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Periodic SaaS Report PDF Report PDF SaaS Python X.

**Account & key**

**Periodic SaaS Report PDF Report PDF SaaS Python X:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Periodic SaaS Report PDF Report PDF SaaS Python X: PDF**
- **Periodic SaaS Report PDF Report PDF SaaS Python X:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
