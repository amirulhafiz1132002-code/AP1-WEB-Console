# API Contracts — Current State

## Document status
- Contract state: PARTIAL
- Scope: APIs currently implemented in AP1-WEB-Console
- Implemented contracts and planned contracts remain separate

## Implemented GitHub API

### GET /api/github/user
Purpose: read the configured GitHub user's public profile data.
Evidence: backend/routes/github_routes.py and backend/services/github_service.py.

### GET /api/github/repositories
Purpose: read repositories and enrich them with service-side metadata.
Query parameter: category (optional).
Current classifier categories include core, tools, research, backend, resources, and other.
Response wrapper: success, data, count.
Evidence: backend/routes/github_routes.py and backend/services/github_service.py.

### GET /api/github/stats
Purpose: calculate aggregate statistics from GitHub user and repository data.
Response wrapper: success, data.
Evidence: backend/routes/github_routes.py and backend/services/github_service.py.

### GET /api/github/health
Purpose: check whether the GitHub service can reach the GitHub API.
Returns success/message for accessible or inaccessible GitHub API state.
Evidence: backend/routes/github_routes.py.

## Implemented status API

### POST /api/status
Creates a status-check record in MongoDB.
Evidence: backend/server.py.

### GET /api/status
Reads status-check records from MongoDB.
Evidence: backend/server.py.

## Runtime caching
GitHub responses use an in-memory cache implemented inside backend/services/github_service.py.
Current cache duration: five minutes.
The previously documented backend/utils/cache.py is not established in the current repository state.

## Authentication and authorization
Current AP1 user authentication/authorization: UNKNOWN / NOT ESTABLISHED.
The optional GITHUB_TOKEN is an outbound GitHub API credential, not proof of AP1 user authorization.

Before repository mutation exists, the contract should define: authenticated actor, permitted repository, requested action, explicit approval, execution result, and audit/evidence record.

## Error contract
Current GitHub routes generally return HTTP 500 for service exceptions and expose a failure message.
This records current implementation behaviour; it is not a claim that this is the final production error standard.

## Project maturity states
- CONCEPT
- PARTIAL
- VERIFIED
- LIVE
- ARCHIVED

Evidence conditions are separate:
- UNKNOWN
- CONFLICTING
- FAILED
- FALLBACK

## Planned contracts — NOT IMPLEMENTED
- repository tree analysis workflow
- structured repository-analysis output contract
- human approval API
- branch creation API
- pull-request creation API
- CI status orchestration API
- autonomous agent execution
- persistent AI memory API
- audit-event persistence

## Evidence rule
A contract is not VERIFIED because it appears in this document. Verification requires the corresponding implementation plus credible reproducible evidence.