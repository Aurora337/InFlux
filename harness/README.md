Harness for In~Flux: scenario engine, replay engine, assertion layer, node mesh simulator, metrics collector, and report generator.

This directory contains tools and test infrastructure for validating the deterministic economic engine across multi-node scenarios. Each module is a placeholder intended to be extended with real simulation logic and integration tests.

Modules
- scenario_engine.py: orchestrates scenario execution
- replay_engine.py: replays recorded events deterministically
- assertion_layer.py: contains test assertions and invariants
- node_mesh_simulator.py: simulates multi-node network behavior
- metrics_collector.py: gathers runtime metrics and statistics
- report_generator.py: produces human-readable test reports