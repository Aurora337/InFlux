FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu

# Install system packages
RUN apt-get update \
 && export DEBIAN_FRONTEND=noninteractive \
 && apt-get install -y --no-install-recommends \
    build-essential cmake git curl wget ca-certificates \
    g++ clang lldb pkg-config libssl-dev python3 python3-pip python3-venv \
 && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain system-wide
ENV RUSTUP_HOME=/usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo
ENV PATH=$CARGO_HOME/bin:$PATH

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
 && rustup default stable \
 && rustup component add clippy rustfmt

# Create cargo dirs for the default vscode user and set ownership if user exists
RUN mkdir -p /home/vscode/.cargo /home/vscode/.rustup \
 && chown -R vscode: /home/vscode/.cargo /home/vscode/.rustup || true

# Ensure /usr/local/cargo is writable and available
RUN mkdir -p /usr/local/cargo /usr/local/rustup \
 && chown -R root:root /usr/local/cargo /usr/local/rustup || true

# Default shell
SHELL ["/bin/bash", "-lc"]