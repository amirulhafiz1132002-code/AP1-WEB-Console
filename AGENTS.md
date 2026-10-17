# AI Working Contract — AP1-WEB-Console

This repository's role in the AMRHZ ecosystem: **Application console and system integration**.

## Required reading
1. [Local adoption status](docs/AMRHZ-STANDARDS-ADOPTION.md)
2. [Canonical UI Evolution Contract](https://github.com/amirulhafiz1132002-code/amrhz-architecture-core/blob/main/docs/standards/UI-EVOLUTION-CONTRACT.md)
3. [Canonical Dual-Layer Documentation Standard](https://github.com/amirulhafiz1132002-code/amrhz-architecture-core/blob/main/docs/standards/DUAL-LAYER-DOCUMENTATION-STANDARD.md)
4. [Canonical Evidence and State Contract](https://github.com/amirulhafiz1132002-code/amrhz-architecture-core/blob/main/docs/standards/EVIDENCE-AND-STATE-CONTRACT.md)

Canonical standards proposal: [amrhz-architecture-core PR #1](https://github.com/amirulhafiz1132002-code/amrhz-architecture-core/pull/1). Until that PR is reviewed and merged, treat the standards as **PROPOSED**, not as an approved or enforced policy.

## Repository-specific boundaries
- Do not change application code, UI, API behavior, backend state, secrets, deployment settings, or integrations as part of standards adoption. Respect existing truth-protocol and architecture documents.
- Existing docs/AMRHZ-TRUTH-PROTOCOL.md and docs/architecture.md are project-specific references; verify them against current implementation and test evidence.
- Inspect the current branch, implementation, relevant tests, and configuration before proposing a change.
- Use the smallest change that solves a demonstrated problem. Keep unrelated files and behavior unchanged.
- Do not claim `VERIFIED` without a scoped, observed test result; do not claim `LIVE` without environment-specific deployment/runtime evidence.
- If evidence is missing or contradictory, report `BLOCKED` or `UNKNOWN`; do not fill gaps with assumptions.
- Do not deploy, delete data, change secrets, rewrite architecture, or expand into other repositories unless explicitly approved.
- Report changed files, tests actually run, results, limitations, and remaining unknowns.

These instructions document intended workflow; they do not by themselves prove that automated enforcement exists.
