# JEP Core 0.7: one-page overview

JEP is a compact signed event format for statements of Judgment (J), Delegation
(D), Termination (T) and Verification (V). It helps implementations exchange the
same event and report exactly which checks they performed.

| Concept | Core meaning |
| --- | --- |
| Event Identity `(who,id)` | Stable identity across delivery, export and re-verification |
| Event Hash | Identity of one exact signed artifact, not the stable event |
| Validation | Independent checks and `valid`, `invalid` or `indeterminate` |
| Acceptance | At-most-once effects per Event Identity within an acceptance domain |
| Profiles | Explicit additional trust, freshness, audience or domain requirements |

J/D/T/V have defined statement semantics. Their signatures do not establish
external truth, authorization validity, legal effect or an executed workflow.
Core requires no global identity system, runtime or mandatory nonce. Freshness
mechanisms and chain/lifecycle effects belong to the applicable companion layer.

## Illustrative event

```json
{
  "jep": "1",
  "id": "urn:uuid:00000000-0000-4000-8000-000000000001",
  "verb": "J",
  "who": "example:actor",
  "when": 1790726400,
  "what": {"claim": "approve-result"},
  "sig": "PLACEHOLDER_DETACHED_JWS"
}
```

This shape is not a signed test vector. Use the [BYOI fixtures and commands](BYOI-CONFORMANCE.md)
for executable examples and [published specifications](SPECIFICATION-SOURCES.md)
for requirements. Start implementation with the [implementer guide](IMPLEMENTER-GUIDE.md).

[Historical 0.6 overview](historical/0.6/ONE-PAGE-OVERVIEW.md).
