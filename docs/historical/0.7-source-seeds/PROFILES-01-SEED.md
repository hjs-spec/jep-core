# JEP Profiles
## Interoperability Profiles for JEP Core 0.7
### draft-wang-jep-profiles-01

Author: Yuqiang Wang  
Intended status: Experimental  
Companion draft: draft-wang-jep-judgment-event-protocol-07

---

## Abstract

This document defines how profiles extend JEP Core 0.7 without redefining
Core semantics. Profiles may specify actor/key binding, credential use,
algorithm policy, audience, freshness, challenge-response, archival,
attestation, or domain-specific validation requirements.

Profiles MUST NOT redefine Event Identity, J/D/T/V Core semantics, JCS
signing input, Event Hash meaning, or the substantive-neutrality boundary.

## 1. Profile Contract

A profile descriptor SHOULD declare:

- `profile_id`;
- name and version;
- `supported_jep_core: "0.7"`;
- actor identifier forms;
- key-resolution rules;
- algorithm policy;
- required validation checks;
- audience requirement;
- freshness/challenge policy;
- acceptance-domain rules;
- security considerations;
- privacy considerations.

Profiles MUST NOT express conformance in terms of cumulative Validation
Levels. They instead declare which independent checks are required.

## 2. Check Ownership

A profile may require or parameterize:

- `actor_binding`
- `freshness`
- `audience`

A chain profile may define `chain_integrity`.

A policy profile may define `policy`.

Profiles MUST NOT change the meaning of Core-defined checks:

- `syntax`
- `cryptographic`
- `event_identity`
- `reference_integrity`
- `extension_processing`

## 3. Identity and Key Binding

A trust profile MUST define how a signing key is resolved and how that key
is bound to `who`.

The signer and actor are not assumed to be the same entity.

If actor binding is required for acceptance, an implementation MUST NOT
commit authoritative Event Identity or acceptance state before the
actor-binding check passes.

Profiles may use DID, X.509, VC, OAuth/OIDC, RATS, enterprise directories,
or other systems. JEP Core requires none of them.

## 4. Freshness and Replay

JEP Core 0.7 does not require a nonce.

Profiles MAY require:

- receiver challenge;
- nonce;
- sequence number;
- trusted timestamp;
- short-lived audience-bound token;
- transaction identifier;
- monotonic counter;
- ledger position.

These mechanisms add profile-specific freshness, ordering, or single-use
properties. They do not replace stable Event Identity.

## 5. Audience

`aud` is optional in Core. A profile MAY require it.

A profile that uses `aud` MUST define matching rules and MUST NOT present
`aud` as access control by itself.

## 6. Reference and Chain Profiles

Logical references to JEP events SHOULD use Event Identity. Exact signed
artifacts MAY additionally be pinned with Event Hash.

Chain profiles may define reference resolution, delegation paths, cycle
analysis, termination cascade, complete-log assumptions, or authorization
consequences.

Those semantics remain outside JEP Core.

## 7. Archival Profiles

Archival profiles may define receipts, transparency anchors, timestamp
evidence, retention, disclosure, and historical algorithm policy.

Blockchain anchoring or transparency logs SHOULD anchor exact artifact
hashes when the intent is to bind one signed representation.

## 8. Profile Descriptor Example

```json
{
  "profile_id": "example.interactive-acceptance",
  "name": "Example Interactive Acceptance",
  "version": "1",
  "supported_jep_core": "0.7",
  "actor_identifier_forms": ["did"],
  "key_resolution": "profile-defined DID resolution",
  "algorithm_policy": ["Ed25519"],
  "required_checks": [
    "syntax",
    "cryptographic",
    "actor_binding",
    "event_identity",
    "freshness",
    "audience",
    "extension_processing"
  ],
  "audience_required": true,
  "freshness_policy": "receiver challenge required",
  "challenge_policy": "profile extension example.challenge",
  "acceptance_domain": "service-local"
}
```

## 9. Compatibility

Profiles written for JEP Core 0.6 MUST be revised before claiming 0.7
compatibility if they depend on:

- mandatory nonce;
- cumulative Validation Levels;
- Event Hash as event identity;
- Core chain enforcement;
- Core termination cascade.

A 0.6 profile MUST NOT be silently treated as a 0.7 profile.

## 10. IANA Considerations

This document requests no IANA actions.
