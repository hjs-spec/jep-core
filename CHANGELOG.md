# Changelog

All notable changes to the HJS Core project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of four core primitives
  - Judgment event creation and verification
  - Delegation chain management
  - Termination records
  - Verification modes (platform, open, dual)
- Receipt generation and validation
- Ed25519 cryptographic signatures
- UUIDv7 timestamp support (RFC 9562)
- JCS canonical serialization (RFC 8785)

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- N/A (initial release)

---

## [0.1.0] - 2026-03-03

### Added
- Initial release
- Core protocol implementation matching IETF draft-wang-hjs-judgment-event-00
- CLI tool for basic operations
- Rust crate with public API
- Unit tests and integration tests
- Documentation and examples

[Unreleased]: https://github.com/hjs-protocol/core/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hjs-protocol/core/releases/tag/v0.1.0
