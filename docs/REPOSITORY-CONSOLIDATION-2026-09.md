# Repository consolidation — 2026-09-26

This maintenance change consolidates documentation and clarifies historical onboarding. It introduces no new protocol semantics or package release.

| Previous repository | Maintained destination | Treatment of old repository |
|---|---|---|
| `hjs-spec/jep-architecture` | [Architecture](architecture/README.md) | Migration notice; retain prior files/history, ready for GitHub read-only archive |
| `hjs-spec/jep-vs-logging` | [Comparison](comparisons/logging.md) and [legacy illustration](../examples/legacy/logging-comparison/README.md) | Migration notice; retain prior files/history, ready for GitHub read-only archive |
| `hjs-spec/jep-e2e-demo` | [Current onboarding](https://github.com/hjs-spec/jep-quickstart) | Historical Core 0.6 example and release remain available; ready for GitHub read-only archive |

The E2E example is not byte-converted into Core 0.7. It contains a distinct historical signed J/D/T/V flow; the current Quickstart has its own documented supported examples.

## Provenance

Architecture source: [`daedfeef8671f949fcef274155e9436a7b6678cc`](https://github.com/hjs-spec/jep-architecture/tree/daedfeef8671f949fcef274155e9436a7b6678cc). All tracked files were copied into `docs/architecture`; the README command/location and HJS documentation link were updated for the new home. Diagrams and their generator retain their behavior.

Logging source: [`7ed10ec09389cf14d6c9730df21c4109c0e9b777`](https://github.com/hjs-spec/jep-vs-logging/tree/7ed10ec09389cf14d6c9730df21c4109c0e9b777). The Python script and ignore rules were copied byte-for-byte. The maintained explanatory document was updated for Core 0.7 and explicitly identifies the script's historical unsigned format.

[Source file hashes and destinations](consolidation-sources.json) allow each copied asset to be compared with its source. Published Core -07 files, prior releases, historical signatures and frozen research baselines are unchanged.

## Link and archive handling

Current Core documentation and organization navigation use the new destinations. Existing release reports keep their historical PR, release and source citations. The original repositories retain migration notices so external links still lead to a useful page.

Migration and deprecation notices do **not** by themselves set GitHub's repository `archived` flag. That separate repository-settings action must be verified after it is applied. No repository deletion is part of this change.
