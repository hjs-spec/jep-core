# JEP Core 0.7

JEP Core 0.7 corresponds to `draft-wang-jep-judgment-event-protocol-07`, published as an Internet-Draft on 2026-09-26.

## Core changes from 0.6

- Added required `id` and defined Event Identity as `(who, id)`.
- Separated stable Event Identity from Event Hash.
- Retained Event Hash as an exact signed-artifact digest.
- Removed mandatory top-level Core `nonce`.
- Defined safe retransmission through idempotent acceptance.
- Defined `accepted`, `already_accepted`, `rejected`, and `indeterminate` acceptance outcomes.
- Required atomic or equivalent first-acceptance processing.
- Made `aud` optional in Core and profile-required where needed.
- Clarified `when` as actor-declared event time rather than trusted time or freshness proof.
- Defined typed event references by Event Identity with optional exact-artifact pinning.
- Replaced cumulative Validation Levels with independent validation checks.
- Separated Core checks, trust/acceptance-profile checks, and companion/external checks.
- Moved chain enforcement, termination cascade, cycle analysis, complete-log evaluation, authorization consequences, and causal interpretation outside Core.
- Tightened the minimum J/D/T/V semantic matrix.
- Required a target, verification scope, and result for V events.
- Clarified the J/V boundary.
- Clarified substantive neutrality: JEP verifies protocol properties of signed statements without deciding substantive truth, authority, legality, causality, policy consequence, or external effect.
- Retained wire major `jep: "1"`; pre-07 Internet-Draft encodings remain historical development artifacts.

## Freeze rule

The published `-07` artifact is immutable. Corrections after publication are made in the next Internet-Draft revision.

Exact published RFCXML:
`releases/draft-07/draft-wang-jep-judgment-event-protocol-07.xml`

SHA-256:
`601809b4053d485fa68367db22f5e43919e859c4f0227609b8f851c627e9caab`

## Companion migration

The existing Conformance/00, Profiles/00, schemas, vectors, and validators originated against pre-07 semantics. They remain useful as historical and compatibility assets, but they are not automatically JEP Core 0.7 conformance definitions. Their migration is tracked separately.
