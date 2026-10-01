# Try JEP for the first time

Choose the task you need below. Start in a fresh environment and follow its
linked instructions. No HJS background is required. Record the installed package
versions, commands and results so another person can reproduce the attempt.

| Task | Prerequisites and instructions | Expected result |
| --- | --- | --- |
| Verify an existing event | Python 3.10+; [packaged sample](../README.md#verify-your-first-event) | `status: "valid"` and `checks.cryptographic: "pass"` using the supplied test keys |
| Create and verify locally | Python 3.10+; [Agent SDK local example](https://github.com/hjs-spec/jep-agent-sdk#local-create--export--independent-verification) | Create a signed event, export it, then verify it with the separately installed Core verifier |
| Connect over HTTP | Python 3.10+, Git, Bash/WSL and two terminals; [HTTP Quickstart](https://github.com/hjs-spec/jep-quickstart) | Start the local API, create a signed event through the client, then obtain a valid archival verification |
| Check your own implementation | Python 3.10+ and a trusted local adapter for your implementation; [BYOI guide](BYOI-CONFORMANCE.md) | A JSON report identifying the tested implementation, roles and suite digest; exit 0 when all selected assertions pass |

The packaged samples use synthetic data and public test keys. A passing
signature check does not establish actor trust or authorize a business action.
For BYOI, the bundled demo checks the runner setup. Testing your own producer or
verifier requires connecting your implementation through the documented adapter.

## Share what happened

Use the [first-use report](https://github.com/hjs-spec/jep-core/issues/new?template=first-use-report.yml)
for a completed attempt or a blocker. Choose one task per report; you do not need
to complete all four. Include:

- OS, Python and installed package versions, plus the instructions you followed.
- Commands, expected result and actual result; link or attach a small reproducible example.
- Whether you finished unaided, needed help, were blocked, or did not attempt a step.
- The exact place you had to guess, find another page or ask the author, if any.

A failed attempt is useful evidence. Report only steps you actually ran.
For completed implementation tests, attach the generated JSON through the
[interoperability report](INTEROPERABILITY-REPORT.md), which records coverage and
implementation independence. A reference wrapper is integration evidence.

Remove credentials, private keys and private data from public reports. Send
security-sensitive findings through [SECURITY.md](../SECURITY.md).
