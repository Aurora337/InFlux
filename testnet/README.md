# Testnet Scaffold

v0.7 testnet preparation layout:

- genesis/
- validators/
- bootstrap/
- peers/
- messages/
- state/
- configs/
- launch/

v0.7.2 runtime artifacts:
- launch/snapshots/
- launch/network_health.json

v0.7.5 runtime artifact:
- launch/fault_report.json
- launch/fault_report.md

v0.8.1 runtime artifacts:
- launch/sync_report.json
- launch/sync_report.md

v0.8.2 runtime workflow:
- launch/sync_report.json and launch/sync_report.md capture catch-up recovery metrics

v0.8.3 runtime workflow:
- launch/staggered_sync_report.json and launch/staggered_sync_report.md capture multi-validator staggered recovery results

v0.8.4 runtime workflow:
- launch/dual_offline_report.json and launch/dual_offline_report.md capture dual-offline recovery and conflict-resolution checks

v0.8.5 runtime workflow:
- launch/partial_replay_report.json and launch/partial_replay_report.md capture chunked replay stress with timeout/retry metrics
- launch/partial_replay_matrix_report.json and launch/partial_replay_matrix_report.md capture multi-target replay profile matrix results

v0.8.6 runtime workflow:
- launch/retry_exhaustion_suite.json and launch/retry_exhaustion_suite.md capture expected success/failure sync resilience checks
- launch/backoff_latency_suite.json and launch/backoff_latency_suite.md capture deterministic backoff latency envelope checks
- launch/policy_comparison_suite.json and launch/policy_comparison_suite.md capture deterministic retry policy ranking results

v0.8.7 runtime workflow:
- launch/sync_orchestration_report.json and launch/sync_orchestration_report.md capture consolidated resilience orchestration outcomes
- launch/sync_orchestration_supervisor_report.json and launch/sync_orchestration_supervisor_report.md capture orchestration retry/escalation supervision outcomes

v0.8.8 runtime workflow:
- launch/sync_ops_runbook.json and launch/sync_ops_runbook.md capture operations runbook severity and response actions

v0.8.9 runtime workflow:
- sync operations runbook includes a deterministic incident timeline appendix for attempt-by-attempt chronology
- launch/sync_ops_handoff_note.json and launch/sync_ops_handoff_note.md capture compact shift-handoff guidance from runbook data

v0.9.0 runtime workflow:
- launch/sync_ops_stability_gate.json and launch/sync_ops_stability_gate.md capture deterministic pass/fail gating for runbook-to-handoff consistency
- stability gate outputs also include release-readiness score, promotion recommendation, and deterministic guidance based on operational state
- launch/sync_ops_promotion_packet.json and launch/sync_ops_promotion_packet.md capture deterministic release decision, blockers, and artifact manifest hashes

v0.9.1 runtime workflow:
- launch/sync_ops_promotion_packet_validation.json and launch/sync_ops_promotion_packet_validation.md capture deterministic promotion packet integrity and decision-consistency checks

v0.9.2 runtime workflow:
- launch/sync_ops_assurance_report.json and launch/sync_ops_assurance_report.md capture deterministic assurance score, readiness verdict, and aggregated release blockers
- launch/sync_ops_assurance_report_validation.json and launch/sync_ops_assurance_report_validation.md capture deterministic assurance-report integrity and consistency checks
- launch/sync_ops_assurance_pipeline.json and launch/sync_ops_assurance_pipeline.md capture one-command end-to-end deterministic assurance execution with stage outcomes and artifact hashes

v0.9.3 runtime workflow:
- launch/sync_ops_governance_report.json and launch/sync_ops_governance_report.md capture deterministic governance approval mode, required sign-offs, and governance actions
- launch/sync_ops_governance_report_validation.json and launch/sync_ops_governance_report_validation.md capture deterministic governance report integrity and consistency checks
- launch/sync_ops_governance_pipeline.json and launch/sync_ops_governance_pipeline.md capture one-command end-to-end governance execution with stage outcomes and governance verdict

v0.9.4 runtime workflow:
- launch/sync_ops_release_certificate.json and launch/sync_ops_release_certificate.md capture deterministic release certificate status, conditions, and SHA-256 fingerprint

v0.9.5 runtime workflow:
- launch/sync_ops_release_certificate_validation.json and launch/sync_ops_release_certificate_validation.md capture deterministic certificate fingerprint and consistency checks

v0.9.6 runtime workflow:
- launch/sync_ops_finalization_pipeline.json and launch/sync_ops_finalization_pipeline.md capture full 14-stage end-to-end finalization with terminal certificate summary

v1.0.0 runtime workflow:
- launch/sync_ops_release_gate.json and launch/sync_ops_release_gate.md capture deterministic v1.0.0 release decision, version-specific checks, and required sign-offs

v1.0.1 runtime workflow:
- launch/sync_ops_audit_log.json and launch/sync_ops_audit_log.md capture deterministic post-release artifact audit with SHA-256 hashes across all terminal pipeline outputs

v1.0.2 runtime workflow:
- launch/sync_ops_audit_log_validation.json and launch/sync_ops_audit_log_validation.md capture deterministic audit-log integrity, artifact-hash, and release-gate consistency checks

v1.0.3 runtime workflow:
- launch/sync_ops_audit_assurance_pipeline.json and launch/sync_ops_audit_assurance_pipeline.md capture one-command deterministic finalization-through-audit-validation execution with stage outcomes and artifact hashes

v1.0.4 runtime workflow:
- launch/sync_ops_audit_assurance_pipeline_validation.json and launch/sync_ops_audit_assurance_pipeline_validation.md capture deterministic audit-assurance pipeline integrity and cross-artifact consistency checks

v1.0.5 runtime workflow:
- launch/sync_ops_audit_assurance_validation_pipeline.json and launch/sync_ops_audit_assurance_validation_pipeline.md capture one-command deterministic audit-assurance execution with downstream pipeline-validation verification and artifact hashes

v1.0.6 runtime workflow:
- launch/sync_ops_reproducibility_manifest.json and launch/sync_ops_reproducibility_manifest.md capture deterministic replay reproducibility across two audit-chain executions with artifact-level hash comparison

v1.0.7 runtime workflow:
- launch/sync_ops_reproducibility_manifest_validation.json and launch/sync_ops_reproducibility_manifest_validation.md capture deterministic reproducibility-manifest integrity and cross-artifact consistency validation

v1.0.8 runtime workflow:
- launch/sync_ops_reproducibility_validation_pipeline.json and launch/sync_ops_reproducibility_validation_pipeline.md capture one-command deterministic reproducibility generation with downstream manifest-validation verification and artifact hashes

Artifacts generated by scripts are written under these directories.
