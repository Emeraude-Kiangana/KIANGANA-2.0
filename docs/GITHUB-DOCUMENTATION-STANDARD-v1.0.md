# GitHub Documentation Standard v1.0

## Purpose

This standard makes every Emeraude-Kiangana repository understandable, auditable and evidence-first without inflating claims.

## Required project surface

Every active repository should expose:

1. `README.md` — what the project is, scope, run/test commands and limitations.
2. `docs/README.md` — documentation index and source-of-truth map.
3. `docs/PROJECT-STATUS.md` — factual state using the vocabulary below.
4. `tests/` or an explicit statement that automated tests do not yet exist.
5. `.github/workflows/` or an explicit statement that CI does not yet exist.
6. `evidence/` when the project makes reproducibility or verification claims.
7. `SECURITY.md` for projects handling secrets, cryptography, networks, financial concepts or adversarial testing.

## Status vocabulary

Use only these labels when describing maturity:

- **DOCUMENTED** — the behavior, decision or design is written down.
- **IMPLEMENTED** — executable code or an artifact exists in the repository.
- **TESTED** — an explicit test has run with an observed result.
- **REPRODUCIBLE** — another clean environment has enough pinned instructions and artifacts to reproduce the verified result.
- **UNKNOWN** — the repository does not currently contain enough evidence to assert a stronger state.
- **BLOCKED** — a known dependency prevents the next verification step.

A specification is not implementation. A commit message is not test evidence. A successful deployment is not proof that every feature works.

## README minimum

A project README should answer, in under two minutes:

- What is this?
- What problem or hypothesis does it address?
- What is the current verified scope?
- What is explicitly out of scope?
- How do I install/run it?
- How do I test it?
- Where are the evidence and architecture records?
- What are the known limitations?

## Evidence rule

Every strong claim should point to at least one inspectable anchor: source file, test, CI run, commit, generated artifact, checksum or reproducible command.

When evidence is absent, write **UNKNOWN** instead of inferring completion.

## Documentation change rule

Documentation changes must not silently change product behavior. Code, scope and validation changes require their own explicit commits or pull requests.

## Version

Standard: **v1.0**  
Introduced: **2026-09-18**
