# Wallet Key Management and Secure Storage

This document outlines recommended practices for securely deriving, storing, and rotating wallet keys for InFlux. It focuses on pragmatic, production-ready guidance: KDF selection and parameters, encrypted on-disk storage formats, integration with HSMs/keystores, and operational procedures.

## Goals
- Protect private keys and seeds at rest and in transit
- Make key derivation reproducible and slow enough to resist offline attacks
- Support secure key rotation and migration
- Provide clear formats for encrypted key blobs and metadata

## Key Derivation Functions (KDFs)
Recommended primary KDF: `argon2id` (memory-hard). Fallback: `PBKDF2-HMAC-SHA256` when Argon2 is unavailable.

Argon2id recommended parameters (2026 baseline):
- `time_cost`: 3
- `memory_cost`: 65536 (64 MiB)
- `parallelism`: 4
- `salt`: 16 bytes cryptographically random
- `hash_len`: 32 bytes

PBKDF2 fallback parameters:
- `iterations`: 200_000
- `hash`: SHA-256
- `salt`: 16 bytes
- `dklen`: 32 bytes

Use a unique salt per key/account. Store salt and KDF parameters alongside the encrypted key blob so they are available for verification and migration.

### Libraries
- Python: `argon2-cffi` (Argon2), `cryptography` (AES-GCM, HKDF), `argon2-cffi-bindings` for lower-level control when needed.
- Avoid homegrown KDFs.

## Key Wrapping (Encryption of Private Keys)
Encrypt derived key material with an authenticated encryption algorithm. Recommended: AES-256-GCM or XChaCha20-Poly1305.

Storage format (JSON example):
{
  "version": 1,
  "kdf": "argon2id",
  "kdf_params": {"time_cost":3, "memory_cost":65536, "parallelism":4},
  "salt": "<base64>",
  "cipher": "aes-256-gcm",
  "nonce": "<base64>",
  "tag": "<base64>",
  "encrypted_key": "<base64>",
  "meta": {"account_id":"wallet-1","created_at":1630000000}
}

Implementation notes:
- Use `os.urandom(16)` for salt and `os.urandom(12)` for AES-GCM nonce.
- Use `cryptography.hazmat.primitives.ciphers.aead.AESGCM` for AES-GCM.
- Do not reuse nonces for the same key encryption key (KEK).

## Key Encryption Keys (KEK)
- Derive the KEK from a user passphrase via Argon2id with the stored salt and KDF params.
- For machine accounts or services, prefer a KEK stored in an OS keystore (e.g., Azure Key Vault, AWS KMS, Google KMS, HashiCorp Vault) or HSM.
- KEK length: 32 bytes (AES-256). If using HKDF, use `HKDF(algorithm=SHA256, length=32, salt=None, info=b'InFlux-KEK')` to derive final symmetric key from KDF output.

## Private Key Storage
- Never store raw seed or private key in plaintext in repository or logs.
- Store only encrypted blobs and metadata in repository-controlled storage if necessary; prefer secure vaults for production.
- Provide a CLI tool to encrypt/decrypt key blobs locally for developer workflows.

## Hardware and OS Integration
- Prefer HSMs or cloud KMS for production keys. Use the KMS to sign requests or unwrap keys only when necessary.
- For local developer convenience, support OS keystores (macOS Keychain, Windows DPAPI, Linux Secret Service) with explicit opt-in.

## Key Rotation and Migration
- Include a `key_version` field in account metadata.
- Rotation steps:
  1. Generate new keypair (new version) and encrypt it under the KEK.
  2. Update account metadata to reference new `key_version`.
  3. Re-sign any pending transactions (if necessary) or accept legacy signatures until a cutoff date.
  4. Publish rotation event to on-chain governance or an off-chain registry for validators.
- Migration tooling should be idempotent and support dry-run mode.

## Multisig considerations
- Store individual participant public keys and the multisig policy separately.
- Do not aggregate private keys; the multisig signing flow should collect signatures from participants and assemble them into the transaction object.

## Operational Practices
- Backup encrypted key blobs and store backups in geographically separate, encrypted storage.
- Maintain a revocation and emergency rotation playbook.
- Limit access to key material with ACLs and audit logging.

## Example: deriving KEK and encrypting a private key (Python sketch)

```python
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, base64

# derive
salt = os.urandom(16)
key = hash_secret_raw(b'passphrase', salt, time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, type=Type.ID)

# encrypt
aesgcm = AESGCM(key)
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, private_key_bytes, None)

blob = {
  'kdf': 'argon2id',
  'kdf_params': {'time_cost':3,'memory_cost':65536,'parallelism':4},
  'salt': base64.b64encode(salt).decode(),
  'cipher': 'aes-256-gcm',
  'nonce': base64.b64encode(nonce).decode(),
  'encrypted_key': base64.b64encode(ciphertext).decode(),
}
```

## Testing and CI
- Add unit tests for KDF parameters, encryption/decryption roundtrips, and incorrect-passphrase behavior.
- Include integration tests with a mock KMS.

## Notes on determinism
- Transaction ID determinism must be preserved; do not change transaction hashing rules during key upgrades.
- Signatures are intentionally non-deterministic (Ed25519 signatures vary by nonce under some schemes) and are stored as scheme-prefixed blobs.

## References
- Argon2 RFC / libsodium / PyNaCl docs
- NIST guidance on key management
- OWASP cryptographic storage cheat sheet
