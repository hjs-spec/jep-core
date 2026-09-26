# Judgment Event Protocol (JEP) — Core

This is the canonical repository for **JEP Core**, the narrow-waist event layer of the Judgment Event Protocol.

JEP Core defines signed judgment-related statements and their protocol-observable properties. It defines the four Core event verbs — Judgment (J), Delegation (D), Termination (T), and Verification (V) — without deciding substantive truth, authority, legality, causality, policy consequence, or external effect.

## Current status

| Item | Current value |
|---|---|
| Latest published Internet-Draft | `draft-wang-jep-judgment-event-protocol-07` |
| Core release | `JEP-Core 0.7` |
| Wire major | `jep: "1"` |
| Published date | 2026-09-26 |
| Editor's Copy | [draft-wang-jep-judgment-event-protocol.md](draft-wang-jep-judgment-event-protocol.md) |
| Frozen -07 snapshot | [releases/draft-07/](releases/draft-07/) |
| IETF Datatracker | https://datatracker.ietf.org/doc/draft-wang-jep-judgment-event-protocol/ |

The published `-07` snapshot is immutable. Any later correction or semantic change belongs to a subsequent Internet-Draft revision; the published `-07` artifact is never rewritten.

## Core invariants in 0.7

- **Event Identity:** `(who, id)` identifies the event instance.
- **Artifact identity:** Event Hash identifies an exact signed artifact and is not the Event Identity.
- **Safe retry:** delivery may repeat; an acceptance processor applies the acceptance effect of one Event Identity at most once within one acceptance domain.
- **Replay mechanisms:** Core does not mandate nonce, challenge, counter, ledger, or other freshness mechanisms; profiles may add them.
- **Orthogonal validation:** Core checks are separated from trust/acceptance-profile checks and companion/external checks.
- **Substantive neutrality:** protocol validity does not itself establish truth, authority, legality, policy outcome, causality, or external consequence.
- **Layer boundary:** chain reconstruction, termination cascade, authorization consequences, and domain policy remain outside JEP Core.

## Repository model

```text
repository identity     hjs-spec/jep-core
main                    current Editor's Copy and maintained Core assets
published revision      immutable release snapshot
future changes          next Internet-Draft revision, not a rewrite of -07
```

The unversioned Editor's Copy is the working source for future evolution. Versioned files such as `draft-wang-jep-judgment-event-protocol-07.*` are historical snapshots.

## Published JEP-07

The exact published RFCXML is preserved at:

- [releases/draft-07/draft-wang-jep-judgment-event-protocol-07.xml](releases/draft-07/draft-wang-jep-judgment-event-protocol-07.xml)
- [ietf-rendered/draft-wang-jep-judgment-event-protocol-07.xml](ietf-rendered/draft-wang-jep-judgment-event-protocol-07.xml)

SHA-256:

```text
601809b4053d485fa68367db22f5e43919e859c4f0227609b8f851c627e9caab
```

See [releases/draft-07/README.md](releases/draft-07/README.md) for the freeze record.

## Migration status of companion assets

JEP Core 0.7 changed identity, replay/acceptance, validation, and chain boundaries. Therefore older companion material MUST NOT be assumed to describe 0.7 merely because it remains in this repository.

| Asset | Status |
|---|---|
| JEP Core `-07` | Current / frozen publication |
| Editor's Copy | Current working Core source |
| `draft-wang-jep-judgment-event-protocol-06.md` | Historical pre-07 draft |
| `draft-wang-jep-conformance-01.md` | Current 0.7 conformance companion |
| `draft-wang-jep-profiles-01.md` | Current 0.7 profile companion |
| 0.7 schemas / test vectors / Python reference validator | Current 0.7 implementation aids |
| `draft-wang-jep-conformance-00.md` / `profiles-00.md` | Historical pre-07 companions |
| 0.6 schemas/test vectors/validators | Explicit legacy compatibility assets |

Historical material is retained for auditability and compatibility. It does not override JEP Core 0.7. Current conformance and profile work is represented by the `-01` companion drafts and the versioned 0.7 implementation aids.

## Implementation boundary

The repository also contains historical schemas, test vectors, reference validators, and implementation aids. These are non-normative unless a specific JEP Core revision or conformance specification explicitly binds them.

For JEP Core 0.7, do not infer:
- mandatory Core nonce semantics from pre-07 validators;
- cumulative Validation Levels 0–4 from pre-07 conformance material;
- chain or termination-cascade semantics as Core behavior;
- Event Hash as stable Event Identity.

## Versioning

Repository identity is stable; versions are snapshots.

```text
Repo        = protocol component identity
main        = Editor's Copy
draft-XX    = immutable Internet-Draft snapshot
Datatracker = external publication record
```

See [docs/VERSIONING.md](docs/VERSIONING.md).

## Developer documentation

[Documentation index](docs/README.md) · [Architecture](docs/architecture/README.md) · [Logging comparison](docs/comparisons/logging.md) · [Current Quickstart](https://github.com/hjs-spec/jep-quickstart)

Architecture and logging explanations are maintained here after [repository consolidation](docs/REPOSITORY-CONSOLIDATION-2026-09.md). Their original repositories retain historical links.

## Companion ecosystem

JEP Core is intentionally narrower than the wider JEP ecosystem. Profiles, conformance rules, semantic bindings, chain composition, runtime behavior, SDKs, and application integrations may evolve independently, but MUST NOT silently redefine Core semantics.

## Historical repository identity

This repository was previously named `hjs-spec/jep-v06`. The repository was renamed to `hjs-spec/jep-core` so that repository identity no longer tracks a particular draft revision.

## Local checks

```sh
python -m pip install -e '.[test]'
make validate conformance repository-check
make conformance-legacy
python -m pytest
```

The default Make targets use the current 0.7 path. `validate-legacy` and
`conformance-legacy` select the historical 0.6 implementation explicitly.
`repository-check` verifies immutable -07 artifact hashes and manifest paths.
The retired -07 rendering workflow is now read-only: it checks and exports the
frozen publication, and cannot regenerate or commit replacements.
