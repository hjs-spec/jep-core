# JEP Core 0.7 Implementer Guide

This guide describes the current JEP Core implementation path. For the
normative definition, use `draft-wang-jep-judgment-event-protocol-07`.

The [source map](SPECIFICATION-SOURCES.md) identifies exact published Core -07,
Profiles -01 and Conformance -02. After implementing your selected role, use the
[BYOI path](BYOI-CONFORMANCE.md) and [report guide](INTEROPERABILITY-REPORT.md).

## Produce

A Core 0.7 producer:

1. assigns a stable `id`;
2. sets `jep: "1"`;
3. sets `verb`, `who`, `when`, and `what`;
4. satisfies the verb-specific minimum:
   - J: judgment claim;
   - D: `what.delegatee` and `what.scope`;
   - T: `ref` and `what.termination_scope`;
   - V: `ref`, `what.verification_scope`, and `what.result`;
5. canonicalizes the unsigned event using JCS;
6. signs under a declared signature/conformance profile.

Core 0.7 does not require a top-level nonce.

## Identify

Event Identity is `(who,id)`.

Event Hash identifies one exact signed artifact. Do not use Event Hash as
the stable event identity.

A retransmission keeps the same Event Identity.

Reusing one Event Identity for different unsigned content is an
`ERR_EVENT_ID_CONFLICT`.

## Verify

Report independent checks rather than a highest Validation Level.

Core checks:
`syntax`, `cryptographic`, `event_identity`,
`reference_integrity`, `extension_processing`.

Profile checks:
`actor_binding`, `freshness`, `audience`.

Companion/external checks:
`chain_integrity`, `policy`.

## Accept safely

Delivery may be at-least-once. Acceptance effects are at-most-once per
Event Identity within an acceptance domain.

First valid acceptance:

```text
status = valid
acceptance.outcome = accepted
effect_applied = true
```

Safe retry:

```text
status = valid
acceptance.outcome = already_accepted
effect_applied = false
```

Identity conflict:

```text
status = invalid
ERR_EVENT_ID_CONFLICT
effect_applied = false
```

Recording first acceptance and applying the effect must be atomic or
equivalent.

## Freshness

Stable identity is not proof of liveness or freshness.

Interactive profiles may require challenge, nonce, audience, trusted time,
sequence number, transaction identifier, counter, or ledger position.

Those mechanisms belong to a profile or extension.

## Chain boundary

Core references do not create causal, authorization, or lifecycle
semantics by themselves.

Delegation-scope enforcement, termination cascade, cycle analysis,
complete-log assumptions, and policy effects belong to chain/profile
layers.

## Historical 0.6

Do not rewrite historical signed events.

Use the explicit legacy validator for pre-0.7 artifacts. Never attempt
0.7, observe failure, and silently retry 0.6 based only on field presence.
