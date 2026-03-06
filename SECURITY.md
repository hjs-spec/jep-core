# Security Policy

## Supported Versions

We currently support the following versions of JEP Core with security updates:

| Version | Supported          |
|---------|-------------------|
| 0.1.x   | ✅ Yes            |
| < 0.1   | ❌ No             |

## Reporting a Vulnerability

We take the security of JEP Core seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do NOT

- **Do not** open public GitHub issues for security vulnerabilities
- **Do not** discuss the vulnerability in public forums
- **Do not** disclose the vulnerability to others until we've had a chance to address it

### How to Report

Please send a detailed report to **[security@humanjudgment.org](mailto:security@humanjudgment.org)**. 

If you prefer, you can also contact us via our main email at [signal@humanjudgment.org](mailto:signal@humanjudgment.org) with "SECURITY" in the subject line.

### What to Include

To help us understand and fix the issue quickly, please include:

- Type of vulnerability (e.g., buffer overflow, signature bypass, etc.)
- Full steps to reproduce the issue
- Affected versions
- Any potential impacts
- Your name/affiliation (if you wish to be credited)

### What to Expect

- We will acknowledge receipt within **48 hours**
- We will provide an initial assessment within **5 business days**
- We will keep you informed of progress
- Once fixed, we will credit you in the release notes (unless you prefer to remain anonymous)

### Disclosure Policy

We follow a coordinated disclosure process:

1. Reporter submits vulnerability details
2. We confirm and assess the issue
3. We develop and test a fix
4. We release a patched version
5. We publicly disclose the issue after users have had time to update

## Security Features

JEP Core implements several security features:

| Feature | Description |
|---------|-------------|
| **Ed25519 Signatures** | All receipts are signed with Ed25519, a modern, secure signature scheme |
| **Canonical Serialization** | JCS ensures deterministic JSON serialization before hashing |
| **Constant-Time Operations** | Critical cryptographic operations use constant-time implementations |
| **No External Dependencies** | Minimal attack surface with carefully audited dependencies |

## Responsible Disclosure Hall of Fame

We thank the following individuals for responsibly disclosing security issues:

*(None yet - be the first!)*

---

**© 2026 HJS Foundation Ltd.**  
This document is licensed under the [MIT License](https://opensource.org/licenses/MIT).
