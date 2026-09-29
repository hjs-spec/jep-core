# JEP Core

The canonical source for **Judgment Event Protocol**: signed statements of Judgment (J), Delegation (D), Termination (T) and Verification (V).

Core defines event structure and observable checks. It does not decide truth, authority, legal effect, causality, policy or external consequences. JEP is an individual Internet-Draft, not an IETF-endorsed standard.

## Install the validator

In a fresh Python environment:

```sh
python -m pip install jep-core-conformance==0.7.5
jep-validate --help
jep-validate validate event.json --keys keys.json
```

`event.json` must be the actual event and `keys.json` the verifier's key map; use the [local create/export/verify example](https://github.com/hjs-spec/jep-agent-sdk#local-create--export--independent-verification) to generate synthetic sample files. Demo-supplied public keys establish signature consistency, not independently trusted actor identity. No hosted API or account is required.

Do not install historical `jep-v06-conformance-seed` alongside this package: they share the `jep_conformance` import namespace. The current package already includes the explicit `jep-validate-06` compatibility command. Existing old environments and signed archives are not silently migrated.

## Start here

| Task | Entry |
|---|---|
| Read the published protocol | [Frozen Internet-Draft -07](https://github.com/hjs-spec/jep-core/tree/main/releases/draft-07/) |
| Read the working source | [Editor's Copy](https://github.com/hjs-spec/jep-core/blob/main/draft-wang-jep-judgment-event-protocol.md) |
| Implement or migrate | [Implementer guide](https://github.com/hjs-spec/jep-core/blob/main/docs/IMPLEMENTER-GUIDE.md) · [0.7 migration](https://github.com/hjs-spec/jep-core/blob/main/docs/MIGRATION-0.7.md) |
| Create, export and independently verify locally | [Agent SDK local example](https://github.com/hjs-spec/jep-agent-sdk#local-create--export--independent-verification) |
| Try a locally hosted HTTP API | [HTTP Quickstart](https://github.com/hjs-spec/jep-quickstart) |
| Choose a client or recorder | [Integration directory](https://github.com/hjs-spec/.github/blob/main/PROJECTS.md#integrate) |
| Understand component boundaries | [Architecture](https://github.com/hjs-spec/jep-core/blob/main/docs/architecture/README.md) |

## Current contract

**Core 0.7 · wire major `jep: "1"` · published 2026-09-26.**

- Event Identity `(who,id)` identifies an event; Event Hash identifies an exact signed artifact.
- Acceptance is idempotent per Event Identity within an acceptance domain.
- Validation reports independent checks and `valid`, `invalid` or `indeterminate`.
- Freshness mechanisms belong to profiles; Core does not require a nonce.
- Chain reconstruction, delegation enforcement and termination cascade belong to companion/application layers.

The published -07 snapshot is immutable. Its exact RFCXML and SHA-256 are recorded in the [freeze record](https://github.com/hjs-spec/jep-core/blob/main/releases/draft-07/README.md). Later changes belong to the Editor's Copy and a subsequent draft. [Datatracker](https://datatracker.ietf.org/doc/draft-wang-jep-judgment-event-protocol/) is the external publication record.

## Develop and test from source

Clone this repository before using the source-only commands below:

```sh
git clone https://github.com/hjs-spec/jep-core.git
cd jep-core
python -m pip install -e '.[test]'
make validate conformance repository-check
python -m pytest
```

The default Python validator, schemas and manifest target Core 0.7. [Validator usage](https://github.com/hjs-spec/jep-core/blob/main/reference-validator/README.md) explains keys and acceptance storage.

## Current and historical assets

| Current | Historical compatibility |
|---|---|
| Core `-07`; profiles/conformance `-01` | Core `-06`; profiles/conformance `-00` |
| `test-manifest-0.7.json`, Python `jep_validate_07.py` | `test-manifest-0.6.json`, Python `jep_validate.py` |
| Versioned 0.7 schemas and vectors | Go and TypeScript validators currently support **0.6 only** |

Schemas and tools are implementation aids; the applicable specification controls normative requirements. Use `make conformance-legacy` only for known 0.6 artifacts. Never select a legacy decoder because current validation failed, or rewrite a historical signed artifact.

[Documentation index](https://github.com/hjs-spec/jep-core/blob/main/docs/README.md) · [Versioning](https://github.com/hjs-spec/jep-core/blob/main/docs/VERSIONING.md) · [Logging comparison](https://github.com/hjs-spec/jep-core/blob/main/docs/comparisons/logging.md) · [Current delivery status](https://github.com/hjs-spec/.github/blob/main/DELIVERY-CURRENT.md)

The repository was previously named `jep-v06`. Repository identity is now stable; protocol drafts and software packages have separate versions. Maintainer-operated production API hosting is deferred; self-hosting remains optional.
