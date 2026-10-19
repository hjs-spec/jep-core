# Probity reader through native BYOI

This integration tests the separate Probity Core 0.7 fixture reader through JEP's
native BYOI runner. It does not replace the [original pinned pilot](../.github/workflows/probity-core07.yml)
or [candidate gate proposed in #49](https://github.com/hjs-spec/jep-core/pull/49).
Their source pins and claims remain unchanged.

## Boundary found

At reader commit `cbd3ea8f4de89b835d6d3c4182ff4b4b1c7608f9`, Probity's own fixed
script executes 25 verifier, four producer and eight synthetic acceptance
assertions. That script checks selected expected fields, not the complete native
BYOI result envelope. Directly passing the original adapter to native BYOI gives
four producer passes, 25 incomplete-result failures and eight acceptance setup
failures: it omits empty diagnostic arrays and expects its runner to initialize
the SQLite database before the first read-only probe.

The [JEP-owned bridge](../integration/probity_byoi_bridge.py) performs only:

- Explicitly add absent `warnings: []` and `errors: []` arrays. Preserve existing
  diagnostics, malformed values, statuses, checks, hashes, events and signatures.
- During the optional setup hook, call Probity's unchanged initializer on a fresh
  `probity-core07` subdirectory of the supplied synthetic state directory.
- Map subsequent state paths to that directory. The probe uses Probity's existing
  read-only SQLite connection and never initializes or repairs state.

Conformance -02 section 5.4 requires warnings and errors to be distinguished;
the executable result envelope is a runner interface. No Core semantics, frozen
publication, signed fixture or expected answer is changed. Probity's original
source is neither patched nor republished by this integration. The reader's own
scope and stated independence limitations continue to apply.

## Reproduce

Use a trusted checkout of this candidate JEP branch and a fresh Python 3.10+
environment. Clone the public reader separately and explicitly select its pin:

```sh
git clone https://github.com/probityai/agent-evidence-vectors.git external-reader
git -C external-reader checkout --detach cbd3ea8f4de89b835d6d3c4182ff4b4b1c7608f9
python -m pip install -e '.[test]'
python -m pip install -r external-reader/interop/jep-core07-reader/requirements.txt
python integration/run_probity_byoi.py --reader-root external-reader --report probity-native-byoi-report.json
```

The report and `.implementation.json` sidecar must not already exist. The driver
checks the reader's exact Git HEAD and refuses tracked reader modifications.
It invokes native BYOI with all three roles, an explicit setup command and a
separate read-only probe. Expect `outcome: pass`, `tests_passed: 37`,
`tests_failed: 0`. Any other result needs investigation, not editing into a pass.
The report records the exact suite digest and commands; the disclosure names the
reader pin, bridge digest, reused JEP harness and reference producer oracle.

Review the [dedicated CI run](../.github/workflows/probity-byoi.yml) for candidate
evidence. It retains the scoped report and disclosure, including a failed report
when available. This is JEP's reproduction of an independently written reader
through a JEP-owned bridge, not a new unassisted third-party adoption claim.

## Limits

The expected answers were public. The same local operator controls this run and
the synthetic SQLite state. A pass establishes only the selected 37 assertions.
It does not establish complete Core conformance, actor/key trust, external
actions, independent effect custody, power-loss durability, distributed failover,
business completion or production security. Unchecked properties stay unchecked.
