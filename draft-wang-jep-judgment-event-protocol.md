---
title: "Judgment Event Protocol (JEP)"
abbrev: "JEP"
docname: draft-wang-jep-judgment-event-protocol-07
category: exp
submissiontype: IETF
ipr: trust200902
date: 2026-09-26
keyword:
 - judgment
 - delegation
 - verification
 - accountability
 - AI agents

stand_alone: yes
smart_quotes: no
pi: [toc, sortrefs, symrefs]

author:
 -
    ins: Y. Wang
    name: Yuqiang Wang
    email: signal@humanjudgment.org
    uri: https://github.com/hjs-spec

normative:
  RFC6234:
  RFC7493:
  RFC7515:
  RFC8259:
  RFC8785:

informative:
  RFC8032:
  RFC9562:

...

--- abstract

This document defines the Judgment Event Protocol (JEP), a neutral
verifiable event format for judgment-related acts in human,
organizational, software, and autonomous agent systems.

JEP specifies four immutable event verbs: Judgment (J), Delegation (D),
Termination (T), and Verification (V). It defines a signed JSON event
structure, stable event identity, detached JSON Web Signature (JWS)
verification over JSON Canonicalization Scheme (JCS) canonicalized
payloads, signed-artifact hash and reference semantics, independent
validation checks, idempotent acceptance semantics, structured
validation results, extension handling, trust-profile interfaces, and
determinability boundaries.

JEP-Core defines protocol properties rather than mandating one replay
mechanism. In particular, JEP-Core does not require a top-level nonce.
An acceptance processor MUST prevent the same JEP event from applying
acceptance effects more than once within the same acceptance domain.
Profiles MAY additionally require nonces, challenges, sequence numbers,
trusted timestamps, ledger positions, or equivalent mechanisms.

JEP-Core does not define legal liability, authorization validity,
regulatory compliance, organizational trust decisions, global identity,
global truth, causal-chain enforcement, or mandatory support for any
specific credential, identity, AI platform, agent framework, transport,
or blockchain system.

--- middle

# Companion Drafts

This draft defines JEP-Core. Optional identity, credential, attestation,
chain, archival, mandate, and domain bindings are defined by companion
profiles and extensions.

Existing companion drafts written against JEP-Core 0.6 remain historical
documents until revised for JEP-Core 0.7. Where an earlier companion
draft conflicts with this document, this document controls JEP-Core 0.7
semantics.

Schemas, test vectors, validation-result structure, and reference
validator behavior for JEP-Core 0.7 are expected to be defined by a
matching conformance revision.

# Introduction

Autonomous and semi-autonomous systems increasingly make, assist with,
delegate, terminate, verify, or record judgments across organizational,
platform, model, and jurisdictional boundaries. These systems need a
minimal and interoperable way to record judgment-related acts so that
later verifiers can determine whether a particular event existed,
whether it was signed under an applicable trust profile, whether its
signed content changed, which event instance it represents, what it
references, and which verification checks were actually performed.

JEP addresses this need by defining a compact signed JSON event format.
The format is intentionally narrow. It records an event identifier, verb,
actor identifier, declared event time, claim or digest, optional audience,
optional references, extensions, and signature.

JEP separates event identity from signed-artifact identity:

- the event identity identifies the judgment-related act;
- the event hash identifies a particular full signed artifact.

JEP also separates event validity from acceptance effects. The same
valid event MAY be delivered repeatedly. Repeated delivery MUST NOT be
treated as a new event or cause the same acceptance effect to be applied
again within one acceptance domain.

More complex identity, credential, policy, archival, challenge-response,
causal-chain, and lifecycle semantics are externalized to profiles,
extensions, HJS-like archival layers, JAC-like chain-composition layers,
or application-specific systems.

JEP records verifiable protocol facts. It does not by itself prove
external target facts. In partially observed systems, a signed event log
can support audit and accountability workflows without guaranteeing
complete or zero-error determination of external facts.

# Protocol Objective and Non-Goals

# Objective

JEP-Core defines a neutral event layer for verifiable judgment-related
acts. Subject to the applicable validation mode and trust profile, a
conforming implementation can support determination that:

1. a specific event identity was asserted by an actor;
2. an event payload existed;
3. the event payload was signed as specified;
4. the signed payload was not modified without invalidating the
   signature;
5. the signer was or was not bound to the claimed actor under an
   applicable trust profile;
6. references, exact-artifact hashes, and critical extensions were
   processed according to the checks actually requested;
7. the verifier reports which checks passed, failed, were not performed,
   were unsupported, were not applicable, or were indeterminate;
8. an acceptance processor does not apply acceptance effects more than
   once for the same event identity within one acceptance domain.

# Non-Goals

JEP-Core does not define:

- legal liability;
- moral responsibility;
- regulatory compliance;
- global truth determination;
- external target-fact determinability;
- authorization delegation validity;
- permission-chain enforcement;
- lifecycle state-machine enforcement;
- termination cascade policy;
- a global identity framework;
- a global credential framework;
- a global trust framework;
- mandatory DID, VC, X.509, OAuth, RATS, blockchain, or AI-platform
  support;
- confidentiality for event content;
- long-term storage, redaction, retention, or disclosure policy;
- causal-chain or responsibility-graph computation;
- exactly-once network delivery;
- a mandatory challenge, nonce, counter, ledger, or transport mechanism.

A JEP event records claims about judgment-related acts. It MUST NOT be
presented as proof that an underlying real-world assertion is true unless
an applicable external profile and evidence policy makes that
determination.

# Design Principles

JEP-Core follows these principles:

1. **Core minimality:** JEP-Core defines the stable narrow-waist event
   layer.
2. **Property over mechanism:** JEP-Core defines required protocol
   properties without mandating a single replay, transport, storage, or
   challenge mechanism.
3. **Stable event identity:** event identity is a first-class protocol
   concept and is separate from signed-artifact hashing.
4. **Idempotent acceptance:** repeated delivery of the same event does
   not create a new event and MUST NOT repeatedly apply acceptance
   effects within one acceptance domain.
5. **Identity-system neutrality:** JEP-Core MUST NOT require a specific
   identity system.
6. **Credential-system neutrality:** JEP-Core MUST NOT require VC or any
   other credential model.
7. **Platform neutrality:** JEP-Core MUST NOT require an AI platform,
   agent framework, cloud provider, transport, or blockchain network.
8. **Profile-based interoperability:** identity, credentials,
   attestation, authorization, challenge-response, and archival policy
   are handled by optional profiles.
9. **Orthogonal verification:** syntax, cryptographic validity,
   actor-binding, freshness, audience, event identity, references,
   extensions, chain analysis, and policy evaluation are independent
   checks rather than cumulative quality levels.
10. **Explicit determinability boundary:** protocol validity is not the
    same as external truth.
11. **Privacy by minimization:** sensitive evidence SHOULD be referenced
    by digest or controlled evidence mechanisms rather than embedded in
    event payloads.
12. **Extension without semantic capture:** extensions MUST NOT redefine
    JEP-Core semantics.
13. **Algorithm agility:** cryptographic algorithms are selected by JOSE
    headers, conformance profiles, and trust profiles rather than by
    event verbs.
14. **Historical immutability:** historical signed events are verified
    under the rules that produced them and MUST NOT be silently rewritten
    into newer JEP representations.

# Requirements Language

{::boilerplate bcp14-tagged}

# Terminology

**Actor:** The entity identified by `who` that is claimed by the event.
An actor MAY be a human, organization, model, agent, tool, service,
device, workflow, committee, session, swarm, human-agent composite, or
organization-agent composite.

**Signer:** The key holder that produces the event signature. The signer
is not necessarily identical to the actor. The binding between signer and
actor is defined by a trust profile.

**Subject:** The entity or object about which a judgment, delegation,
termination, or verification is made. A subject is distinct from the
actor.

**Event:** A single immutable signed JSON object representing one
judgment-related act.

**Event ID:** The value of the top-level `id` member. An Event ID is an
opaque identifier chosen by the producer for one event instance.

**Event Identity:** The pair `(who, id)`. A producer MUST NOT reuse the
same Event Identity for different unsigned event content.

**Unsigned Event:** A JEP event object with the `sig` member omitted.

**JEP Signing Payload:** The UTF-8 octets of the JCS-canonicalized
unsigned event.

**Event Hash:** An algorithm-tagged digest over the full signed event,
including `sig`. The Event Hash identifies an exact signed artifact; it
is not the Event Identity.

**Acceptance Domain:** The local application, trust, or processing
context within which an event can produce a state-changing acceptance
effect. Independent systems MAY accept the same event independently.

**Acceptance Processor:** A component that, after applicable validation,
decides whether an event may apply an acceptance effect in an acceptance
domain.

**Idempotent Acceptance:** The requirement that the same Event Identity
MUST NOT apply acceptance effects more than once within one acceptance
domain.

**Claim:** Semantic content carried by `what` or by an extension.

**Reference:** A typed or cryptographic pointer to another event,
digest, credential, policy, evidence, context, archive receipt, or
external object.

**Exact Artifact Pin:** A reference that includes an Event Hash or other
digest in order to bind to an exact signed representation in addition to
logical identity.

**Trust Profile:** A profile that defines actor identifier forms,
signing-key resolution, actor/key binding, revocation, historical
validity, acceptable algorithms, and related evidence policy.

**Validation Check:** An independently reported verification operation,
for example `syntax`, `cryptographic`, `actor_binding`,
`freshness`, `audience`, `event_identity`,
`reference_integrity`, `extension_processing`, `chain_integrity`,
or `policy`.

**Validation Mode:** The context in which validation is performed, such
as `archival`, `acceptance`, `chain`, or `policy`.

**Verification Scope:** The declared scope of a V event, such as syntax,
cryptographic, actor-binding, chain-integrity, credential-status, policy
compliance, human review, external evidence, factual claim, or archival
integrity.

# Core Event Object

A JEP event is a JSON object {{!RFC8259}}. Producers MUST emit I-JSON-compatible JSON {{!RFC7493}}
and MUST NOT emit duplicate JSON member names. Verifiers MUST reject
events containing duplicate JSON member names.

The top-level members are:

| Member | Status | Description |
|---|---|---|
| `jep` | REQUIRED | Wire-format major version. For this draft, `"1"`. |
| `id` | REQUIRED | Opaque event identifier. Event Identity is `(who,id)`. |
| `verb` | REQUIRED | One of `"J"`, `"D"`, `"T"`, `"V"`. |
| `who` | REQUIRED | Actor identifier claimed by the event. |
| `when` | REQUIRED | Actor-declared event time, Unix seconds. |
| `what` | Conditional | Claim object, descriptor, or algorithm-tagged digest. |
| `aud` | OPTIONAL | Intended audience or validation context. |
| `ref` | Conditional | Typed reference or exact-artifact reference. |
| `ext` | OPTIONAL | Extension object. |
| `ext_crit` | OPTIONAL | Critical extension identifier list. |
| `sig` | REQUIRED | Detached signature container. |

JEP-Core 0.7 has no required top-level `nonce` member.

The top-level extensibility mechanism is `ext`. Producers SHOULD NOT add
new top-level members outside this specification unless defined by a
future JEP revision.

# Field Semantics

# `jep`

The `jep` member identifies the wire-format major version. For this
draft, the value is `"1"`.

`JEP-Core-0.7` identifies the specification release version. It is not
the wire-format version.

The `-06` and earlier Internet-Draft encodings were pre-stable
development artifacts and do not create a permanent wire-compatibility
contract for `jep: "1"`.

A verifier MUST NOT infer Internet-Draft revision number or release
maturity solely from `jep`.

# `id`

`id` identifies one event instance within the namespace of `who`.
Event Identity is the pair `(who, id)`.

The `id` value:

- MUST be a non-empty ASCII string;
- MUST be stable for the lifetime of the event;
- MUST be included in the signed payload;
- MUST NOT be reused by the same `who` for different unsigned event
  content;
- SHOULD be collision-resistant across independently generated events;
- MUST NOT be treated as a secret, bearer token, authorization grant, or
  proof of freshness.

UUID URNs {{?RFC9562}}, other collision-resistant URIs, or equivalent opaque
identifiers are suitable choices. JEP-Core does not require a specific
identifier-generation algorithm.

A producer SHOULD NOT derive `id` solely from the event's semantic
content when doing so could collapse two distinct event emissions with
identical content into one Event Identity.

If a verifier observes the same Event Identity with different
JCS-canonicalized unsigned event content, it MUST report
`ERR_EVENT_ID_CONFLICT`.

Re-signing an otherwise identical unsigned event MAY produce a different
Event Hash while retaining the same Event Identity.

# `verb`

The `verb` member identifies the event verb. It MUST be one of `J`,
`D`, `T`, or `V`.

Event verbs do not determine cryptographic algorithms, storage policy,
privacy mode, identity method, transport, or legal effect.

# `who`

`who` identifies the actor claimed by the event.

`who` is not necessarily:

- the signer;
- a legal person;
- the controller of the key;
- a real-world identity;
- the subject of the judgment.

The binding between `who` and the signing key is determined by the
applicable trust profile.

Because Event Identity includes `who`, two different actors MAY use the
same `id` string without creating the same Event Identity.

# `when`

`when` is an actor-declared event time in Unix seconds.

`when` does not by itself prove trusted wall-clock time, liveness, or
freshness. Stronger time evidence requires a timestamping, receipt,
archival, transparency, challenge-response, transport, or storage
profile.

Implementations SHOULD distinguish:

- declared event time;
- signature time;
- receipt time;
- archive time;
- verification time;
- acceptance time;
- policy-evaluation time.

An acceptance profile MAY define a permitted time window using `when`,
but such a window is a profile or deployment rule rather than proof that
`when` is externally accurate.

# `what`

`what` carries the event claim, digest, descriptor, or report. It
records what the actor asserted, judged, delegated, terminated, or
verified. It does not by itself prove external truth.

A J event MUST contain `what`.

A D event MUST contain an object-valued `what` that identifies at least
a delegatee and a scope, directly or through a profile-defined structure.

A T event MUST contain an object-valued `what` that identifies a
termination scope. The target of termination is identified by `ref`.
JEP-Core does not require duplication of the target inside `what`.

A V event MUST contain an object-valued `what` that declares a
verification scope.

Additional domain semantics belong to profiles or extensions.

When `what` is represented as a digest where permitted, the digest MUST
be an algorithm-tagged digest string.

# `aud`

`aud` indicates an intended audience or validation context.

`aud` is OPTIONAL in JEP-Core. A profile MAY require it, including for
interactive acceptance or cross-domain replay isolation.

`aud` does not by itself enforce access control. Access control,
retention, redaction, and disclosure policy are outside JEP-Core.

# `ref`

`ref` is a reference field. A reference does not by itself imply
endorsement, truth, authorization validity, legal effect, or causality.

References MAY identify:

- a JEP event;
- a digest;
- a credential;
- a policy;
- evidence;
- a context;
- an archive receipt;
- an external object.

A logical reference to another JEP event SHOULD use a typed reference:

```json
{
  "type": "jep:event",
  "value": {
    "who": "did:example:actor-123",
    "id": "urn:uuid:018f4f8d-7c63-7c2e-9b43-4ef657eec1c0"
  }
}
```

An exact signed artifact MAY additionally be pinned:

```json
{
  "type": "jep:event",
  "value": {
    "who": "did:example:actor-123",
    "id": "urn:uuid:018f4f8d-7c63-7c2e-9b43-4ef657eec1c0"
  },
  "hash": "sha256:..."
}
```

The `value` identifies the event. The optional `hash` identifies one
exact signed artifact for that event.

A bare Event Hash MAY be used when an application intentionally refers
only to an exact signed artifact, but it MUST NOT be described as the
stable Event Identity.

# `ext` and `ext_crit`

`ext` contains named extension objects. `ext_crit` contains the
identifiers of critical extensions.

Unknown critical extensions MUST cause the applicable
`extension_processing` check to fail. Unknown non-critical extensions
MAY be ignored.

Profiles that require a nonce, challenge, sequence number, transaction
identifier, ledger position, or similar mechanism SHOULD carry that
mechanism in a registered extension or transport/profile layer rather
than redefining JEP-Core fields.

# `sig`

`sig` carries the detached signature container. JEP-Core uses detached
JWS over the JCS-canonicalized unsigned event unless another registered
signature profile applies.

# Event Verb Semantics

# J — Judgment

A Judgment event records that an actor made, accepted, produced,
approved, selected, rejected, ranked, classified, or otherwise committed
to a judgment-related claim.

A J event MUST NOT be interpreted as proof that the judged claim is true.

Typical uses include:

- model output approval;
- human approval;
- risk classification;
- tool-selection decision;
- policy decision;
- recommendation acceptance;
- evidence assessment.

# D — Delegation

A Delegation event records that an actor declared a delegation of a task,
authority, responsibility, capability, or judgment context to another
actor or system.

A D event MUST identify a delegatee and scope. It MAY identify:

- constraints;
- expiry;
- context;
- termination conditions;
- related evidence or policy references.

A D event records a delegation claim. It does not by itself prove legal,
organizational, or technical authority to delegate.

Permission-chain enforcement and downstream authorization are outside
JEP-Core.

# T — Termination

A Termination event records that an actor declared a previous
delegation, authority, session, capability, workflow context,
verification context, or future-reliance relationship ended, revoked,
expired, superseded, or no longer valid for a stated termination scope.

A T event MUST identify its target through `ref` and MUST declare a
termination scope.

A T event does not delete historical events, erase past facts,
retroactively invalidate an event, or by itself prove that all downstream
systems stopped relying on the target.

Cascade semantics, downstream effects, authority consequences, and
lifecycle enforcement are defined by chain, mandate, domain, or policy
profiles.

# V — Verification

A Verification event records that an actor performed a validation, audit,
review, confirmation, rejection, or verification action over an event,
digest, subject, credential, policy, evidence, chain result, or external
object.

A V event MUST identify its verification target through `ref` and MUST
declare its verification scope. A V event MUST NOT imply verification
beyond its declared scope.

Initial verification scopes include:

- `syntax`;
- `cryptographic`;
- `actor_binding`;
- `freshness`;
- `audience`;
- `event_identity`;
- `reference_integrity`;
- `extension_processing`;
- `chain_integrity`;
- `credential_status`;
- `policy_compliance`;
- `human_review`;
- `external_evidence`;
- `factual_claim`;
- `archival_integrity`.

# Event Identity, Delivery, and Acceptance

# Event Identity

The Event Identity is `(who, id)`.

The same Event Identity represents the same JEP event instance across
retransmission, storage, export, and re-verification.

The same Event Identity MUST NOT identify different unsigned event
content.

A verifier that maintains identity state SHOULD retain, for each observed
Event Identity, a digest of the JEP Signing Payload or an equivalent
collision-resistant representation sufficient to detect conflicting
reuse.

# Delivery Is Not Event Creation

Network delivery, queue delivery, storage import, export, retry, or
replication of an existing signed event does not create a new JEP event.

A sender MAY retransmit the same event when delivery outcome is unknown.

A receiver MUST NOT require a new JEP Event Identity merely because a
transport retry occurs.

# Idempotent Acceptance

An acceptance processor MUST NOT apply acceptance effects more than once
for the same Event Identity within one acceptance domain.

A conforming acceptance processor MUST distinguish at least:

- `accepted`: the event is valid for the requested acceptance context
  and its acceptance effect is being applied for the first time;
- `already_accepted`: the event is valid for the requested acceptance
  context but the same Event Identity has already applied its acceptance
  effect;
- `rejected`: one or more required validation checks failed;
- `indeterminate`: a required acceptance determination could not be
  completed.

`already_accepted` is not a cryptographic validation failure.

If the same Event Identity is presented with different unsigned event
content, the event MUST be rejected with `ERR_EVENT_ID_CONFLICT`.

# Atomicity

The operation that records first acceptance and the operation that
applies its state-changing acceptance effect MUST be atomic or provide an
equivalent concurrency guarantee.

An implementation MUST NOT perform:

```text
check unseen
apply effect
mark seen
```

as independent raceable operations.

Database uniqueness constraints, transactional insertion, durable
compare-and-set, ledger consumption, or equivalent mechanisms are
suitable approaches.

# Acceptance-State Lifetime

An implementation claiming at-most-once acceptance MUST preserve enough
acceptance state to prevent reapplication for as long as the event
remains eligible to produce that acceptance effect.

A profile MAY define a bounded acceptance window. If no bounded window
exists, acceptance state may need to persist for the lifetime of the
effect or dependent state.

Archival verification MUST NOT consume acceptance state.

# Optional Challenge and Replay Profiles

JEP-Core does not require a nonce.

Profiles MAY additionally require:

- receiver-issued nonces;
- sender-generated nonces;
- challenge-response;
- sequence numbers;
- transaction identifiers;
- trusted timestamps;
- short-lived audience-bound tokens;
- monotonic counters;
- ledger positions;
- previous-event commitments.

Such mechanisms MAY establish properties that stable Event Identity alone
does not establish, including current liveness, server challenge
freshness, total order, or single-use authority.

# References and Chain Boundaries

A JEP reference proves only that one signed event referenced another
object. It does not prove causality, endorsement, truth, authorization,
completeness, or legal consequence.

A typed event reference identifies an event through Event Identity. An
optional artifact hash additionally pins a particular signed
representation.

If an exact-artifact hash is present, a verifier performing
`reference_integrity` MUST verify the hash against the resolved signed
artifact.

Chain reconstruction, delegation-scope enforcement, termination cascade,
cycle analysis, complete-log assumptions, responsibility graphs, and
causal interpretation are outside JEP-Core and belong to JAC-like chain
profiles or application-specific systems.

A chain system MUST NOT reinterpret a JEP Event Hash as the stable Event
Identity.

# Algorithm-Tagged Digest Strings

JEP uses algorithm-tagged digest strings for Event Hashes, content
digests, exact-artifact pins, and other digest references.

Syntax:

```text
<hash-algorithm>:<lowercase-hex-digest>
```

The hash algorithm identifier MUST be lower-case ASCII. The digest value
MUST be lower-case hexadecimal.

Implementations conforming to the JEP-Core 0.7 baseline MUST support
`sha256` as specified for SHA-256 in {{!RFC6234}}.

Example:

```text
sha256:3a6eb0790f39ac87c94f3856b2dd2c5d110e6811602261a9a923d3bb23adc8b7
```

Additional digest algorithms MAY be defined by conformance profiles,
trust profiles, or registered extensions.

# Signing Input and Event Hash

The JEP Signing Payload is the unsigned event object with `sig` omitted,
canonicalized using JCS {{!RFC8785}} and encoded as UTF-8 octets.

The Event Hash identifies the full signed event object, including `sig`.

For the default hash profile:

```text
event_hash = sha256(UTF8(JCS(full_signed_event)))
```

The Event Identity, signing payload, and Event Hash are intentionally
different:

- Event Identity is `(who, id)`;
- signing payload excludes `sig`;
- Event Hash includes `sig`.

A different valid signature representation over otherwise identical
unsigned event content MAY result in a different Event Hash without
creating a different Event Identity.

# Signature, Hash, and Algorithm Agility

JEP-Core preserves algorithm agility.

A JEP event is protected by a detached JWS signature {{!RFC7515}} over a
JCS-canonicalized unsigned event payload.

JEP-Core does not assign cryptographic algorithms to event verbs. J, D,
T, and V share the same cryptographic processing model.

The concrete signature algorithm, key type, hash algorithm, and algorithm
acceptability policy are determined by JOSE headers, conformance
profiles, and trust profiles.

A baseline conformance class MAY define a required-to-implement
algorithm set for interoperability. Ed25519 {{?RFC8032}} is one possible
baseline signature algorithm. Such a conformance class does not
make one algorithm the only algorithm allowed by JEP-Core semantics.

A trust profile MUST define which algorithms are acceptable for its
deployment context.

A verifier MUST reject an event if the declared algorithm is unsupported,
prohibited by the applicable profile, inconsistent with the resolved key
type, inconsistent with the signature container, or inconsistent with a
critical cryptographic extension.

A verifier SHOULD distinguish real-time acceptance validation from
archival validation. An algorithm MAY be acceptable for historical
verification while being prohibited for newly produced events.

# Trust Profile Interface

JEP-Core does not define a global identity or trust framework.

A trust profile MUST define, where applicable:

- supported actor identifier forms;
- key identifier syntax and discovery;
- binding rules between `who` and signing keys;
- accepted signature algorithms;
- downgrade policy;
- key rotation handling;
- revocation handling;
- historical key validity;
- credential or attestation use;
- audience requirements;
- freshness requirements;
- challenge-response requirements;
- acceptance-domain rules;
- policy evaluation hooks.

Support for DID, VC, X.509, OAuth, RATS, blockchain anchoring, or any
specific identity system is OPTIONAL and MUST NOT be required for
JEP-Core conformance.

# Validation Model

# Independent Validation Checks

JEP-Core does not define cumulative validation levels.

A verifier reports independent checks. Initial check identifiers include:

- `syntax`;
- `cryptographic`;
- `actor_binding`;
- `freshness`;
- `audience`;
- `event_identity`;
- `reference_integrity`;
- `extension_processing`;
- `chain_integrity`;
- `policy`.

A check status is one of:

- `pass`;
- `fail`;
- `not_checked`;
- `not_applicable`;
- `unsupported`;
- `indeterminate`.

`unsupported` means the verifier does not implement the requested
check or profile.

`indeterminate` means the verifier implements the check but cannot
complete it from the available evidence or state.

A verifier MUST NOT report an unperformed check as `pass`.

# Overall Validation Status

The overall validation status is one of:

- `valid`;
- `invalid`;
- `indeterminate`.

For a requested mode and profile:

- `valid` means all required checks passed or were not applicable;
- `invalid` means at least one required check failed;
- `indeterminate` means no required check failed, but at least one
  required check is unsupported or indeterminate.

Checks not required by the requested mode or profile MAY be
`not_checked`.

# Validation Modes

Initial validation modes are:

- `archival`;
- `acceptance`;
- `chain`;
- `policy`.

Archival validation is repeatable and MUST NOT consume acceptance state.

Acceptance validation includes JEP-Core event-identity checks and
idempotent acceptance semantics plus any freshness, audience,
actor-binding, or challenge requirements declared by the applicable
profile.

Chain mode invokes a companion chain profile or chain system. JEP-Core
does not define chain-integrity semantics.

Policy mode invokes a domain, organizational, legal, regulatory, or
deployment policy. Policy results MUST NOT be presented as intrinsic
properties of JEP-Core.

# Deterministic Core Validation Order

A JEP-Core verifier SHOULD process an event in this order:

1. parse JSON;
2. reject duplicate JSON member names;
3. check required top-level fields;
4. validate `jep`, `id`, `verb`, `who`, and `when`;
5. check verb-specific core field requirements;
6. remove `sig` to construct the unsigned event;
7. canonicalize the unsigned event using JCS;
8. verify the detached signature;
9. compute the Event Hash if needed;
10. evaluate Event Identity consistency if identity state is available;
11. resolve actor/key and actor binding if required;
12. validate audience if required by the requested profile;
13. evaluate freshness if required by the requested profile;
14. validate reference syntax and exact-artifact pins if requested;
15. process critical extensions;
16. invoke optional chain checks if requested;
17. invoke optional policy checks if requested;
18. if acceptance mode is requested, atomically determine and record the
    acceptance outcome;
19. return a structured validation result.

An implementation MUST perform cryptographic validation before writing
new acceptance state for an untrusted input. Deployments SHOULD bound
acceptance-state resource use according to their trust, audience, retention,
and abuse-control policy.

# Validation Result Object

A verifier SHOULD return a structured validation result.

Example for first acceptance:

```json
{
  "status": "valid",
  "mode": "acceptance",
  "profile": "jep-core-0.7",
  "event_identity": {
    "who": "did:example:agent-789",
    "id": "urn:uuid:018f4f8d-7c63-7c2e-9b43-4ef657eec1c0"
  },
  "event_hash": "sha256:...",
  "checks": {
    "syntax": "pass",
    "cryptographic": "pass",
    "actor_binding": "not_checked",
    "freshness": "pass",
    "audience": "pass",
    "event_identity": "pass",
    "reference_integrity": "not_applicable",
    "extension_processing": "pass",
    "chain_integrity": "not_checked",
    "policy": "not_checked"
  },
  "acceptance": {
    "outcome": "accepted",
    "effect_applied": true
  },
  "warnings": [],
  "errors": []
}
```

Example for safe retry:

```json
{
  "status": "valid",
  "mode": "acceptance",
  "profile": "jep-core-0.7",
  "event_identity": {
    "who": "did:example:agent-789",
    "id": "urn:uuid:018f4f8d-7c63-7c2e-9b43-4ef657eec1c0"
  },
  "event_hash": "sha256:...",
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

A validation result MUST distinguish:

- invalid from indeterminate;
- cryptographic validity from actor binding;
- historical validity from current acceptance eligibility;
- event identity from exact signed-artifact identity;
- a repeated valid event from a conflicting reuse of an Event Identity;
- chain analysis from JEP-Core validity;
- policy outcome from JEP-Core validity.

# Failure Codes

A conforming validator SHOULD return structured failure codes.

# Syntax and Identity Errors

- `ERR_INVALID_JSON`
- `ERR_DUPLICATE_MEMBER`
- `ERR_UNSUPPORTED_JEP_VERSION`
- `ERR_UNKNOWN_VERB`
- `ERR_MISSING_REQUIRED_FIELD`
- `ERR_INVALID_FIELD_TYPE`
- `ERR_INVALID_TIMESTAMP`
- `ERR_EVENT_ID_INVALID`
- `ERR_EVENT_ID_CONFLICT`

# Cryptographic Errors

- `ERR_CANONICALIZATION_FAILED`
- `ERR_CANONICALIZATION_VERSION_UNSUPPORTED`
- `ERR_INVALID_EVENT_HASH`
- `ERR_UNSUPPORTED_SIGNATURE_ALG`
- `ERR_PROHIBITED_SIGNATURE_ALG`
- `ERR_ALG_KEY_TYPE_MISMATCH`
- `ERR_ALG_PROFILE_MISMATCH`
- `ERR_HASH_ALG_UNSUPPORTED`
- `ERR_SIGNATURE_CONTAINER_INVALID`
- `ERR_SIGNATURE_MISSING`
- `ERR_SIGNATURE_INVALID`
- `ERR_DIGEST_MISMATCH`
- `ERR_ARCHIVAL_ALG_STATUS_UNKNOWN`
- `ERR_ALG_DEPRECATED_FOR_NEW_EVENTS`

# Actor and Trust Errors

- `ERR_ACTOR_UNRESOLVED`
- `ERR_KEY_UNRESOLVED`
- `ERR_KEY_NOT_BOUND_TO_ACTOR`
- `ERR_KEY_REVOKED`
- `ERR_KEY_NOT_VALID_AT_EVENT_TIME`
- `ERR_TRUST_PROFILE_UNSUPPORTED`

# Freshness and Acceptance Errors

- `ERR_EVENT_EXPIRED`
- `ERR_TIMESTAMP_OUT_OF_WINDOW`
- `ERR_ACCEPTANCE_STATE_UNAVAILABLE`
- `ERR_ACCEPTANCE_ATOMICITY_UNAVAILABLE`

`already_accepted` is an acceptance outcome, not an error code.

# Reference Errors

- `ERR_REF_UNRESOLVED`
- `ERR_REF_HASH_MISMATCH`
- `ERR_REF_IDENTITY_MISMATCH`

Chain-specific failure codes, including delegation-scope, termination
cascade, cycle, and complete-log failures, belong to the applicable
chain profile rather than JEP-Core.

# Extension Errors

- `ERR_UNKNOWN_CRITICAL_EXTENSION`
- `ERR_EXTENSION_SCHEMA_INVALID`
- `ERR_EXTENSION_VALIDATION_FAILED`
- `ERR_EXTENSION_CONFLICT`

# Policy Errors

- `ERR_POLICY_REJECTED`
- `ERR_AUTHORIZATION_CONTEXT_MISSING`
- `ERR_DOMAIN_REQUIREMENT_UNSATISFIED`

# Extension Rules and Conflict Handling

An extension MUST declare:

1. extension identifier;
2. extension version;
3. JSON schema or equivalent data model;
4. whether it may be critical;
5. validation requirements;
6. security considerations;
7. privacy considerations;
8. interaction with Event Identity, Event Hashes, and signatures;
9. interaction with other known extensions, if applicable.

Extensions MUST NOT redefine the semantics of core JEP members.

Unknown critical extensions MUST cause the
`extension_processing` check to fail. Unknown non-critical extensions
MAY be ignored.

If two critical extensions impose inconsistent requirements, validation
MUST fail with `ERR_EXTENSION_CONFLICT`.

Extension identifiers SHOULD be collision-resistant. Supported forms
include:

- reverse-DNS identifiers;
- URI identifiers;
- registered short names;
- experimental `x-*` identifiers.

# Conformance Requirements

# Producer Conformance

A JEP-Core-0.7 producer MUST support:

- I-JSON-compatible event construction;
- generation or assignment of a stable `id`;
- required top-level fields;
- JCS canonicalization of unsigned payloads;
- detached JWS signature generation under at least one conformance class;
- algorithm-tagged digest strings;
- `ext` and `ext_crit` semantics.

A producer MUST NOT reuse one Event Identity for different unsigned event
content.

# Verifier Conformance

A JEP-Core-0.7 verifier MUST support:

- duplicate-member rejection;
- core field validation;
- Event Identity validation;
- JCS canonicalization;
- detached signature verification under at least one conformance class;
- Event Hash calculation;
- independent validation checks;
- structured validation result objects;
- unknown critical extension rejection;
- archival validation mode.

A verifier MUST NOT require support for any optional identity,
credential, attestation, blockchain, AI platform, agent framework,
challenge, transport, or chain profile.

# Acceptance-Processor Conformance

An implementation claiming JEP-Core-0.7 acceptance-processor conformance
MUST additionally support:

- stable acceptance-domain definition;
- detection of conflicting Event Identity reuse;
- durable or otherwise sufficient acceptance state;
- atomic or equivalent first-acceptance processing;
- `accepted`, `already_accepted`, `rejected`, and
  `indeterminate` outcomes;
- separation between repeated valid delivery and invalid event content.

A profile MAY add freshness, audience, challenge-response, authorization,
or single-use-authority requirements.

# Baseline Algorithm Conformance

A baseline conformance class MAY require detached JWS using JCS
canonicalization, `sha256` algorithm-tagged digest strings, and Ed25519
verification.

This baseline is a conformance-class requirement, not a JEP-Core semantic
requirement. Other profiles MAY define additional or alternative
algorithm suites, including regional, enterprise, COSE/CBOR, composite,
or post-quantum profiles, provided that their identifiers, key
representations, downgrade policies, and validation behavior are
specified.

# Determinability Boundary

JEP distinguishes observable protocol facts from external target facts.

# Observable Protocol Facts

JEP can support determination of protocol-level facts such as:

- whether an Event Identity was asserted in a signed event;
- whether an unsigned payload was signed by a key;
- whether a key is acceptable under a trust profile;
- whether an Event Hash matches an exact signed artifact;
- whether an event references another Event Identity;
- whether an exact-artifact pin matches the resolved artifact;
- whether the same Event Identity was already accepted in one acceptance
  domain;
- whether a critical extension was processed;
- which validation checks were actually performed.

# External Target Facts

JEP alone does not determine external target facts such as:

- whether a real-world statement is true;
- whether a model internally understood a request;
- whether an actor is legally liable;
- whether a delegation is legally enforceable;
- whether a human actually read a document;
- whether a physical-world action occurred outside the logged system;
- whether all downstream systems honored a Termination event;
- whether an observed event log is complete.

A profile MAY define evidence rules for external target facts. Such rules
are outside JEP-Core.

# Observed Log Assumptions

An observed JEP log is not necessarily a complete log.

Absence of an event in an observed log MUST NOT be interpreted as proof
that the event did not occur unless a complete-log assumption is
explicitly declared by a deployment or chain profile.

Profiles MAY define:

- complete-log profiles;
- partial-log profiles;
- selective-disclosure logs;
- redacted logs;
- archive-backed logs;
- transparency-backed logs.

A chain reconstruction result MUST declare whether it relies on complete
or partial log assumptions.

JEP-Core does not itself compute chain completeness, termination cascade,
or responsibility lineage.

# Relationship to HJS and JAC

JEP defines atomic signed judgment-related events.

HJS-like systems manage storage, receipt, archival context, retention,
redaction, selective disclosure, privacy policy, and evidence lifecycle
for JEP events. Such systems MUST NOT redefine JEP-Core Event Identity,
signature semantics, Event Hash semantics, or validation-check meanings.

JAC-like systems compose JEP events into causality chains,
responsibility chains, delegation paths, verification paths, and
workflow accountability graphs. Such systems MUST NOT redefine JEP-Core
event format, Event Identity, signature semantics, or Event Hash
semantics.

A JEP reference does not by itself imply causality. Causal,
authorization, lifecycle, and termination-cascade interpretations are
defined by JAC or another chain/profile layer.

# Security Considerations

JEP-Core provides mechanisms and invariants for:

- payload integrity;
- signature verification under supported algorithms;
- stable event identity;
- detection of conflicting Event Identity reuse;
- exact-artifact hash verification;
- critical-extension processing;
- idempotent acceptance within a declared acceptance domain.

JEP-Core does not by itself prevent:

- compromised signing keys;
- false claims signed by legitimate actors;
- omission of relevant events from a log;
- collusion among actors;
- legal or organizational misuse;
- incorrect external evidence;
- malicious trust profiles;
- timestamp manipulation without external time evidence;
- cross-domain acceptance when no audience/profile rule forbids it;
- replay against an implementation that does not claim acceptance
  conformance;
- repeated authority consumption when the applicable authority profile
  requires stronger single-use semantics than event acceptance.

# Event ID Security

`id` is not a secret and MUST NOT be used as an authorization token.

Because Event Identity is `(who,id)`, deliberate use of another actor's
`id` string does not create the same Event Identity.

A validly signed actor MUST NOT reuse its own Event Identity for different
unsigned event content. Verifiers with identity state MUST detect such
reuse as `ERR_EVENT_ID_CONFLICT`.

Predictable Event IDs do not weaken signature integrity, but they may
increase correlation or enumeration risk in systems that expose lookup
interfaces. Profiles MAY impose stronger identifier-generation rules.

# Replay and Safe Retry

A copied, unmodified signed event can remain cryptographically valid.
Signature validity alone therefore does not prevent repeated delivery.

JEP-Core addresses duplicate acceptance through stable Event Identity and
idempotent acceptance. A valid retry yields `already_accepted` rather
than a second state-changing effect.

Applications requiring proof of current liveness, server challenge
freshness, strict request ordering, or single-use authority SHOULD use an
appropriate challenge, nonce, sequence, timestamp, counter, reservation,
or ledger profile in addition to JEP-Core.

# Acceptance-State Failure

If an implementation cannot reliably determine whether an Event Identity
was already accepted, it MUST NOT claim a fresh `accepted` outcome.

If required acceptance state or atomicity guarantees are unavailable, the
result MUST be `indeterminate` or rejected according to the applicable
profile.

# Downgrade Resistance

A verifier MUST reject algorithms prohibited by the applicable profile. A
verifier MUST NOT accept a weaker algorithm merely because it is
syntactically valid in JOSE.

# Human-in-the-Loop Semantics

A human-review event records that a human actor emitted or endorsed a
review-related claim. It does not prove that the human fully understood
the underlying material, that the judgment was correct, or that legal
compliance was satisfied.

# AI Actor Semantics

JEP-Core does not mandate any specific AI actor identity scheme. AI
actor identity, model identity, tool identity, service identity, and
session identity are defined by trust profiles or extensions.

# Privacy Considerations

JEP events may reveal actor identity, event identity, subject identity,
judgment timing, delegation structure, organizational workflow, tool
usage, and audit relationships.

Deployments SHOULD minimize personal data in `what` and extensions.
When possible, external evidence SHOULD be referenced by digest rather
than embedded directly.

Event IDs and Event Hashes may enable correlation across exports or
systems. Deployments SHOULD avoid stable cross-context identifiers when
they are not required by the trust or interoperability model.

Digest references may enable correlation, confirmation attacks, or
dictionary attacks. Sensitive evidence references MAY require salted
digests, commitment schemes, access-controlled evidence stores,
audience-bound references, selective disclosure, or redaction.

JEP signatures and references may create linkability across contexts.
Implementations SHOULD avoid reusing actor identifiers across unrelated
audiences unless required by the trust profile.

JEP is an accountability protocol component. It SHOULD NOT be deployed as
a general monitoring mechanism without data-minimization, retention,
access-control, and redaction policies.

# Registry Considerations

JEP registries SHOULD cover:

- verbs;
- extension identifiers;
- verification scopes;
- validation modes;
- validation-check identifiers;
- check-status values;
- acceptance outcomes;
- error codes;
- trust profile identifiers;
- conformance class identifiers;
- algorithm policy labels.

New verb registrations are NOT RECOMMENDED. New verbs require an update
to JEP-Core explaining why existing verbs plus extensions are
insufficient.

# Versioning and Compatibility

# Wire Version

For JEP-Core 0.7, `jep` remains `"1"`.

The `-06` and earlier Internet-Draft encodings are pre-stable draft
artifacts. Their use of `jep: "1"` does not require JEP-Core 0.7 to
preserve their field set.

# Historical Verification

Implementations MAY retain historical pre-`-07` decoders.

Historical signed events MUST NOT be rewritten, re-signed, or silently
upgraded merely to satisfy JEP-Core 0.7.

A historical decoder MUST be selected explicitly through a named
compatibility mode, known artifact context, archive metadata, or other
non-heuristic mechanism.

An implementation MUST NOT:

1. attempt JEP-Core 0.7 validation;
2. observe failure;
3. silently retry as JEP-Core 0.6 based only on field presence.

# Future Compatibility

Future revisions MAY add optional fields or extensions without changing
the wire major when the core event object remains compatible.

A future revision that changes stable Event Identity semantics, signing
input semantics, canonicalization requirements, or required Core fields
after real-world `jep: "1"` adoption SHOULD define a new wire major.

Unknown critical extensions MUST fail the
`extension_processing` check. Unknown non-critical extensions MAY be
ignored.

# Examples

# Minimal Judgment Event Shape

```json
{
  "jep": "1",
  "id": "urn:uuid:018f4f8d-7c63-7c2e-9b43-4ef657eec1c0",
  "verb": "J",
  "who": "did:example:agent-789",
  "when": 1742345678,
  "what": "sha256:aa55ad4393538f14e6b4961de1a29216eed93517cb6c2631a56a5ee75edb3b7a",
  "sig": "..."
}
```

# Judgment Event with Audience and Event Reference

```json
{
  "jep": "1",
  "id": "urn:uuid:018f4f8d-8ad2-7baf-b752-e529e79bc88a",
  "verb": "J",
  "who": "did:example:agent-789",
  "when": 1742345700,
  "what": {
    "claim": "approve-result",
    "subject": "urn:example:result:42"
  },
  "aud": "https://platform.example.com",
  "ref": {
    "type": "jep:event",
    "value": {
      "who": "did:example:agent-123",
      "id": "urn:uuid:018f4f8d-7c63-7c2e-9b43-4ef657eec1c0"
    },
    "hash": "sha256:..."
  },
  "sig": "..."
}
```

Full signed test vectors belong in the matching conformance revision.

# Changes from -06

Major changes from `draft-wang-jep-judgment-event-protocol-06`:

- Retained `jep: "1"` and clarified that pre-`-07` Internet-Draft
  encodings were pre-stable development artifacts.
- Added required `id` and defined stable Event Identity as `(who,id)`.
- Separated stable Event Identity from Event Hash.
- Kept Event Hash as the digest of the full signed artifact.
- Removed the required top-level `nonce` from JEP-Core.
- Replaced nonce-specific replay semantics with idempotent acceptance.
- Defined `accepted`, `already_accepted`, `rejected`, and
  `indeterminate` acceptance outcomes.
- Required atomic or equivalent first-acceptance processing.
- Defined conflicting Event Identity reuse as
  `ERR_EVENT_ID_CONFLICT`.
- Made `aud` OPTIONAL in Core and profile-required where appropriate.
- Clarified that `when` is declared event time, not trusted time or
  proof of freshness.
- Defined typed event references in terms of Event Identity.
- Allowed optional exact signed-artifact pinning with Event Hash.
- Replaced cumulative Validation Levels 0-4 with independent validation
  checks and explicit check statuses.
- Added overall `valid`, `invalid`, and `indeterminate` result
  states.
- Moved delegation-scope enforcement, termination cascade, cycle
  detection, complete-log evaluation, and causal interpretation out of
  JEP-Core and into chain/profile layers.
- Clarified that a T event records a termination declaration but does not
  itself prove that every downstream system stopped relying on the target.
- Clarified that duplicate valid delivery is not a cryptographic failure.
- Added explicit historical-decoder rules and prohibited heuristic
  fallback from 0.7 to pre-`-07` draft formats.
- Updated conformance requirements for producers, verifiers, and
  acceptance processors.
- Expanded security considerations for Event ID conflicts, safe retry,
  acceptance-state failure, and optional challenge profiles.

# IANA Considerations

This document requests no IANA actions.

A future standards-track revision may request registries for JEP verbs,
extension identifiers, validation checks, acceptance outcomes, trust
profiles, conformance classes, or related identifiers.

--- back

# Acknowledgments
{:numbered="false"}

The author thanks implementers and reviewers who provided interoperability,
security, and deployment feedback on earlier JEP draft revisions.
