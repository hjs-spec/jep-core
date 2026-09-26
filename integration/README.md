# SDK and API interoperability

## Current Core 0.7 / Binding/02

`verify_current_07.py` checks signed artifacts against current implementations. The
[CI workflow](../.github/workflows/interop-07.yml) pins every companion checkout
by commit; this Core checkout is the implementation under test. No production
service, credentials or acceptance state is used.

```sh
# Place the workflow-pinned companion repositories under /path/to/ecosystem.
# Install their Python dependencies as shown in the workflow; Node and Go must be on PATH.
python integration/verify_current_07.py --workspace /path/to/ecosystem
```

The gate covers:

- 10 published Binding/02 signed carriers plus an independently signed Core event
  with explicit empty extensions and a large, exactly representable JCS number.
- Original, Python SDK, JavaScript SDK, Go SDK and Blackbox serialization paths;
  all 55 roundtrips must preserve signatures and exact Event Hashes.
- Core, API, Agent SDK and Blackbox verification; Core/API/Agent SDK result schemas.
- 50 Binding/02 structural/reference checks, including policy-reference equality,
  plus rejection of a Core-valid carrier with the wrong TSTO policy reference.
- Schema-valid rejection diagnostics for malformed event identities.

The API verifier is called locally; JavaScript request serialization is captured
without a network request. API tests separately cover HTTP request handling.
This gate does not evaluate domain policy, evidence truth or deployed-service
acceptance. It does not replace the original Binding/02 release reproduction:
that release retains its original Core pin, fixtures, checksums and test report.
The current gate uses its signed fixtures with the current Core implementation.

> Historical **Core 0.6** regression harnesses. These scripts assume matching 0.6 API/SDK releases, pre-0.7 result shapes and a Core checkout named `jep-v06`. They are not a gate for current 0.7 packages. For the maintained 0.7 SDK/API flow use [Quickstart tests](https://github.com/hjs-spec/jep-quickstart#test); for current conformance use [Core checks](../README.md#validate-locally).

## Historical 0.6 checks

These checks start a temporary API on loopback with disposable state and a test bearer token. They do not deploy or call a live signing service.

`verify_workspace.py` checks the sibling API, SDKs, reference validators and packaged GitHub Action, including restart/replay behavior. Node and Go must be on PATH; install the API/Python validator dependencies and build the TypeScript validator and Action first.

`verify_packages.py` checks installed Python and JavaScript distribution artifacts, plus the sibling Go module (or an explicitly released Go version). Each SDK creates and verifies all J/D/T/V verbs, preserves conformance metadata and diagnostics, and roundtrips hashes. Python also verifies the JavaScript/Go events.

```sh
python integration/verify_packages.py \
  --workspace /path/to/hjs-spec \
  --python-wheel /path/to/jep_sdk_py-0.6.2-py3-none-any.whl \
  --javascript-tarball /path/to/hjs-spec-jep-sdk-js-0.6.2.tgz \
  --go-version v0.6.2
```

Omit `--go-version` when testing local unmerged changes. Wheel and tarball files must be trusted release artifacts or locally built packages. The separate `jep-agent-sdk/scripts/check_coexistence.py` checks the legacy/current Python namespaces and CLI commands in fresh environments, both installation orders and independent uninstalls.
