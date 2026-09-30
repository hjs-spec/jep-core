# JEP Core

Judgment Event Protocol defines signed statements of Judgment (J), Delegation (D),
Termination (T) and Verification (V). Core defines event structure and observable
checks. It does not decide truth, authority, legal effect, causality, policy or
external consequences. JEP is an individual Internet-Draft, not an IETF-endorsed standard.

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

To generate a complete reference demonstration report:

```sh
jep-byoi demo --report byoi-reference-report.json
```

The report identifies a reference wrapper and its exact code digests. It covers
25 verifier assertions and four producer checks, with acceptance scenarios not
selected. It is not evidence of an independent implementation or full conformance.

Do not install historical `jep-v06-conformance-seed` alongside this package: they
share the `jep_conformance` import namespace. The current package includes the
explicit `jep-validate-06` compatibility command.

## Continue from here

| Step | Entry |
| --- | --- |
| 1. Understand the contract | [One-page overview](https://github.com/hjs-spec/jep-core/blob/main/docs/ONE-PAGE-OVERVIEW.md) · [Exact specification sources](https://github.com/hjs-spec/jep-core/blob/main/docs/SPECIFICATION-SOURCES.md) |
| 2. Implement your selected role | [Implementer guide](https://github.com/hjs-spec/jep-core/blob/main/docs/IMPLEMENTER-GUIDE.md) |
| 3. Test your implementation | [BYOI adapter and test guide](https://github.com/hjs-spec/jep-core/blob/main/docs/BYOI-CONFORMANCE.md) |
| 4. Submit reproducible results | [Report guide](https://github.com/hjs-spec/jep-core/blob/main/docs/INTEROPERABILITY-REPORT.md) · [Contribution routes](https://github.com/hjs-spec/jep-core/blob/main/CONTRIBUTING.md) |

## Current contract

**Core 0.7 · wire major `jep: "1"` · published 2026-09-26.**

- Event Identity `(who,id)` identifies an event; Event Hash identifies an exact signed artifact.
- Acceptance is idempotent per Event Identity within an acceptance domain.
- Validation reports independent checks and `valid`, `invalid` or `indeterminate`.
- Freshness mechanisms belong to profiles; Core does not require a nonce.
- Chain reconstruction, delegation enforcement and termination cascade belong to companion/application layers.

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
explains keys and acceptance storage. Go and TypeScript validators in this
repository support **0.6 only**; select legacy tools explicitly. Never infer a
legacy decoder from a current validation failure or rewrite historical signed events.

## More documentation

The [documentation index](https://github.com/hjs-spec/jep-core/blob/main/docs/README.md)
contains profile authoring, migration, architecture, optional SDK/API integrations
and historical records. No companion repository is required for the path above.
[Current ecosystem delivery](https://github.com/hjs-spec/.github/blob/main/DELIVERY-CURRENT.md)
tracks separately released components. Maintainer-operated API hosting remains deferred.

## Licensing and security

Original implementation code and implementation aids use [BSD-3-Clause](https://github.com/hjs-spec/jep-core/blob/main/LICENSE).
Internet-Draft text, extracted Code Components and third-party material retain
their applicable terms; see [licensing scope](https://github.com/hjs-spec/jep-core/blob/main/LICENSING.md).
Report security-sensitive findings through [SECURITY.md](https://github.com/hjs-spec/jep-core/blob/main/SECURITY.md).
