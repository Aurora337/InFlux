# InFlux API Reference

Version: v1.4.4

---

# Overview

The InFlux API provides standardized interfaces for interacting with validator nodes, network services, and protocol components.

The API is designed to be deterministic, versioned, and stable across protocol releases.

---

# Base URL

Development:

```
http://localhost:8000/api/v1/
```

Testnet:

```
https://testnet.influx.network/api/v1/
```

Mainnet:

```
https://api.influx.network/api/v1/
```

---

# Authentication

Supported authentication methods may include:

* API Keys
* Validator Certificates
* OAuth (future)
* Mutual TLS (future)

---

# Network Endpoints

## GET /network/status

Returns current network status.

Response includes:

* Network ID
* Protocol Version
* Current Block Height
* Active Validators
* Cluster Count

---

## GET /network/health

Returns network health metrics.

---

## GET /network/peers

Returns connected peer information.

---

# Validator Endpoints

## GET /validator/{id}

Returns validator information.

---

## GET /validator/{id}/health

Returns validator health metrics.

---

## GET /validators

Returns all active validators.

---

# Consensus Endpoints

## GET /consensus/status

Returns consensus status.

---

## GET /consensus/round

Returns current consensus round.

---

# State Endpoints

## GET /state/latest

Returns latest finalized state.

---

## GET /state/snapshot

Returns current snapshot information.

---

# Transaction Endpoints

## POST /transaction

Submit a transaction.

---

## GET /transaction/{hash}

Query transaction status.

---

## GET /transactions

List recent transactions.

---

# Economics Endpoints

## GET /economics/supply

Returns protocol supply metrics.

---

## GET /economics/propagation

Returns economic propagation metrics.

---

## GET /economics/rewards

Returns validator reward information.

---

# Governance Endpoints

## GET /governance/proposals

Returns governance proposals.

---

## GET /governance/status

Returns governance information.

---

# Response Format

Every API response should include:

* Request ID
* Timestamp
* Protocol Version
* Status
* Result
* Error (if applicable)

---

# Error Codes

Common responses include:

* 200 OK
* 400 Bad Request
* 401 Unauthorized
* 403 Forbidden
* 404 Not Found
* 500 Internal Server Error

---

# Versioning

All endpoints are versioned to maintain compatibility across protocol releases.

Example:

```
/api/v1/
/api/v2/
```

---

# Future Expansion

Planned API additions include:

* Wallet APIs
* Explorer APIs
* Exchange APIs
* Smart Contract APIs
* Analytics APIs

---

This document serves as the reference for developers integrating with the InFlux protocol.
