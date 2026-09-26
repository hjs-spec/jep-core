# Should JEP have a separate credential / receipt repository?

Status: implementation planning note, 2026-09-26. This document defines no new Core member, schema, signature algorithm, conformance class or credential standard.

## Decision for now

Keep one implementation home while defining a portable evidence use case. Do not create another repository solely because signed JEP events or reports are called “credentials”. The first implementation candidate is a separate bundle module in an existing SDK, with a runnable Quickstart example and reuse of the Core verifier. This is a proposal, not a claim that the module is implemented.

## Distinguish the objects

| Object | Existing boundary / proposed owner |
|---|---|
| Original signed JEP event | Core and its SDK/API; Event Identity is `(who,id)`, Event Hash binds the exact signed artifact |
| HTML/JSON report | Human-readable projection; the Agent SDK export does not itself establish independent verification |
| AIP sidecar receipt | Existing `aip-sidecar-receipt-0.2` prototype with its own envelope and canonicalization; not a universal JEP Core receipt |
| Portable evidence bundle | A prospective application/profile artifact collecting unchanged signed events, exact artifact digests, materials/references and explicit verification evidence |
| Identity credential / external signature certificate | External trust input with its own issuer, scope and validation; not supplied merely by calling an event a credential |
| Actual business records | Application-controlled storage and access policy; a public source repository is not the default storage location |

Core Profiles/01 explicitly leaves archival receipts, transparency anchors and timestamp evidence to archival profiles. Such a bundle must not turn optional companion functions into mandatory Core behavior or duplicate the signature validator.

## Minimum acceptance criteria before splitting a repository

1. Name the concrete artifact and version, independently of a rendered report.
2. Preserve original signed events and bind exact bytes/materials with a manifest; clearly distinguish Event Identity from Event Hash.
3. Verify through the existing Core implementation and an explicit key/trust configuration. Keys merely packaged with an event do not establish actor identity.
4. Report syntax, cryptographic integrity, material binding, actor/key binding and any time/receipt checks separately; unavailable evidence stays unresolved rather than becoming a pass.
5. Make an offline verification path work without the originating application's private database, and state which external trust/status data was needed and when it was obtained.
6. Cover tampering, missing evidence, wrong key, identity/content conflict, unsupported critical extensions, historical formats and unsafe archive paths.
7. Demonstrate reuse by two independently maintained consumers before adopting a separate release lifecycle. Independent implementation of the format remains a separate interoperability check.

Only then consider a dedicated `jep-evidence` implementation repository or a clearly scoped receipt profile. Any new profile needs its own specification and review; software packaging must not imply legal effect, certified identity, authority, trusted time, truthful content or universal third-party acceptance.

## Evidence reviewed

The current Core reference verifier, Agent SDK event verifier/exporter, API verification endpoints and AIP sidecar receipt implementation were inspected. The owner confirmed on 2026-09-26 that `hjs-spec/hjs-05` was intentionally deleted. This plan does not depend on or recreate that repository. HJS archival-profile concepts remain distinct from the existing JEP Core event and verification implementations.
