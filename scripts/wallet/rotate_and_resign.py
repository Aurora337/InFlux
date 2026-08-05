#!/usr/bin/env python3
"""Wallet rotation CLI wrapper for the InFlux package entrypoint."""

from __future__ import annotations

from influx.wallet.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
