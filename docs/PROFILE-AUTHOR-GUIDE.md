# JEP Core 0.7 Profile Author Guide

Profiles add interoperability constraints without redefining Core.

## A profile should declare

- profile identifier and version;
- supported JEP Core version;
- actor identifier forms;
- signing-key resolution;
- actor/key binding;
- algorithm policy;
- required validation checks;
- audience rules;
- freshness/challenge rules;
- acceptance-domain rules;
- security considerations;
- privacy considerations.

## Use checks, not levels

Do not say that a profile "raises validation to Level 3" or similar.

Instead declare exact required checks, for example:

```json
{
  "required_checks": [
    "syntax",
    "cryptographic",
    "actor_binding",
    "event_identity",
    "freshness",
    "audience",
    "extension_processing"
  ]
}
```

## Do not redefine Core

A profile MUST NOT redefine:

- Event Identity `(who,id)`;
- Event Hash meaning;
- J/D/T/V Core semantics;
- JCS signing payload;
- Core check meanings;
- substantive-neutrality boundary.

## Replay / freshness

Core does not require a nonce. If a profile needs current liveness,
single-use authority, or ordering, specify the required mechanism
explicitly.

## Chain profiles

Chain profiles may define:

- reference resolution;
- delegation paths;
- termination cascade;
- cycle rules;
- complete-log assumptions;
- authorization consequences.

These remain companion semantics even when reported through
`chain_integrity`.

## Compatibility

A pre-0.7 profile is not automatically a 0.7 profile. Any dependency on
mandatory nonce, Validation Levels, Event Hash as event identity, or Core
chain effects requires an explicit revision.
