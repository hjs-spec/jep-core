# JEP Architecture

Use the local Agent SDK or an HTTP API/client to create signed Core 0.7 events.
The Core verifier checks exported events with supplied public keys. Applications
manage signing-key trust, permissions and storage.

For runnable setup, use the [Core sample](../../README.md#verify-your-first-event)
and [choose a recording path](../../README.md#continue-from-here). The
[format and verification matrix](architecture-notes.md#format-and-verification-matrix)
lists the checks each component supports.

## Diagram index

| Diagram | Purpose | Markdown | SVG |
| --- | --- | --- | --- |
| Recording and verification | Local and HTTP creation paths produce signed events for Core verification. | [diagrams/protocol-stack.md](diagrams/protocol-stack.md) | [diagrams/protocol-stack.svg](diagrams/protocol-stack.svg) |
| Execution Path | Shows the path a runtime action takes from agent request to replayable archive. | [diagrams/execution-path.md](diagrams/execution-path.md) | [diagrams/execution-path.svg](diagrams/execution-path.svg) |
| Delegation Lineage | Shows how human intent is delegated through agents and tools to external systems. | [diagrams/delegation-lineage.md](diagrams/delegation-lineage.md) | [diagrams/delegation-lineage.svg](diagrams/delegation-lineage.svg) |
| Replay Verification | Shows verification results and the limits of the checks actually performed. | [diagrams/replay-verification.md](diagrams/replay-verification.md) | [diagrams/replay-verification.svg](diagrams/replay-verification.svg) |
| Trust Boundary | Shows which principals own decisions, execution, policy, tool contracts, and outside effects. | [diagrams/trust-boundary.md](diagrams/trust-boundary.md) | [diagrams/trust-boundary.svg](diagrams/trust-boundary.svg) |

See [architecture-notes.md](architecture-notes.md) for implementation notes, data responsibilities, and development guidance.

## Regenerating SVG diagrams

The Mermaid blocks in `diagrams/*.md` are the source of truth. Checked-in SVG files are included as lightweight previews for tools that do not render Mermaid directly.

From the jep-core repository root, regenerate the checked-in SVG previews without external dependencies:

```bash
python docs/architecture/scripts/generate-static-svgs.py
```

[Migration provenance](../REPOSITORY-CONSOLIDATION-2026-09.md) records the original architecture repository and source revision.
