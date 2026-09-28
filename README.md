# AP1-WEB-Console

> Implementation-oriented workspace for the AMRHZ / AP1 ecosystem.

**Project state: PARTIAL**

AP1-WEB-Console is the application-side repository of the AMRHZ ecosystem. It currently contains a React frontend, a FastAPI backend, MongoDB runtime integration, and read-oriented GitHub API integration.

Core principles:
- REAL STATE > UI SIMULATION
- EVIDENCE > CLAIM
- HUMAN INTENTION > AI ASSUMPTION

## Role in the ecosystem

```text
AMRHZ Architecture Core
        |
        | principles / architecture / protocols
        v
AP1-WEB-Console
        |
        | implementation
        v
Current AP1 application capabilities
```

AMRHZ Architecture Core is the supporting architecture and principles repository.
AP1-WEB-Console is the implementation-oriented application repository.
No runtime dependency between them is claimed unless implemented and evidenced in code.

## Current architecture
See docs/architecture.md.

High-level boundary:

```text
Human -> React Frontend -> FastAPI Backend
                         |             |
                         v             v
                      MongoDB      GitHub API
                                      |
                                      v
                               In-memory cache
```

## Currently implemented
- React frontend — VERIFIED
- FastAPI backend — VERIFIED
- GitHub read integration — VERIFIED
- MongoDB status storage — VERIFIED

Evidence paths:
- frontend/
- frontend/package.json
- backend/server.py
- backend/routes/github_routes.py
- backend/services/github_service.py

Current GitHub routes:
- GET /api/github/user
- GET /api/github/repositories
- GET /api/github/stats
- GET /api/github/health

## Not currently claimed as implemented
The following remain UNKNOWN or future until implementation and reproducible evidence exist:
- autonomous AI agent execution
- persistent AI memory
- automatic repository modification
- AP1 branch creation
- AP1 pull-request creation
- automatic merge
- AP1-managed CI orchestration
- runtime approval engine
- persistent audit-event system

A UI, README statement, or architecture concept does not change these states.

## API contracts
See contracts.md for the current API surface and the explicit boundary between implemented and planned contracts.

## Truth model
Project maturity:
CONCEPT -> PARTIAL -> VERIFIED -> LIVE
ARCHIVED is a terminal project state.

Evidence conditions:
UNKNOWN / CONFLICTING / FAILED / FALLBACK

A capability should be labelled VERIFIED only when implementation is accompanied by credible reproducible evidence.

## First AP1 capability boundary

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

Repository mutation is outside this first milestone.
Future write operations should follow:
INSPECT -> PROPOSE -> HUMAN APPROVAL -> EXECUTE -> VERIFY -> AUDIT

## Development rule
- inspect before modifying
- prefer the smallest useful implementation
- require reproducible evidence
- preserve explicit UNKNOWN states
- require human approval before consequential writes
- document actual runtime state

## Repository structure
```text
AP1-WEB-Console/
├── backend/
├── frontend/
├── tests/
├── contracts.md
└── docs/
    └── architecture.md
```