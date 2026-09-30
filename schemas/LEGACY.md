# Legacy pre-0.7 schema semantics

The generic schema entry points in `schemas/` describe JEP Core 0.7.

JEP Core 0.6 and earlier draft artifacts remain historical and MUST be
validated using an explicitly selected pre-0.7 compatibility path. Do not
infer a legacy decoder from field presence after a 0.7 failure.

The previous generic signature/extension helpers are preserved byte-for-byte in
[legacy/0.6](legacy/0.6/README.md). Other exact historical schema versions remain recoverable from Git history and
the published pre-0.7 revisions. Historical signed artifacts MUST NOT be
rewritten to satisfy the 0.7 schemas.
