# JEP reference validators

## Current: JEP Core 0.7

Use:

```bash
python reference-validator/jep_validate_07.py validate EVENT.json --keys KEYS.json
python reference-validator/jep_validate_07.py run-tests test-manifest-0.7.json
```

The 0.7 validator reports independent checks and, in acceptance mode,
`accepted` or `already_accepted`. It uses stable Event Identity
`(who,id)`; it does not require a Core nonce.

## Legacy: JEP Core 0.6

`reference-validator/jep_validate.py` is retained as an explicit pre-0.7
compatibility validator. It preserves nonce and Validation Level behavior
needed to reproduce historical 0.6 tests.

Do not invoke the legacy validator automatically after a 0.7 failure.
Historical decoding must be explicitly selected.
