# JEP Core 0.7 Validation Checks

JEP Core 0.7 does **not** define cumulative Validation Levels 0-4.

## Core-defined checks

- `syntax`
- `cryptographic`
- `event_identity`
- `reference_integrity`
- `extension_processing`

## Trust / acceptance profile checks

- `actor_binding`
- `freshness`
- `audience`

## Companion / external checks

- `chain_integrity`
- `policy`

Each check reports one of:

`pass`, `fail`, `not_checked`, `not_applicable`, `unsupported`,
or `indeterminate`.

Overall status is `valid`, `invalid`, or `indeterminate`.

The old level model remains historical documentation for pre-0.7 artifacts
only. It MUST NOT be used to describe JEP Core 0.7 conformance.
