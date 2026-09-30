# Historical Validation Levels (pre-0.7)

This file documents a **legacy pre-0.7 model**.

JEP Core 0.7 replaced cumulative Validation Levels 0-4 with independent
validation checks. Current implementations should use
[VALIDATION-CHECKS.md](../../VALIDATION-CHECKS.md).

Do not map a 0.7 validation result back into a synthetic "highest level".
Doing so hides which checks were actually performed and incorrectly pulls
profile/chain/policy semantics into Core.

For historical 0.6 verification, use the explicitly selected legacy
validator and historical specification.
