# AMRHZ Truth Protocol

**Status:** PROPOSED / DOCUMENTED
**Principle:** REAL STATE > UI SIMULATION
**Scope:** AMRHZ / AP1 evidence, AI-generated analysis, Studio outputs, development checkpoints

## 1. Purpose

The AMRHZ Truth Protocol defines how claims about the ecosystem must be classified before they are presented as facts or used to drive implementation.

The protocol exists to prevent UI state, README claims, prompts, mock data, generated research, and assumptions from being treated as proof of runtime capability.

## 2. Core Rules

1. **REAL STATE > UI SIMULATION** — runtime/source evidence takes precedence over presentation state.
2. **EVIDENCE > CLAIM** — a documented claim is not implementation proof by itself.
3. **HUMAN INTENTION > AI ASSUMPTION** — AI may propose; the project owner decides scope and acceptance.
4. **VERIFICATION > BLIND TRUST** — every important capability claim should have a traceable source, test, commit, or runtime observation.

## 3. Required Evidence Status

| Status | Meaning |
|---|---|
| **VERIFIED** | Direct evidence exists in source, commit, test result, or observed runtime behavior. |
| **PROPOSED** | Intentionally designed or requested, but implementation is not yet verified. |
| **UNKNOWN** | Evidence is currently insufficient to establish the claim. |
| **CONFLICTING** | Two sources disagree, or documentation claims completion while current source does not establish it. |
| **FAILED** | A verification attempt or workflow produced a confirmed failure. |
| **FALLBACK** | A mock, fixture, reference dataset, or other non-production path is being used instead of the real integration. |
|

## 4. Source Reliability

When sources disagree, use this evidence order unless a stronger direct observation exists:

1. Current executable source and configuration
2. Reproducible test/runtime result
3. Commit history and exact file state
4. Architecture/design documentation
5. README/project descriptions
6. AI-generated research, summaries, prompts, or Studio output

AI-generated research is **research input**, not authoritative project state.

## 5. Current AP1-WEB-Console Baseline

The current audit establishes the following baseline:

- FastAPI backend: **VERIFIED**
- MongoDB runtime integration code: **VERIFIED**
- GitHub API service/routes: **VERIFIED**
- GitHub caching: **VERIFIED**
- React frontend: **VERIFIED**
- Health-monitoring code: **VERIFIED**
- OpenAI SDK dependency: **VERIFIED**
- AI runtime invocation in AP1-WEB-Console: **UNKNOWN**
- Persistent AI memory implementation in AP1-WEB-Console: **UNKNOWN**
- Autonomous agent runtime: **UNKNOWN**
- Multi-agent execution: **UNKNOWN**
- Mock-data removal: **CONFLICTING** where documentation describes completion but `frontend/src/mock.js` remains present

These labels describe the evidence available during the audit; they do not claim that an UNKNOWN capability does not exist elsewhere in the ecosystem.

## 6. Cross-Repository Evidence

`AMRHZ-AI-13` contains a real `/chat` route in multiple backend/API files, so the existence of a chat endpoint in that repository can be classified as **VERIFIED**. This does not automatically prove that AP1-WEB-Console uses or integrates that runtime.

`AP1-WEB-Console/contracts.md` documents `/api/github/user`, `/api/github/repositories`, and `/api/github/stats`. Those endpoints are supported by the current GitHub route/service implementation and are therefore **VERIFIED** as source-level API paths.

The `AMRHZ-Website` changelog work contains an actual `changelog.js` reference in `index.html`, but individual checkpoint claims and commit-specific acceptance should still be verified against the exact commit/file state before being promoted to a general ecosystem fact.

## 7. Studio Output Rule

Audio, video, slides, reports, mind maps, flashcards, and quizzes generated from AMRHZ research must preserve evidence status. They must not silently convert:

- PROPOSED → VERIFIED
- UNKNOWN → VERIFIED
- README claim → runtime fact
- mock/fixture → production capability
- AI-generated research → authoritative architecture

If evidence is insufficient, the output must say **UNKNOWN** rather than filling the gap with an assumption.

## 8. Development Gate

Before implementation based on research:

`RESEARCH → EXTRACT CLAIMS → CROSS-CHECK SOURCE → CLASSIFY STATUS → DECIDE → DEVELOP → VERIFY → DOCUMENT`

The protocol is a guardrail, not an additional product feature. It should remain lightweight and should not create a second development loop.

## 9. Research Provenance

The initial framework was supplied from Gemini NotebookLM research on 2026-09-14. The research proposed the same core evidence principles and Studio-output classifications used here. The research itself is treated as **RESEARCH INPUT**, while repository evidence determines implementation status.

**Build in public. Fail in public. Learn in public. Document the journey. ∞↔13**
