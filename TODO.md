# TODO

## Completed
- [x] Update `ROADMAP_v2.md` v5.0.1 intro to emphasize deterministic integration only (no new economic policy)
- [x] Reformat v5.0.1 integration flow into clear subsystem pipelines
- [x] Add v5.0.1 Objectives subsection with governance, contracts, runtime coordination, metrics/monitoring, and end-to-end deterministic replay validation
- [x] Verify updated `ROADMAP_v2.md` section content

## Full Refactor Mode — Legacy Test Migration to Current Architecture
- [ ] Events: refactor `tests/events/test_event_bus.py` to current `EventBus` API (`publish_event`, current subscribe/unsubscribe semantics)
- [ ] Economics State: refactor `tests/economics/test_state.py` to `EconomicState`/`EconomicAccount`/`SupplyInfo`/`ReserveInfo` current model
- [ ] Economics Executor: refactor `tests/economics/test_executor.py` to current `EconomicOperation` fields (`from_account`, `to_account`) and executor methods (`get_execution_count`)
- [ ] Economics Transition/Snapshot/Validator/Metrics/Engine: refactor remaining economics tests to current APIs
- [ ] Determinism economic test: align to current economics API surface
- [ ] Re-run targeted suites and iterate until green:
  - [ ] `tests/events/test_event_bus.py`
  - [ ] `tests/economics`
  - [ ] `tests/deterministic/test_economic_determinism.py`
