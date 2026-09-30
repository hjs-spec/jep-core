# Bring your own JEP Core 0.7 implementation

This path runs a scoped suite against an implementation written in any language.
No account, hosted API or companion checkout is required. Choose
producer, verifier and/or acceptance processing. A verifier-only implementation
need not implement a producer.

The normative sources are [Core -07, Profiles -01 and Conformance -02](SPECIFICATION-SOURCES.md).
Tests and reference code do not override them. Disagreements are reportable bugs
or clarification requests, not permission to silently redefine Core.

## Install the released runner

Use Python 3.10 or later in a fresh environment.

```sh
python -m pip install jep-core-conformance==0.7.7
jep-byoi export jep-example
jep-validate validate jep-example/vectors/J-basic.json --keys jep-example/keys.json
```

For development, a checkout containing this release can instead be installed
with `python -m pip install -e '.[test]'`.

The sample should return `status: "valid"` and a passing cryptographic check.
Use a new writable output directory. Export
includes manifest, signed fixtures, public keys, producer templates, coverage and
report schema. The manifest binds every file by SHA-256. Reports identify the
exact manifest digest. Do not rewrite a released suite; version changed assertions.

## Try the complete reference exchange

```sh
jep-byoi demo --report byoi-reference-report.json
```

This runs the bundled producer/verifier adapter and writes a report with 29
passing checks. It needs no Git checkout or `scripts/` directory. The report
identifies a reference wrapper, package version and code digests; it does not
claim independent adoption or acceptance effects. A nonzero exit requires
inspection of the report or command error.

## Describe your implementation

Create `implementation.json` from this shape, replacing the values with the
actual tested implementation and commit:

```json
{
  "name": "example-rust-jep",
  "version": "0.1.0",
  "source": "https://example.org/my-implementation",
  "revision": "the-exact-tested-commit",
  "independence": "independently-implemented",
  "reused_components": []
}
```

Disclose any reused JEP validator/SDK. Cryptographic/JSON libraries may also be
listed. Closed-source implementations can name an identifiable build and explain
reproduction limits. This field is a disclosure, not a verified independence claim.

## Adapter contract

The runner launches a **trusted local command** once per request, sends one UTF-8
JSON object on stdin, and reads one JSON object from stdout. Logs go to stderr.
Each invocation is a fresh process. No shell expansion is used. A successful
adapter exchange exits zero even when the JEP result is `invalid` or `indeterminate`.
Use `{"unsupported":"reason"}` for unsupported operations; this cannot pass.

The command line is a JSON argv array. Do not put credentials in it. Do not run
unreviewed adapters or point this harness at production data/effects.

| Operation | Input | Response |
| --- | --- | --- |
| `validate` | `event_json` raw string, public JWK `keys` map, `mode`, explicit `profile`, `signature_class` | `{"result": <structured validation result>}` |
| `produce` | `unsigned_event`, `signature_class` | `{"event_json": <signed JSON string>, "keys": <public JWK map>}` |
| `set_state_availability` | `state_dir`, `acceptance_domain`, boolean `available` | `{"configured": true}` for synthetic failure injection |
| `observe_effects` (separate probe) | `state_dir`, `acceptance_domain` | `{"effect_count": <nonnegative integer>}` |

Every request includes `adapter_protocol: "jep-byoi/1"`. The v1 suite explicitly
selects `jep-core-0.7` and `JEP-Baseline-Ed25519-JWS-JCS-0.7`. The supplied keys
establish test signature consistency, not trusted actor identity. The adapter
must preserve raw input for duplicate-member/invalid-JSON cases: do not parse and
re-serialize `event_json` before passing it to the implementation.

In acceptance scenarios, both archival and acceptance requests also carry
`state_dir` and `acceptance_domain`. Each scenario gets isolated empty state;
steps within it share state across fresh processes. Map domains to distinct
acceptance contexts. The availability hook must disable only synthetic acceptance
state while leaving the read-only effect probe usable. Restore it when requested.

## Run against your implementation

```sh
jep-byoi run --implementation implementation.json --role verifier \
  --adapter '["./my-adapter"]' --report byoi-report.json
```

For a producer, use `--role producer`; combine roles by repeating `--role`.
The runner gives the producer unsigned J/D/T/V templates with assigned stable IDs
and verifies the returned signed artifacts using the bundled reference verifier.
This tests that exchange, not every producer behavior. To show both directions,
select producer and verifier: your verifier receives the bundled signed suite fixtures.

## Acceptance processors

```sh
jep-byoi run --implementation implementation.json --role acceptance \
  --adapter '["./my-adapter"]' \
  --effect-probe '["./read-test-effect-ledger"]' \
  --effect-scope 'Synthetic delivery receipts in the isolated test database' \
  --report byoi-acceptance-report.json
```

Acceptance adds verifier assertions automatically. The independent read path
must observe the protected effect's actual committed records, not sum
`effect_applied` flags or count requests in the runner. Both adapter and probe
need review; separating the commands alone does not prove the observer correct.
If no effect observer is available, run the verifier role and disclose the gap.

The suite exercises archival non-consumption, safe retry across fresh processes,
identity conflicts, re-signing unchanged unsigned content, the same ID under a
different actor, domain isolation, rejection without identity consumption,
eight concurrent deliveries followed by a retry, and unavailable-state recovery.
All concurrent requests reach the target. Temporary `indeterminate` outcomes may
occur, but the retry and observed ledger must establish exactly one protected effect.

For repository developers, `tests/support/byoi_acceptance_fixture.py` is a synthetic SQLite test target for
checking the harness, including deliberate double-effect and false-flag failures.
It is not an independent implementation, production runtime or deployment guarantee.

## Read and publish the result

Exit 0 means the selected assertions passed; exit 1 means failed or incomplete;
exit 2 means a configuration/artifact problem. Default per-command timeout is
15 seconds and is configurable up to 60 seconds. Inspect the JSON report and
[coverage](../reference-validator/byoi_suite/coverage.json); this suite does not
claim complete Core or profile coverage. See the [report guide](INTEROPERABILITY-REPORT.md)
and [contribution paths](../CONTRIBUTING.md).
