# JEP Conformance and Test Suite
## Schemas, Validation Results, Test Vectors, and Reference Validator Behavior
### draft-wang-jep-conformance-01

Author: Yuqiang Wang  
Intended status: Experimental  
Companion draft: draft-wang-jep-judgment-event-protocol-07

---

## Abstract

This document defines conformance classes, validation-result structure,
schema requirements, test-vector categories, reference-validator behavior,
and implementation testing guidance for JEP Core 0.7.

JEP Core 0.7 replaces cumulative validation levels with independent
validation checks, introduces stable Event Identity `(who,id)`, removes
mandatory Core nonce semantics, and defines idempotent acceptance. This
document makes those behaviors testable without moving trust, chain, policy,
or external-fact semantics into JEP Core.

---

## 1. Conformance Principle

Conformance means that an implementation processes JEP events according to
the declared Core version, validation mode, signature/conformance profile,
and requested checks.

Conformance does not establish substantive truth, authorization validity,
legal effect, causality, policy compliance, or external consequences.

Pre-0.7 artifacts MUST be handled by an explicitly selected legacy
compatibility path. A 0.7 validation failure MUST NOT trigger heuristic
fallback to 0.6 based only on field presence.

## 2. Conformance Classes

### 2.1 JEP-Core-0.7 Producer

A conforming producer MUST support:

- I-JSON-compatible JSON;
- stable event `id`;
- Core J/D/T/V field requirements;
- JCS canonicalization of the unsigned event;
- signature generation under at least one declared signature class;
- algorithm-tagged digests;
- `ext` and `ext_crit`.

A producer MUST NOT reuse one Event Identity for different unsigned event
content.

### 2.2 JEP-Core-0.7 Verifier

A conforming verifier MUST support:

- duplicate-member rejection;
- Core field validation;
- Event Identity validation;
- JCS canonicalization;
- signature verification under at least one declared signature class;
- Event Hash calculation;
- independent validation checks;
- structured `valid / invalid / indeterminate` results;
- unknown critical-extension rejection;
- archival validation mode.

### 2.3 JEP-Core-0.7 Acceptance Processor

A conforming acceptance processor MUST additionally support:

- an explicit acceptance domain;
- detection of conflicting Event Identity reuse;
- durable or equivalent acceptance state;
- atomic or equivalent first-acceptance processing;
- `accepted`, `already_accepted`, `rejected`, and `indeterminate`;
- separation of repeated valid delivery from invalid content.

Profiles MAY add freshness, audience, challenge-response, authorization, or
single-use-authority requirements.

### 2.4 JEP-Baseline-Ed25519-JWS-JCS-0.7

The repository baseline requires:

- JCS;
- detached compact JWS;
- Ed25519;
- algorithm-tagged SHA-256 digests.

This is one interoperability class, not a Core semantic requirement.

## 3. Independent Validation Checks

Core-defined checks:

- `syntax`
- `cryptographic`
- `event_identity`
- `reference_integrity`
- `extension_processing`

Trust- or acceptance-profile checks:

- `actor_binding`
- `freshness`
- `audience`

Companion/external checks:

- `chain_integrity`
- `policy`

Each check reports one of:

`pass`, `fail`, `not_checked`, `not_applicable`, `unsupported`,
or `indeterminate`.

An implementation MUST NOT report an unperformed check as `pass`.

## 4. Validation Result

Example archival result:

```json
{
  "status": "valid",
  "mode": "archival",
  "profile": "jep-core-0.7",
  "conformance_class": "JEP-Baseline-Ed25519-JWS-JCS-0.7",
  "event_identity": {
    "who": "did:example:actor",
    "id": "urn:uuid:..."
  },
  "event_hash": "sha256:...",
  "checks": {
    "syntax": "pass",
    "cryptographic": "pass",
    "event_identity": "pass",
    "reference_integrity": "not_checked",
    "extension_processing": "pass"
  },
  "warnings": [],
  "errors": []
}
```

Example repeated acceptance:

```json
{
  "status": "valid",
  "mode": "acceptance",
  "profile": "jep-core-0.7",
  "checks": {
    "syntax": "pass",
    "cryptographic": "pass",
    "event_identity": "pass"
  },
  "acceptance": {
    "outcome": "already_accepted",
    "effect_applied": false
  },
  "warnings": [],
  "errors": []
}
```

A duplicate delivery is not a cryptographic error.

## 5. Required Structural Tests

The 0.7 suite SHOULD include at least:

- valid J with stable `id`;
- valid D with `delegatee` and `scope`;
- valid T with `ref` and `termination_scope`;
- valid V with `ref`, `verification_scope`, and `result`;
- missing `id`;
- Event Identity conflict;
- V missing `result`;
- D missing `scope`;
- T missing `ref`;
- typed `jep:event` reference;
- exact-artifact hash mismatch;
- unknown critical extension;
- first acceptance;
- repeated acceptance;
- acceptance-state unavailable;
- actor-binding required and failed.

Nonce-specific replay vectors belong to a legacy 0.6 suite or to a profile
that explicitly defines nonce semantics.

## 6. Reference Validation Flow

```text
parse JSON
reject duplicate members
validate 0.7 Core shape
construct unsigned event
JCS canonicalize
verify signature
compute Event Hash
evaluate Event Identity consistency provisionally
run actor binding if requested
run audience/freshness if requested
run reference integrity if requested
process critical extensions
run companion chain/policy checks only if requested
if acceptance mode:
    atomically decide first acceptance
    return accepted or already_accepted
return structured validation result
```

When actor binding is required, authoritative Event Identity or acceptance
state MUST NOT be committed until actor binding passes.

## 7. Legacy Compatibility

The repository MAY keep a 0.6 validator and 0.6 vectors. They are legacy
compatibility assets, not the current Core definition.

Historical 0.6 signatures MUST NOT be rewritten or re-signed merely to
satisfy 0.7.

## 8. Security and Privacy

Test suites MUST include identity-conflict and concurrent-acceptance cases.

Test fixtures SHOULD use synthetic actors and non-production keys.

Conformance results MUST NOT be presented as proof of legal, factual, or
policy validity.

## 9. IANA Considerations

This document requests no IANA actions.
