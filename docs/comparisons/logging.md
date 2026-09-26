# Signed events and application logs

JEP Core 0.7 defines signed atomic statements and explicit validation checks. Logs remain useful evidence; a log can itself contain structured or signed data. Compare the properties actually implemented rather than treating every log as unverifiable.

| Concern | Current JEP Core / an explicit additional layer | Preserved local illustration |
|---|---|---|
| Event format | `jep`, `id`, `verb`, `who`, `when`, `what`, `sig`; optional Core members follow the schema | Application-specific actor, intent, delegation and authority fields |
| Stable identity | `(who,id)` | No Core identity contract |
| Integrity | Core canonicalization and signatures under an explicit trusted-key policy | Recomputed SHA-256 only; no signature authentication |
| Artifact digest | Event Hash identifies one exact signed artifact | Ordinary sorted-JSON hash with a different local contract |
| Links | Typed references; chain rules are companion/profile behavior | Local previous-event hash links |
| Delegation and authority | A D statement plus independently evaluated application policy | Illustrative declarations, not proof of authority |
| Archival lifecycle | An explicit archival profile or companion implementation | Ordinary JSON output; no archival conformance claim |
| Completeness | Separate trusted evidence/anchor and completeness model | No independent completeness guarantee |

Core 0.7 does not require a top-level nonce or a previous-event hash. A signature does not establish substantive truth, authority, causality or legal effect.

## Preserved unsigned illustration

The [historical script](../../examples/legacy/logging-comparison/demo.py) was migrated without changing its bytes or old envelope semantics. From the jep-core repository root:

```sh
cd examples/legacy/logging-comparison
python demo.py
python demo.py --verify out/jep_archive.json
```

The script writes `out/audit.log` and `out/jep_archive.json`. The latter name and the old `verification_state: verified` marker are retained for compatibility; neither implies JEP Core validation. The output reports **local hash consistency**.

An author who can rewrite the archive can recompute every hash and pass these checks. Tail deletion cannot be detected against an absent trusted completeness anchor. This demo is an illustration of local data structure, not a signed JEP implementation.

For current signed events and actual syntax/signature checks, use [jep-quickstart](https://github.com/hjs-spec/jep-quickstart). The [Core 0.6 E2E repository](https://github.com/hjs-spec/jep-e2e-demo) remains a historical compatibility example.

[Migration provenance](../REPOSITORY-CONSOLIDATION-2026-09.md) identifies the source repository and revision.
