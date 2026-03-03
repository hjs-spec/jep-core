## 📝 `hjs-core/CONTRIBUTING.md`

```markdown
# Contributing to HJS Core

Thank you for your interest in contributing to **HJS Core**, the Rust reference implementation of the HJS protocol! We welcome contributions from everyone, whether you're fixing a bug, improving documentation, or proposing new features.

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold its standards. Reports can be sent to [signal@humanjudgment.org](mailto:signal@humanjudgment.org).

## Ways to Contribute

### 📝 Issues
Report bugs, suggest improvements, or ask questions via [GitHub Issues](https://github.com/hjs-protocol/core/issues).

| Issue Type | Guidelines |
|------------|------------|
| **Bug reports** | Include steps to reproduce, expected behavior, and actual behavior |
| **Feature suggestions** | Explain the use case and alignment with HJS core primitives |
| **Questions** | Use issues for technical questions about the implementation |

### 🔧 Pull Requests
Submit code changes, fixes, or improvements.

1. **Fork** the repository
2. **Create a branch** (`git checkout -b feature/your-feature`)
3. **Make your changes**, following our guidelines
4. **Write tests** for new functionality
5. **Ensure all tests pass** (`cargo test`)
6. **Run formatting and linting** (`cargo fmt` and `cargo clippy`)
7. **Commit with clear messages** (see [Conventional Commits](https://www.conventionalcommits.org/))
8. **Push to your fork** and submit a Pull Request

### 💬 Discussions
Join the conversation on [GitHub Discussions](https://github.com/hjs-protocol/core/discussions) or reach out via [signal@humanjudgment.org](mailto:signal@humanjudgment.org).

## Development Setup

### Prerequisites

- Rust (install via [rustup](https://rustup.rs/))
- Cargo (comes with Rust)
- Git

### Local Setup

```bash
# Clone the repository
git clone https://github.com/hjs-protocol/core.git
cd core

# Build the project
cargo build

# Run tests
cargo test

# Run the CLI
cargo run --bin hjs -- --help
```

### Development Workflow

1. **Make your changes** in a feature branch
2. **Run tests frequently**: `cargo test`
3. **Check formatting**: `cargo fmt -- --check`
4. **Run linter**: `cargo clippy -- -D warnings`
5. **Update documentation** if needed
6. **Commit with a clear message**

## Guidelines

### Code Style

- Follow Rust standard style (automatically enforced by `rustfmt`)
- Use meaningful variable and function names
- Add comments for non-obvious logic
- Keep functions focused and small

### Testing

- Write unit tests for new functionality
- Place tests in the same file as the code, under a `#[cfg(test)]` module
- Use integration tests in the `tests/` directory for complex scenarios

**Example:**

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_judgment_creation() {
        let event = JudgmentEvent::new("test", "action");
        assert_eq!(event.entity, "test");
    }
}
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**

```
feat(receipt): add Ed25519 signature support

- Implement signing and verification
- Add test vectors from draft
- Update documentation

Closes #42
```

### Pull Request Process

1. Ensure all tests pass and code is formatted
2. Update documentation if necessary
3. Keep PRs focused on a single change
4. Respond to review feedback promptly
5. After approval, a maintainer will merge

## Project Structure

```
core/
├── crates/           # Crate implementations
├── src/              # Main source code
├── tests/            # Integration tests
├── examples/         # Example usage
├── Cargo.toml        # Project manifest
└── README.md         # This file
```

## Related Resources

- [HJS Protocol Specification](https://github.com/hjs-protocol/spec)
- [IETF Draft](https://datatracker.ietf.org/doc/draft-wang-hjs-judgment-event/)
- [API Reference](https://github.com/hjs-protocol/api)
- [Rust Documentation](https://doc.rust-lang.org/)

## Recognition

Contributors will be recognized in:

- Release notes
- Repository README (for significant contributions)
- Our thanks page

## Questions?

Feel free to:

- Open an [issue](https://github.com/hjs-protocol/core/issues)
- Start a [discussion](https://github.com/hjs-protocol/core/discussions)
- Email [signal@humanjudgment.org](mailto:signal@humanjudgment.org)

Thank you for helping make HJS better!

---

**© 2026 Human Judgment Systems Foundation Ltd.**  
This document is licensed under the [MIT License](https://opensource.org/licenses/MIT).
```
