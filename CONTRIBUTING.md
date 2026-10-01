# Contributing to JEP Core

Choose a route below to report a problem, share an implementation or propose a change.

| What you have | Where to send it |
| --- | --- |
| A setup question, software bug or documentation fix | [Open an issue](https://github.com/hjs-spec/jep-core/issues/new) with the package version, command, expected result and actual result; small documentation fixes can go directly to a pull request |
| A specification ambiguity or conflicting implementation behavior | [Open an issue](https://github.com/hjs-spec/jep-core/issues/new); name the exact draft, section, expected behavior and minimal example |
| A first attempt to use JEP | Choose a [first-use task](docs/FIRST-USE-CHECK.md) and submit its result or blocker through the linked form |
| An independent implementation | [Implementation report](https://github.com/hjs-spec/jep-core/issues/new?template=independent-implementation.yml) |
| Reproducible interoperability results | Run the [BYOI path](docs/BYOI-CONFORMANCE.md), then submit an [interoperability report](https://github.com/hjs-spec/jep-core/issues/new?template=interoperability-result.yml) |
| A security-sensitive issue | Follow [SECURITY.md](SECURITY.md) and report privately |

## Reports and independence

A report may describe a producer, verifier or acceptance processor separately.
Disclose implementation version/commit, reused JEP libraries, conformance
classes, modes, profiles, limitations and the exact suite digest. A wrapper
around this validator is useful integration evidence but is not an independently
implemented verifier. Self-reported and maintainer-reproduced results must remain
distinguishable. Listing a report is not certification.

Use synthetic fixtures and public test keys. Never upload production private
keys, credentials, personal data or confidential business evidence. Report links
and patches are reviewed as untrusted input; submission does not authorize a
maintainer to execute third-party code or access a submitter's deployment.

## Changes

1. Explain the observed problem. For protocol behavior, link the applicable requirement in the [specification sources](docs/SPECIFICATION-SOURCES.md).
2. Make the smallest change on a branch. Keep Core, profile behavior and tools
   distinct; add a regression check when behavior changes.
3. Set up the [development environment](README.md#develop-and-test-from-source), then run `make repository-check conformance` and the relevant tests. BYOI changes
   also require `python -m pytest tests/test_byoi.py` and `make byoi-check`.
4. Open a pull request with the result, evidence and known limitations. Before merging, bring the branch up to date with `main`, pass the required GitHub Actions checks and resolve review conversations.

Core 0.7 is in a feature-stability period: prioritize adoption, interoperability
and implementation corrections. New Core capabilities require a concrete
problem and an explanation of why profiles or existing semantics cannot solve
it. Security findings and specification contradictions do not need to wait for
an adopter. Published snapshots never change; specification corrections belong
in a later draft and must document compatibility effects.

## Contribution rights

By submitting original code or implementation-documentation changes for
inclusion, you agree that they may be distributed under their applicable
repository license. Only submit material you have authority to contribute.
Identify third-party sources and preserve their license/attribution notices.
Specification contributions must be compatible with the applicable IETF
contribution/IPR rules; a GitHub PR does not itself claim IETF submission or
transfer ownership. See [LICENSING.md](LICENSING.md).
