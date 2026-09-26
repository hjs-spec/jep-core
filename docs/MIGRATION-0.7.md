# JEP 0.7 Ecosystem Migration

Current Core: **JEP Core 0.7**.

## Current in this repository

- Core 0.7 specification: current/frozen publication.
- Generic schemas: 0.7 current.
- Conformance/01: 0.7 current draft.
- Profiles/01: 0.7 current draft.
- Python reference validator: 0.7 current.
- 0.7 vectors/manifest: current.
- 0.6 Python/TypeScript/Go validators and vectors: explicit legacy compatibility.

## Still to migrate outside or alongside Core

- jep-api;
- sdk-js / sdk-py / sdk-go;
- jep-agent-sdk;
- jep-runtime;
- AMP / semantic interoperability;
- JEP-TSTO Binding/02;
- HJS / Agent Blackbox adapters;
- application integrations such as Prooftask.

## Migration invariants

1. Never rewrite historical 0.6 signatures.
2. Never silently infer 0.6 after a 0.7 failure.
3. Semantic event references use Event Identity.
4. Exact signed-artifact pins continue to use Event Hash.
5. Duplicate delivery is not cryptographic invalidity.
6. Nonce remains allowed where a profile/application actually requires a challenge.
7. Chain, lifecycle, legal, policy, and external truth semantics remain outside Core.
