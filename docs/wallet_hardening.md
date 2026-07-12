# Wallet Hardening (InFlux)

Goal: upgrade the `wallet` subsystem to production-grade cryptography, key management, and APIs while preserving deterministic behavior where required and maintaining test coverage.

Scope
- Ed25519 for signing and verification
- Secp256k1 support (future optional for interoperability)
- Deterministic transaction IDs unchanged
- Key rotation and migration tooling
- Multisig primitives
- Secure key storage guidance (KDF, hardware support)
- API compatibility layer and migration plan

High-level plan
1. Design and spec (this document)
2. Add dependency: `PyNaCl` for Ed25519 (or `pynacl` package)
3. Implement `Ed25519WalletSigner` in `src/influx/wallet/signing.py`:
   - New API: `sign(transaction, private_key_bytes)` and `verify(transaction, public_key_bytes)`
   - Store signatures as base64-encoded strings with a header `ed25519:`
   - Keep legacy deterministic SHA256 signer available as `LegacyWalletSigner` for compatibility/migration
4. Update tests under `tests/wallet` to exercise `Ed25519WalletSigner` and verify backward compatibility with `LegacyWalletSigner` where necessary
5. Add key rotation support:
   - `KeyVersion` metadata for accounts
   - Migration tooling to re-sign pending transactions or mark legacy signatures
6. Implement multisig primitives:
   - `MultisigPolicy` describing signers and threshold
   - Aggregation as ordered signatures array or M-of-N scheme
   - Tests for construction and verification
7. Secure storage guidance (doc + checklist):
   - Use PBKDF2 or argon2id with salt for seed encryption
   - Recommend HSM/secure enclave for production
   - Provide CLI helpers for key generation and key wrapping
8. CI and test coverage:
   - Add cryptography unit tests to CI matrix
   - Run static analysis on cryptographic code
9. Integration and rollout:
   - Phased rollout: tests -> devnet -> public testnet -> mainnet
   - Migration strategy recorded in repo

Backward compatibility
- Transaction ID calculation must remain unchanged.
- Signatures change format; new field `signature_scheme` or prefix `ed25519:` used to distinguish.
- Legacy signatures remain verifiable by `LegacyWalletSigner` for a deprecation window.

Developer workflow notes
- Local dev: `pip install -e .[dev]` will pull `pynacl` in dev env.
- Tests: add deterministic key fixtures to `tests/fixtures/keys.py`.

Security considerations
- Never log private keys or raw seeds
- Validate public key lengths and signature formats
- Constant-time comparisons when verifying signatures
- Use OS randomness for key generation

Next concrete implementable steps
- Add `pynacl` to `pyproject.toml` dependencies
- Implement `Ed25519WalletSigner` with tests
- Add KDF guidance document and helpers8. Add a CLI wrapper and documentation for running wallet key rotation and signature migration tooling from scripts/wallet/run.sh

