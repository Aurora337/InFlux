# Contributing to InFlux

Thank you for your interest in contributing to InFlux.

The InFlux protocol is built around deterministic execution, reproducibility, and long-term maintainability. Every contribution should strengthen these principles.

---

# Guiding Principles

All contributions should:

* Preserve deterministic behavior.
* Maintain consensus correctness.
* Improve documentation when functionality changes.
* Include tests for protocol-facing changes.
* Keep the repository organized and maintainable.

---

# Development Workflow

Contributors should follow this workflow:

1. Create a feature branch from `main`.
2. Implement a focused set of changes.
3. Add or update documentation.
4. Add or update tests.
5. Run the validation suite.
6. Commit using clear, descriptive messages.
7. Open a Pull Request for review.

---

# Branch Naming

Recommended branch naming:

* `feature/<name>`
* `fix/<name>`
* `docs/<name>`
* `audit/<name>`
* `release/<version>`

Example:

```
feature/economic-propagation
```

---

# Commit Messages

Use concise, descriptive commit messages.

Examples:

```
docs: update validator lifecycle specification
```

```
feat: add deterministic cluster synchronization
```

```
fix: resolve replay state validation issue
```

---

# Pull Requests

Each Pull Request should include:

* A summary of the change.
* The motivation for the change.
* Related documentation updates.
* Test results.
* Any known limitations.

---

# Documentation

Documentation is considered part of the protocol.

If code changes affect behavior, update the corresponding documentation in the same Pull Request.

---

# Testing

Before submitting changes:

* Run relevant unit tests.
* Verify deterministic behavior.
* Confirm no regression failures.
* Ensure documentation reflects the implementation.

---

# Code Style

Code should be:

* Readable
* Well documented
* Modular
* Deterministic
* Consistent with the existing project structure

---

# Reporting Issues

Bug reports should include:

* Environment details
* Steps to reproduce
* Expected behavior
* Actual behavior
* Relevant logs or screenshots

---

# Community

Be respectful, collaborative, and focused on improving the protocol.

Constructive discussion and technical feedback are encouraged.

---

# License

By contributing to InFlux, contributors agree that their submissions are provided under the project's license.
