Tests for In~Flux: golden unit tests and integration tests.

Structure
- golden/: fast unit-level tests for individual kernel components
- integration/: higher-level integration tests across modules

Run with pytest from the repository root. Tests load source modules from src/ using importlib to avoid package requirements.