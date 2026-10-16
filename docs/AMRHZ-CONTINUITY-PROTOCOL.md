# AMRHZ Continuity Protocol

**Protocol state:** PROPOSED  
**Implementation state:** NOT IMPLEMENTED BY THIS DOCUMENT  
**Scope:** Durable task checkpoints and explicit handoff between AI agents and development environments  
**Initial repository:** `amirulhafiz1132002-code/AP1-WEB-Console`

## 1. Objective

Preserve enough verified task state for another authorized agent or environment to resume work without relying on the previous chat transcript. A checkpoint is a structured record of intent, current state, evidence, and the next permitted action. It is not proof that an action ran successfully.

## 2. Invariants

1. **Human intent is authoritative.** An agent may suggest scope changes but cannot silently broaden approved scope.
2. **Evidence is separate from claims.** A reported result must identify its evidence or be marked `UNKNOWN`.
3. **One task has one active lease.** Two agents must not both believe they own the same task revision.
4. **State changes are versioned.** A write must name the expected revision; stale writes are rejected as conflicts.
5. **Handoff is explicit.** The sender records a handoff; the receiver acknowledges it before becoming the active owner.
6. **Persistence must be tested.** A successful local file write does not prove cross-deployment or cross-environment durability.
7. **Human approval gates consequential writes.** Repository mutation, deployment, secret changes, and destructive actions require a separately recorded approval.
8. **No credentials in checkpoints.** Tokens, API keys, passwords, private keys, and other secrets must never be copied into task descriptions, context, or evidence.

## 3. Task record (version 1)

A task record should contain:

| Field | Requirement | Meaning |
|---|---|---|
| `task_id` | Required, immutable | Globally unique identifier (UUID recommended) |
| `schema_version` | Required | Record schema version |
| `revision` | Required, monotonically increasing | Optimistic-concurrency version |
| `title` | Required | Short human-readable task label |
| `original_instruction` | Required | User-approved scope, preserved verbatim where practical |
| `status` | Required | Task lifecycle state |
| `evidence_status` | Required | `VERIFIED`, `PROPOSED`, `UNKNOWN`, `CONFLICTING`, `FAILED`, or `FALLBACK` |
| `current_agent_id` | Nullable | Stable identifier of the active, authorized agent |
| `environment` | Nullable | Environment label, e.g. Termux, PC, CI; descriptive only |
| `base_commit` | Nullable | Repository commit against which work was inspected or proposed |
| `summary` | Required | Concise current state, distinguishing fact from assumption |
| `evidence` | Required list | Evidence type, locator, observed result, and timestamp |
| `blocker` | Nullable | Specific unresolved dependency or reason work cannot proceed |
| `next_action` | Required when non-terminal | One bounded next step |
| `approval` | Required for gated actions | Approver, exact action/scope, target, decision, and timestamp |
| `created_at`, `updated_at` | Required | UTC timestamps |
| `created_by`, `updated_by` | Required | Authenticated actor identifiers, not unverified display names |

The schema must reject unknown lifecycle values and malformed required fields. Sensitive values must be redacted before persistence.

## 4. Lifecycle

Task lifecycle and evidence status are separate dimensions.

Allowed task lifecycle states:

- `OPEN` — recorded but not yet accepted by an agent.
- `ACKNOWLEDGED` — an agent explicitly accepted responsibility for the current revision.
- `IN_PROGRESS` — work is underway under the active lease.
- `BLOCKED` — a named blocker prevents the next action.
- `HANDOFF_PENDING` — ownership transfer has been requested but not accepted.
- `COMPLETED` — the stated acceptance criteria have evidence-backed results.
- `FAILED` — a verification or execution attempt failed and the failure is recorded.
- `CANCELLED` — the human owner cancelled the task.

A task must not become `COMPLETED` solely because an agent says it is done. Completion requires acceptance criteria and evidence to be recorded. Reopening a terminal task creates a new revision and records the reason.

## 5. Acknowledgement and handoff

An acknowledgement must include `task_id`, `expected_revision`, `agent_id`, `accepted_scope`, and a timestamp. The service must reject an acknowledgement if the task revision changed, the agent is not authorized, or another agent holds the active lease.

A handoff record must include the sender, intended recipient (or an explicit unassigned queue), the source revision, a concise checkpoint summary, evidence references, blocker, next action, and reason for transfer. Handoff does not transfer ownership until the recipient acknowledges it. An expired or rejected handoff must remain visible in the audit trail.

## 6. Conflict and idempotency rules

- Every state-changing request supplies the expected `revision`.
- A stale revision returns a conflict and must not overwrite newer state.
- Retrying the same request with the same idempotency key must not create duplicate state transitions.
- Concurrent claims must be resolved atomically by the persistence layer.
- Conflicts are surfaced as `CONFLICTING`; agents must re-read state and reconcile rather than force-overwrite.
- Event history is append-only at the application level; corrections are new events that reference the event being corrected.

## 7. Persistence boundary

The existing application has MongoDB integration, while `backend/services/memory_service.py` stores builder events in a local JSONL file. The JSONL file is useful as an event log but is not, by itself, evidence of durable cross-environment storage.

**Proposed direction:** evaluate MongoDB for task records and audit events because the application already connects to it. This remains a proposal until deployment configuration, access controls, atomic claim/version semantics, backups/retention, and cross-environment connectivity are verified. Do not create a second persistence system without a documented reason.

No continuity API should be exposed for writes until authentication and authorization are implemented and tested. An outbound `GITHUB_TOKEN` is not proof that a caller is authorized to change AP1 task state.

## 8. Security and approval boundary

- Authenticate the caller and derive `actor_id` from verified identity, never from a caller-supplied name alone.
- Authorize each operation and task/repository scope.
- Treat agent IDs as identity labels, not credentials.
- Keep secrets out of logs, event payloads, and responses.
- Record approvals as narrowly scoped decisions: actor, action, target, exact scope, timestamp, and expiry or one-time-use identifier.
- Approval for one operation does not authorize unrelated operations.
- Phase one does not execute repository writes, merges, deployments, or shell commands.

## 9. Minimum acceptance tests for a future runtime implementation

1. Create a task and read it back with the same immutable ID and revision.
2. Reject missing or malformed required fields.
3. Accept one valid agent acknowledgement.
4. Reject acknowledgement from an unauthorized agent.
5. Reject a second simultaneous active claim for the same task.
6. Reject stale-revision updates without changing the stored record.
7. Make an idempotent retry produce one logical transition.
8. Preserve handoff history and require recipient acknowledgement before ownership changes.
9. Distinguish `UNKNOWN` evidence from `VERIFIED` evidence.
10. Verify persistence after process restart and across the intended deployment/environment boundary.
11. Verify unauthenticated and unauthorized writes are denied.
12. Verify no secret-bearing field is written to logs or returned to clients.

These tests must run against an isolated test database/collection. Do not run tests that delete or overwrite the shared `memory/events.jsonl` file.

## 10. Implementation sequence

1. Review this contract against the current API and deployment configuration.
2. Select and verify the persistence boundary.
3. Implement schema and service-layer validation in isolation.
4. Add isolated tests for revision conflicts, claims, and handoffs.
5. Implement authenticated read/write API routes only after the authorization design is established.
6. Run targeted tests, then the relevant regression suite.
7. Document exact commit and test evidence; do not claim cross-environment continuity until it has been observed.

**Current truth:** this file specifies the intended protocol. It does not claim that a continuity runtime, authentication boundary, persistent checkpoint API, or multi-agent execution has been implemented.
