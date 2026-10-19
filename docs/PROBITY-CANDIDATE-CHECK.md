# Candidate Core 0.7 check

The candidate check runs current JEP code against the agreed cases and keeps
the fixed pilot unchanged.

| Output | Code | Suite | Population |
| --- | --- | --- | --- |
| Candidate agreed run | Candidate validator and producer | Frozen [a87a395 suite](https://github.com/hjs-spec/jep-core/tree/a87a395b54b5685fd22d6cc86d120058f1c8850d/reference-validator/byoi_suite) | 29 native assertions; 8 acceptance assertions unselected |
| Separate reader | Pinned [cbd3ea8 reader](https://github.com/probityai/agent-evidence-vectors/tree/cbd3ea8f4de89b835d6d3c4182ff4b4b1c7608f9/interop/jep-core07-reader) | The same frozen suite | 25 validation, 4 producer and 8 synthetic acceptance assertions |
| Candidate suite run | Candidate validator and producer | Candidate-owned suite bytes | Current native population, recorded separately |

The native adapter wraps JEP code. The Probity reader is separately implemented;
its synthetic state is controlled by Probity. Reports retain source heads,
trees, file hashes, exchanges and exit statuses. These are finite fixture runs.

## Regression controls

Three isolated mutations remove duplicate-member admission, bypass signature
verification or change the assigned producer event. Each must fail the candidate
run on the frozen agreed cases. The candidate checkout stays unchanged.

A separate negative control weakens the candidate suite's expected answer to
hide the duplicate-member fault. That run becomes green, while the frozen gate
still fails. Candidate-owned expectations cannot replace the agreed comparison.

## Suite updates

Reviewed candidate suite updates get their own native run and manifest digest.
A metadata-only update control passes that path without moving the agreement.
The pinned reader explicitly refuses the changed manifest if given those bytes.

To expand or revise the cross-implementation agreement, publish and review the
reader protocol and source lock first, then update the suite/reader pins and
population checks together. Keep the fixed pilot and previous reports at their
original pins. Current-suite native results do not qualify new cases for the
pinned reader.

The workflow runs on every PR so its context is always present. Maintainers
decide whether to require it for Core 0.7 validator and BYOI suite changes.
