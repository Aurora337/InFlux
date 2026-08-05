# InFlux Developer Guide

Version: v1.4.4

---

# Introduction

Welcome to InFlux development.

This guide explains how to set up a development environment, contribute code, run tests, and follow the project's engineering standards.

---

# Repository Structure

```text
InFlux/

├── src/
├── tests/
├── docs/
├── scripts/
├── CONTRIBUTING.md
├── CHANGELOG.md
├── ROADMAP.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── README.md
└── pyproject.toml
```

---

# Development Environment

Recommended tools:

* Python 3.12+
* Git
* VS Code
* pytest
* virtualenv

---

# Setting Up

Clone the repository.

Create a virtual environment.

Activate the virtual environment.

Install project dependencies.

Run the test suite.

---

# Branch Strategy

Development should occur on feature branches.

Example:

* feature/new-module
* docs/update-spec
* fix/state-replication

Never commit directly to `main`.

---

# Coding Standards

Code should be:

* Deterministic
* Modular
* Well documented
* Fully typed where practical
* Readable
* Tested

---

# Testing

Before opening a Pull Request:

* Run unit tests.
* Run protocol validation tests.
* Verify deterministic behavior.
* Confirm documentation updates.

## Wallet migration tooling

The repo includes a wallet key rotation and transaction resigning tool under `scripts/wallet/`. Run it with:

```bash
scripts/wallet/run.sh --storage .wallet --account acct-cli --private-hex <private_hex> --public-hex <public_hex> --resign-dir storage/txs --backup
```

If the package is installed, the entrypoint `influx-wallet-rotate` is available for direct use.

## Wallet migration tooling

The repo includes a wallet key rotation and transaction resigning tool under `scripts/wallet/`. Run it with:

```bash
scripts/wallet/run.sh --storage .wallet --account acct-cli --private-hex <private_hex> --public-hex <public_hex> --resign-dir storage/txs --backup
```

If the package is installed, the entrypoint `influx-wallet-rotate` is available for direct use.

---

# Documentation

Documentation is maintained alongside the implementation.

Any protocol-facing change should include corresponding documentation updates.

---

# Pull Requests

A Pull Request should contain:

* A clear summary.
* Associated documentation.
* Passing tests.
* Focused scope.
* Descriptive commit history.

---

# Project Philosophy

InFlux prioritizes:

* Determinism
* Security
* Reproducibility
* Maintainability
* Long-term protocol stability

Every contribution should reinforce these principles.

---

# Additional Resources

See:

* README.md
* CONTRIBUTING.md
* ARCHITECTURE_OVERVIEW.md
* docs/specs/
* docs/testnet/
* docs/roadmap/
