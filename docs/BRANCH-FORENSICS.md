# AP1-WEB-Console Branch Forensics

**Status:** VERIFIED / FINAL CLEANUP DECISION
**Canonical branch:** `Amrhz`
**Audit principle:** REAL STATE > UI SIMULATION

## Purpose

This record locks the branch-forensics result after source comparison and unique-file extraction review. It separates the canonical source from historical branches that no longer add verified runtime value.

## Final decision

### KEEP — canonical source

- `Amrhz` — **KEEP**
  - Canonical AP1-WEB-Console source of truth.
  - All further development and verification should start from this branch unless a later architecture decision explicitly changes the canonical source.

### CLEANUP — no verified unique runtime value remaining

The following branches are classified as **DEAD / CLEANUP CANDIDATES** after comparison and extraction review:

- `Ap1-projects-Console-workflows` — superseded by `Amrhz`.
- `feature/file-management-integration` — already incorporated into `Amrhz`.
- `feat/sofa-integration` — useful test utilities were already present in `Amrhz`; remaining SOFA material is process/documentation/workflow content, not verified AP1 runtime.
- `file-ingest-skeleton` — no verified file-ingestion runtime was established; remaining unique material is documentation/configuration rather than a proven runtime component.
- `amirulhafiz1132002-code-patch-1` through `amirulhafiz1132002-code-patch-19` — historical patch branches; inspected examples and lineage show obsolete/disconnected snapshots rather than current AP1 source.
- `alert-autofix-9`, `alert-autofix-10`, `alert-fix-10` — superseded security/autofix branches.
- `My-crypto` — disconnected experiment, not part of the current AP1-WEB-Console lineage.
- `codespace-orange-engine-r4jx5pj666v9hg7r` — disconnected Codespace experiment, not part of the current AP1-WEB-Console lineage.

## Extraction result

No branch above contains a verified unique runtime component that must be migrated into `Amrhz` before cleanup.

Important findings:

- `feat/sofa-integration` contained `tests/fixtures.py` and `tests/utils.py`, but equivalent reusable testing utilities are already present on `Amrhz`.
- `tests/fixtures.py` contains mock AI behavior for testing; it is **not** evidence of live AI execution.
- `file-ingest-skeleton` contained `Rival-Ai-Ap1-Asistance-models-prompt.yml`; this is prompt/configuration documentation, not proof of live AI runtime or file-ingestion implementation.
- No branch is allowed to become an alternative source of truth merely because it contains a more ambitious README, prompt, workflow, or UI claim.

## Deletion state

**VERIFIED:** cleanup classification is complete.

**NOT VERIFIED:** remote branch deletion is complete.

The connected GitHub interface available for this audit does not expose a branch-delete operation. Therefore this record deliberately does **not** claim that the remote branches have been deleted.

The correct manual cleanup action is to delete the branches classified above from GitHub, while retaining `Amrhz`.

## Post-cleanup rule

After manual deletion, the expected active branch set for this repository should be centered on:

- `Amrhz` — canonical development source.

Any future branch should have an explicit purpose and should not silently become a competing source of truth.

## Truth rules

1. Do not treat branch names, README claims, prompts, or UI labels as implementation proof.
2. Do not copy mock AI behavior into runtime paths and call it live AI.
3. Do not reopen dead branches merely because they contain interesting wording or generated artifacts.
4. Preserve verified value; remove historical noise.
5. Human approval remains required for architectural source-of-truth changes.
6. `Amrhz` remains canonical unless a later architecture decision explicitly changes it.

**Decision:** PRESERVE VALUE → REMOVE NOISE → LOCK SOURCE → MOVE FORWARD.
