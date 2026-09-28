# AP1-WEB-Console — Current Architecture

## Document status
- Project state: PARTIAL
- Scope: current repository structure and observable runtime boundaries
- Source of truth: repository code and reproducible evidence

## Current system boundary

```text
Human
  |
  v
React Frontend
  |
  v
FastAPI Backend
  |--------------------|
  v                    v
MongoDB             GitHub API
(runtime data)      (repository/profile data)
                         |
                         v
                 In-memory cache
```

## Components

### Frontend — VERIFIED
Evidence: frontend/ and frontend/package.json.

### Backend/API — VERIFIED
Evidence: backend/server.py. FastAPI, MongoDB configuration, API routing, and GitHub route inclusion are implemented.

### GitHub integration — VERIFIED
Evidence: backend/routes/github_routes.py and backend/services/github_service.py.
Implemented read-oriented routes:
- GET /api/github/user
- GET /api/github/repositories
- GET /api/github/stats
- GET /api/github/health
The service uses the GitHub API and an in-memory five-minute cache.

### MongoDB runtime data — VERIFIED
Evidence: backend/server.py.
Implemented:
- POST /api/status
- GET /api/status

### AI model/agent layer — UNKNOWN
AI functionality described by documentation is not treated as runtime proof.

### Persistent AI memory layer — UNKNOWN
No AP1 runtime component is treated as a verified persistent AI memory system.

### GitHub write/execution layer — UNKNOWN
Branch creation, pull requests, merge, repository mutation, and autonomous execution are not established as AP1 runtime capabilities.

### Approval/audit layer — UNKNOWN
A human approval boundary is an architectural requirement for future write operations, but its runtime implementation is not established.

## Next architecture boundary

```text
User
  |
  v
Select repository
  |
  v
AP1 reads real repository
  |
  v
Structured analysis
  |
  v
Evidence + UNKNOWN
  |
  v
Human review
```

Repository mutation is outside this first boundary.

Future write operations should follow:

```text
INSPECT -> PROPOSE -> HUMAN APPROVAL -> EXECUTE -> VERIFY -> AUDIT
```

## Evidence rule
A capability is VERIFIED only when implementation is accompanied by credible reproducible evidence such as a passing test, working integration, workflow result, or other directly inspectable runtime evidence.

README statements and UI appearance alone do not establish runtime capability.

## Relationship to AMRHZ Architecture Core
amrhz-architecture-core is treated as the architecture and principles reference repository.
AP1-WEB-Console is the implementation-oriented application repository.
This document does not claim a runtime dependency between them unless such a dependency is implemented and evidenced in code.