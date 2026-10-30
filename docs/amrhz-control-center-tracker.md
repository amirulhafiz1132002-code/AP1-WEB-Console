# AMRHZ Control Center — Additive Tracker Module

## Scope
This is an isolated, additive browser-local tracking module for AP1-WEB-Console. It is served as a standalone static page at:

`/amrhz-control-center.html`

## Preservation boundary
- Does not modify the existing React application entry point, routes, components, backend, API contracts, dependencies, or build scripts.
- Does not change the existing home page.
- Does not perform GitHub writes, run tests, or deploy anything.
- Added on a dedicated feature branch, not directly on the default branch.

## Current capabilities
- Multiple project records and task records.
- Task states: Not tested, In progress, Blocked, Verified.
- Evidence reference field per task.
- A task contributes to verified completion only when its status is Verified and its evidence field is non-empty.
- Project/status/search filters.
- Browser localStorage persistence.
- JSON export/import backup.

## Important limitations
- This is manual tracking, not automatic repository or CI evidence collection.
- Data is local to the browser profile until exported; it is not shared across devices or users.
- Evidence references are user-entered and are not independently validated by this page.
- Initial AP1 audit tasks start Not tested. No prior audit result is promoted to Verified by assumption.

## Data key
Browser storage key: `amrhz-control-center:v1`.

## Verification still required
- Open the static page through the configured frontend host.
- Exercise task status/evidence gating, filters, project/task creation, and JSON round-trip.
- Run the frontend production build in the repository's normal environment.
