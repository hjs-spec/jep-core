# JEP Core

Create portable signed event records and verify their structure and signatures.

Judgment Event Protocol defines signed statements of Judgment (J), Delegation (D),
Termination (T) and Verification (V). Start with the packaged sample below.

[Website](https://www.judgmentevent.org/) · [Getting started](https://www.judgmentevent.org/developers)

## Verify your first event

Use Python 3.10 or later in a fresh environment. These commands work without a
repository checkout, account, hosted API or another SDK:

```sh
python -m pip install jep-core-conformance==0.7.7
jep-byoi export jep-example
jep-validate validate jep-example/vectors/J-basic.json --keys jep-example/keys.json
```

Look for `status: "valid"` and `checks.cryptographic: "pass"`. The keys are public
synthetic fixtures: this verifies the sample's structure and signature, not trust
in a real actor. Use a new export directory; an existing directory is not overwritten.

## Continue from here

| I want to… | Entry |
| --- | --- |
| Record my own events locally | [Agent SDK example](https://github.com/hjs-spec/jep-agent-sdk#local-create--export--independent-verification): create, export and verify a signed event |
| Use an HTTP service | [HTTP Quickstart](https://github.com/hjs-spec/jep-quickstart): start a local API, then create and verify through a client |
| Build an independent implementation | [One-page overview](https://github.com/hjs-spec/jep-core/blob/main/docs/ONE-PAGE-OVERVIEW.md) → [Implementer guide](https://github.com/hjs-spec/jep-core/blob/main/docs/IMPLEMENTER-GUIDE.md) → [BYOI tests](https://github.com/hjs-spec/jep-core/blob/main/docs/BYOI-CONFORMANCE.md) |
| Submit reproducible results | [Report guide](https://github.com/hjs-spec/jep-core/blob/main/docs/INTEROPERABILITY-REPORT.md) |

For setup questions, bugs, documentation fixes and implementation reports, use the
[contribution routes](https://github.com/hjs-spec/jep-core/blob/main/CONTRIBUTING.md).

## Current contract

**Core 0.7 · wire major `jep: "1"` · published 2026-09-26.**

JEP is an individual Internet-Draft, not an IETF-endorsed standard.

- Event Identity `(who,id)` identifies an event; Event Hash identifies an exact signed artifact.
- Acceptance is idempotent per Event Identity within an acceptance domain.
- Validation reports independent checks and `valid`, `invalid` or `indeterminate`.
- Freshness mechanisms belong to profiles; Core does not require a nonce.
- Chain reconstruction, delegation enforcement and termination cascade belong to companion/application layers.

Core checks event structure and signatures. Apply your own trust and authorization
rules before acting on a record; see the [validation checks](https://github.com/hjs-spec/jep-core/blob/main/docs/VALIDATION-CHECKS.md).

The [published -07 snapshot](https://github.com/hjs-spec/jep-core/tree/main/releases/draft-07/)
is immutable. Its checksum and the current Profiles -01 and Conformance -02
publications are listed in the [source map](https://github.com/hjs-spec/jep-core/blob/main/docs/SPECIFICATION-SOURCES.md).

## Develop and test from source

For repository development, clone this repository first:

```sh
git clone https://github.com/hjs-spec/jep-core.git
cd jep-core
python -m pip install -e '.[test]'
make validate conformance repository-check
python -m pytest
```

[Validator usage](https://github.com/hjs-spec/jep-core/blob/main/reference-validator/README.md)
explains keys, validation results and acceptance storage.

## More documentation

Use the [documentation index](https://github.com/hjs-spec/jep-core/blob/main/docs/README.md)
for profile authoring, validator configuration and optional integrations.
For an existing 0.6 integration, use the [migration guide](https://github.com/hjs-spec/jep-core/blob/main/docs/MIGRATION-0.7.md).
[Current ecosystem delivery](https://github.com/hjs-spec/.github/blob/main/DELIVERY-CURRENT.md)
tracks separately released components.

## Licensing and security

Original implementation code and implementation aids use [BSD-3-Clause](https://github.com/hjs-spec/jep-core/blob/main/LICENSE).
Internet-Draft text, extracted Code Components and third-party material retain
their applicable terms; see [licensing scope](https://github.com/hjs-spec/jep-core/blob/main/LICENSING.md).
Report security-sensitive findings through [SECURITY.md](https://github.com/hjs-spec/jep-core/blob/main/SECURITY.md).
