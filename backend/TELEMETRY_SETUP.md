# AP1 Telemetry Setup

## What is recorded

The opt-in homepage telemetry currently records only a UTC calendar day and an aggregate page-view counter in MongoDB collection `site_analytics_daily`.

It does not store application-level IP addresses, names, email addresses, user-agent strings, referrers, account IDs, or browser fingerprints. The public endpoint returns only all-time and rolling seven-day totals. The admin endpoint returns daily aggregate totals.

Hosting, reverse-proxy, CDN, and platform access logs are separate systems and may have their own retention settings. Review those settings independently; this application-level design cannot control external infrastructure logs.

## Enable owner/admin analytics

Set `AP1_ANALYTICS_ADMIN_TOKEN` in the backend deployment's secret/environment settings to a randomly generated secret with at least 32 characters.

- Never put this value in a `REACT_APP_*` variable or frontend build configuration.
- Never commit the value to Git or paste it into source files.
- The admin endpoint remains disabled with HTTP 503 until a sufficiently long token is configured.
- Send the token only as an HTTPS `Authorization: Bearer` header.
- Rotate it through the hosting provider's secret manager if it is exposed.

The homepage admin form keeps the entered token in component memory only; it is not written to localStorage or sessionStorage.

## Endpoints

- `POST /api/telemetry/event` — accepts the fixed `page_view` event from visitors who opt in.
- `GET /api/telemetry/public` — returns coarse public aggregate totals.
- `GET /api/telemetry/admin?days=30` — returns daily aggregate totals; requires the admin bearer token. The `days` parameter is limited to 7–90.

## Limitations and operational checks

- Counts are approximate and can be inflated by automated requests; no visitor identifier is retained for per-visitor deduplication.
- The frontend records at most one page view per browser tab session after consent.
- MongoDB availability is required. If storage is unavailable, telemetry fails closed and the portfolio remains usable.
- This release does not claim to provide project build percentages or checkpoint scores. Those require a separate verified project-evidence source and approval workflow.
- Before production use, validate the site's privacy notice and applicable legal requirements, and verify HTTPS, CORS origin restrictions, database access controls, backups, and hosting log retention.
