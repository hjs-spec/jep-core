# HJS Core

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

> **Status**: Alpha — Work in Progress  
> **IETF Draft**: [draft-wang-hjs-judgment-event-00](https://datatracker.ietf.org/doc/draft-wang-hjs-judgment-event/)

Rust implementation of **HJS: A Judgment Event Protocol** for cross-platform AI accountability attribution.

## Overview

HJS provides minimal, portable, cryptographically verifiable proof of who is responsible for AI decisions. This crate implements the core protocol:

- **4 Primitives**: Judge, Delegate, Terminate, Verify
- **Portable Receipts**: Self-contained verification credentials
- **3 Verification Modes**: platform, open, dual
- **IETF Standards**: UUIDv7 (RFC 9562), JCS (RFC 8785)

## Quick Start

```bash
# Build
cargo build --release

# Run CLI
cargo run --bin hjs -- --help

# Create a Judge event (placeholder)
cargo run --bin hjs -- judge \
  --actor "did:example:ai-agent-1" \
  --decision-hash "sha256:abc123..." \
  --authority "https://policy.example.com/v1" \
  --from 1712345678 \
  --until 1714937678
```

## Compliance

| Draft Section | Feature | Status |
|--------------|---------|--------|
| 6.1 | Event Model | 🚧 In Progress |
| 6.2 | Common Fields | 🚧 In Progress |
| 6.3 | State Machine | 🚧 In Progress |
| 6.4 | Data Format (JCS) | 🚧 In Progress |
| 6.5 | Receipt Format | 🚧 In Progress |
| 7.2 | HTTP API | ❌ Out of scope (see hjs-api) |

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   hjs-cli   │────▶│  hjs-core   │◀────│  hjs-wasm   │
│  (CLI tool) │     │ (this crate)│     │(JS bindings)│
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  hjs-api    │
                    │(SaaS service)│
                    │  (optional)  │
                    └─────────────┘
```

## Related Repositories

- [hjs-api](https://github.com/schchit/hjs-api) — Production SaaS implementation
- [hjs-aip-integration](https://github.com/schchit/hjs-aip-integration) — AIP protocol integration

## License

Apache-2.0 — See [LICENSE](LICENSE)

