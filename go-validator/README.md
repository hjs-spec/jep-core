# Go JEP-Core-0.6 validator

Independent RFC 8785 / detached JWS Ed25519 verifier. It passes the explicit `test-manifest-0.6.json` used by the legacy Python and TypeScript implementations; it does not invoke either runtime.

This is an explicitly selected **legacy Core 0.6 validator**. Repository software version 0.7.x does not upgrade this decoder. Use the [Python reference validator](../reference-validator/README.md#current-jep-core-07) for Core 0.7 validation. The [Go HTTP SDK](https://github.com/hjs-spec/sdk-go) is a separate client of the current API, not this local verifier.

From the repository root:

```sh
cd go-validator
go build -o jep-validate-06 .
./jep-validate-06 validate event.json --keys keys.json
./jep-validate-06 validate-chain chain.jsonl --keys keys.json --trust-profile kid-prefix
./jep-validate-06 validate event.json --keys keys.json --mode acceptance --aud my-service --replay-cache nonces.json
```

The historical `go.mod` module path remains `github.com/hjs-spec/jep-v06/go-validator` for compatibility; it is not the current repository name. The local build above avoids an obsolete repository alias and version pin. Never fall back to this decoder after current validation fails.

`syntax file.json` explicitly runs only Level 0. `canonicalize file.json` emits RFC 8785 bytes. `validate` defaults to archival signature verification (Level 1); optional explicit `inline` or `kid-prefix` local trust profiles add actor binding (Level 2). Chain validation completes Level 3 only when actor binding also completed. No external policy or business truth is inferred.

Use locally configured trusted JWK files (map or JWKS). No remote key URLs from untrusted events are fetched. Malformed JOSE, duplicate JSON, noncanonical base64url and small-order identity forgeries fail closed.

Acceptance uses the same cache file and exclusive `.consume-lock` directory as the Python/TypeScript implementations. Locks left by a crash fail closed; remove only after confirming the owner is gone. Keep the cache throughout the freshness window. This CLI cache is for a shared local filesystem; use the API PostgreSQL backend for independent hosts.

CLI exit codes: 0 valid, 1 validation failure, 2 usage/file/key configuration error.
