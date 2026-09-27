# Architecture notes

These implementation notes explain the diagrams. Protocol definitions remain in [JEP Core 0.7](https://github.com/hjs-spec/jep-core), [HJS 0.5](https://datatracker.ietf.org/doc/draft-wang-hjs-accountability/) and [JAC](https://github.com/hjs-spec/jac-agent-02).

## Responsibilities

| Layer | Owns | Does not establish by itself |
|---|---|---|
| JEP: Judgment Event Protocol | Atomic signed J/D/T/V statements, Core canonicalization, signatures, event hashes and verification results | Truth, complete logging, identity binding or valid authority |
| HJS | Archive, privacy, receipt and evidence lifecycle | New JEP verbs, signature rules, Core validation-check meanings or execution permissions |
| JAC | Declared dependencies over JEP/HJS, including `ext["https://jac.org/chain"]` with `based_on`, `based_on_type`, `relation` | Core canonicalization or proof of real causality |
| Application runtime | Tool dispatch, independently configured policy, identity resolution and storage integration | Automatic conformance to all three protocols |
| SDK/API | Supported event creation and verification interfaces | Authority validation merely because a signature passes |

## Format and verification matrix

Choose components by their actual format, not their repository name. JSONL describes a container, not an interoperability contract.

| Component | Format / ownership | What verification establishes |
|---|---|---|
| Core reference validator | Current 0.7 signed wire event; explicit legacy 0.6 path | Independent Core checks under the supplied keys/profile |
| API + Python/JS/Go SDK + CLI | Current 0.7 wire event; clients delegate signing/verification to the API | Server-reported checks; clients do not independently verify signatures |
| Agent SDK | Current 0.7 event plus local chain extensions | Core signatures and supported local checks; HTML export is an unverified projection |
| Agent Blackbox | Core 0.7-style events plus local JAC/HJS conventions | Local hashes/signatures and incident links; not universal companion conformance |
| Runtime | Own normalized/sorted JSON envelope and mock signatures | Local profile checks; not Core JCS/JWS conformance |
| LangGraph / OpenAI Agents / MCP adapters | Three separate unsigned observation/archive formats | Each adapter's archive consistency checks; not Core signature verification |
| Authority runtime / lineage explorer | Declared local scope and delegation records | Local policy-model consistency; not authenticated real-world authority |
| Replay visualizer | Normalized projection of supplied records | Displayed links/results; no hash recomputation or JWS verification |
| Claude replay | Own envelope, signatures and `.jcrpack` | Its declared replay/signature profile; not Core detached JWS |
| AIP sidecar | `aip-sidecar-receipt-0.2`, sorted ASCII JSON | Receipt integrity under a caller-trusted key; not a Core event |
| JAC seed | JAC extension/fragment; historical unsigned demo events | Declaration structure and fragment hashes; not event signatures |
| GitHub Action | Historical 0.6-style workflow artifact or legacy API result | Mode-specific checks; unsigned artifacts are not signed Core events |

The runtime, authority, lineage, replay and three observation-adapter experiments are retired from active development; their formats and readers remain available for historical reproduction. New signed recording and reports belong to the [Agent SDK](https://github.com/hjs-spec/jep-agent-sdk/blob/main/docs/INTEGRATIONS.md). Maintenance status is listed in the organization directory.

No automatic adapter connects these archive formats. A bridge must name the source format, preserve original signed bytes, define its mapping and pass interoperability tests. A lifecycle label such as completion or failure is not automatically a Core `T` statement.

## Component ownership

Core owns protocol definitions and conformance assets. The API owns shared service state; HTTP clients own transport and language ergonomics. The Agent SDK owns local agent recording and reports. Quickstart owns the introductory workflow. Retired runtime experiments preserve only their historical envelopes, policies and readers; they are outside the active feature roadmap.

The [organization directory](https://github.com/hjs-spec/.github/blob/main/PROJECTS.md) is the sole repository inventory. This document explains boundaries, rather than duplicating installation or release tables.

## Core objects and application envelopes

Preserve signed Core members exactly when forwarding or archiving. The current protocol profile is `jep-core-0.7`, while its wire member remains `jep: "1"`. Event Identity is `(who,id)`; Event Hash identifies an exact signed artifact. Software version numbers are independent.

Application fields such as `record_id`, `sequence`, `event_hash`, `previous_event_hash`, tool digests and external references belong to an explicitly defined local envelope or permitted extension. They are not a universal set of required Core members. Do not append them to an already signed Core object or replace its canonicalization with ordinary sorted JSON.

A Core `D` event is a declaration. Enforcing permissions before a tool side effect requires the application's policy and trust model. A `T` event does not undo an external side effect. A `V` statement must describe the checks actually performed, with its scope preserved; a cryptographic `pass` does not imply actor binding, authority, chain integrity, or policy validity.

## Verification and replay

1. Parse strictly and select an explicit format/profile. Historical formats require explicit compatibility paths.
2. Validate Core syntax, canonicalize according to Core rules and verify the signature under an independently trusted key policy.
3. Return the actual `profile`, `status`, `mode`, independent `checks`, `conformance_class`, Event Identity, diagnostics, and Event Hash.
4. If required and supported, separately validate archive receipts, declared dependencies, identity binding and application authority. Report missing evidence as unresolved or failed under that validator's contract.

The current reference API exposes JEP Core 0.7 checks. Archival mode is repeatable and does not consume acceptance state; acceptance mode uses stable Event Identity and idempotent acceptance. Actor binding, freshness, audience, chain, and policy checks are performed only when the applicable profile/mode requires them. A locally recomputed hash chain lacks a trusted completeness anchor and can be rewritten by its author.

## Runtime integration

Capture successful and failed operations according to the application's recording policy, minimize sensitive data, and preserve links to independently available evidence. Recording may fail after a tool side effect, so middleware alone does not guarantee complete or atomic logging. Replay should be read-only; re-executing tools is a separate explicit action. Keep policy decisions, signing-key trust, execution permissions and retention rules visible as distinct responsibilities.
