# Unreleased: external implementation adoption

- Add scoped BSD-3-Clause licensing and package notices.
- Preserve exact Profiles -01 and Conformance -02 publications, with provenance
  and immutable checksums; archive abbreviated companion seeds and 0.6 docs.
- Add contribution, private security and implementation/interop report routes.
- Add a self-contained BYOI suite and language-neutral adapter runner, with
  separate producer/verifier/acceptance roles and observed acceptance effects.
- Accept the single-string V verification scope shown in published Conformance
  -02 while retaining existing signed array-scope artifacts. Core -07 is unchanged.

The package VERSION is not bumped here. BYOI commands require this source
revision until a subsequent package release is explicitly made. Existing release
artifacts must not be overwritten.

# Software 0.7.5

Align structural schemas with current verifier boundaries: non-empty extension
identifiers and exact whole-string digest matching, including terminal newlines.
A cross-repository hostile-input gate checks Core/API/Agent archival and acceptance
results, diagnostic check categories, unchanged hashes, corrected retries and
idempotence. It complements, rather than replaces, the existing signed-artifact
and historical interoperability gates.

Published -07 and existing signed fixtures remain byte-for-byte unchanged. The
local example path and post-publication installed-wheel checks are separate from
hosted API configuration and external policy/authority guarantees.

# Software 0.7.4

Complete the JCS numeric roundtrip repair: accept the canonical shortest decimal spelling of a binary64 number as well as its exact integer value. For example, JavaScript emits `1000000000000000100` for the float whose exact integer value is `1000000000000000128`. Both serialize to the same JCS bytes. Noncanonical precision-losing integers and overflow remain rejected.

Regression coverage includes positive and negative shortest-form numbers, exact large integers, real signatures and unchanged Event Hashes. Published normative artifacts remain unchanged.

# Software 0.7.3 follow-up

- Preserve JCS signatures when exactly representable large numbers arrive in integer-token form after JavaScript serialization (for example `1e20`). Reject precision-losing integers and keep `when` within its existing interoperable integer range.

Malformed event identities now produce `event_identity: null` in structured failure results, rather than copying empty or mistyped members that violate the result schema. Rejection remains side-effect free in acceptance mode.

A current cross-repository interoperability gate checks signed Binding/02 carriers, Core-only empty extensions, independent signature/hash agreement, client transport and malformed-identity diagnostics. It complements the retained historical 0.6 harnesses.

The published Core -07, Binding/02 and historical signed artifacts are unchanged.

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

## Current implementation delivery

Software release **0.7.2** publishes `jep-core-conformance` with the current Python validator, schemas and vectors. Conformance/01 and Profiles/01 describe the Core 0.7 migration. Explicit legacy validators and historical vectors remain available.

This release repairs malformed-input handling, unresolved-key results, acceptance-state failure handling, and schema alignment. It also verifies the published -07 hashes in CI. Legacy Go binaries are named `jep-validate-06-*` to identify their actual protocol target. The default Python command is `jep-validate` (Core 0.7).

The earlier software tag `v0.7.0` contained legacy 0.6 artifacts; it is retained as published history. No published Internet-Draft bytes are changed by this software release.

The unpublished 0.7.1 delivery attempt exposed a legacy Go test reading the current manifest. Release 0.7.2 selects the explicit 0.6 manifest and disables Go test-result caching in both CI and release gates.
