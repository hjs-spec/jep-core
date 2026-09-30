# Specification sources

Core semantics come from the applicable published Core specification. Profiles
own their additional rules. Conformance defines testing conventions. Schemas,
vectors, validators and reports are derived artifacts, not independent sources
of protocol requirements.

| Role | Current publication | Exact repository copy |
| --- | --- | --- |
| Core event semantics | [Core -07 / Core 0.7](https://datatracker.ietf.org/doc/html/draft-wang-jep-judgment-event-protocol-07), 2026-09-26 | [Frozen Core](../releases/draft-07/) |
| Profile contracts | [Profiles -01](https://datatracker.ietf.org/doc/html/draft-wang-jep-profiles-01), 2026-09-26 | [Frozen Profiles](../releases/profiles-01/) |
| Conformance conventions | [Conformance -02](https://datatracker.ietf.org/doc/html/draft-wang-jep-conformance-02), 2026-09-30 | [Frozen Conformance](../releases/conformance-02/) |

The [Core Editor's Copy](../draft-wang-jep-judgment-event-protocol.md) may evolve
for a later revision; do not substitute it silently for a published version.
Companion Markdown entries point to exact published files instead of maintaining
another abbreviated specification under the same draft number. The old
[repository seeds](historical/0.7-source-seeds/README.md) remain available as history.

Core release `0.7`, wire major `jep: "1"`, Internet-Draft revision `-07`,
validator package version and executable suite version are separate identifiers.
Conformance -02 includes an illustrative suite version; that example does not
establish that any particular executable release has been published.

Run `make repository-check` to verify immutable publication checksums and source
references. Every BYOI report identifies its actual executable suite version
and digest. A passing report covers the assertions exercised, not every possible
Core requirement, deployment or profile.
