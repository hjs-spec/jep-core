# JEP v0.6 TypeScript Validator Seed

This is an explicitly selected **legacy Core 0.6 validator**. Repository software version 0.7.x does not upgrade this decoder. Use the [Python reference validator](../reference-validator/README.md#current-jep-core-07) for current Core 0.7 validation. The [JavaScript HTTP SDK](https://github.com/hjs-spec/sdk-js) is a separate client of the current API, not this local verifier.

The TypeScript seed implements strict JSON duplicate-member detection, I-JSON checks, the repository baseline event shape, RFC 8785-compatible ECMAScript canonicalization, detached compact JWS/Ed25519 verification, event hashes, critical-extension rejection, optional local actor binding, and acceptance replay/freshness checks.

It currently declares Level 0/1 capability plus optional local Level 2 actor binding. It does not declare JEP-Chain-0.6 conformance.

```bash
npm install
npm run check
```

Direct validation:

```bash
node dist/jep_validate.js \
  ../test-vectors/interop/control-J.json \
  ../test-vectors/interop/public-keys.json
```

The test script checks legacy JCS edge vectors, exact failure codes, Validation Levels and replay behavior alongside the explicitly selected Python 0.6 implementation. Never fall back to this decoder after current validation fails.
