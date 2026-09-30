# JEP Core Versioning and Repository Governance

## Stable identity

The repository `hjs-spec/jep-core` is the permanent repository identity for the JEP narrow-waist Core. Repository names do not track Internet-Draft revision numbers.

## Editor's Copy

`draft-wang-jep-judgment-event-protocol.md` on `main` is the current Editor's Copy.

The Editor's Copy may evolve after a publication. It MUST NOT be described as byte-identical to an earlier published revision unless it actually is.

## Published revisions

A published Internet-Draft revision is immutable.

For each published revision:

1. preserve the exact submitted/published artifact under `releases/draft-XX/`;
2. record its cryptographic checksum;
3. preserve the corresponding versioned source when available;
4. create an immutable Git tag such as `draft-07`;
5. never move or rewrite that tag;
6. place later corrections in the next draft revision.

## Wire version

Internet-Draft revision and wire major are different concepts.

JEP Core 0.7 retains:

```text
jep: "1"
```

A future draft number alone does not require a wire-major change. A future revision that breaks an adopted stable wire contract should define a new wire major.

## Companion specifications

Profiles, Conformance, Semantic Interoperability, chain composition, bindings, SDKs, runtimes, and applications are separate layers. Their versioning MUST NOT silently redefine JEP Core.

## Historical material

Pre-07 material remains available for migration and archival verification. Historical artifacts are not rewritten into JEP Core 0.7.

## Core feature stability

Core 0.7 remains the implementation target. Prioritize adoption and observable
interoperability issues before proposing new Core capability. Security findings,
normative contradictions and implementation bugs remain actionable. Published
snapshots are immutable; normative corrections belong in later drafts.

Companion publications also retain exact artifacts, checksums and provenance.
BYOI suite versions and assertion identifiers evolve independently of Core.
Never turn reference-implementation behavior into a new normative requirement.
