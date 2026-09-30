# JEP reference validators

## Current: JEP Core 0.7

After installing `jep-core-conformance==0.7.7`, follow the
[packaged first-event example](../README.md#verify-your-first-event). For a full
reference exchange, run `jep-byoi demo --report byoi-reference-report.json`.

The following commands require a repository checkout:

```bash
python reference-validator/jep_validate_07.py validate EVENT.json --keys KEYS.json
python reference-validator/jep_validate_07.py run-tests test-manifest-0.7.json
```

The 0.7 validator reports independent checks and, in acceptance mode,
`accepted` or `already_accepted`. It uses stable Event Identity
`(who,id)`; it does not require a Core nonce.

CLI setup failures, such as an unreadable key file, exit 2 with a concise message
on stderr. A completed
validation still returns its structured result; a non-valid result exits 1.

## Validation results and storage

Missing verification keys produce `indeterminate`, not proof of invalidity.
Malformed input produces structured errors. Missing/corrupt/locked acceptance
state produces an indeterminate acceptance outcome without replacing the state.
The filesystem reference store serializes a local acceptance decision; it does
not atomically apply an external business effect or provide multi-host consensus.

## Legacy: JEP Core 0.6

`reference-validator/jep_validate.py` is retained as an explicit pre-0.7
compatibility validator. It preserves nonce and Validation Level behavior
needed to reproduce historical 0.6 tests.

Do not invoke the legacy validator automatically after a 0.7 failure.
Historical decoding must be explicitly selected.
