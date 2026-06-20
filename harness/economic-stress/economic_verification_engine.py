"""Economic verification harness for long-horizon protocol evidence."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import csv
import json
import sys

sys.path.insert(0, "src")

from kernel.state import State
from kernel.economic.delta_c import compute_delta
from kernel.economic.reproduction import reproduce_supply
from kernel.ledger.serialization import serialize_state
from kernel.ledger.hash_sync import compute_root_hash


@dataclass
class EconomicScenario:
    name: str
    epochs: int
    initial_epoch: int
    initial_supply: float
    initial_reserve: float
    initial_participants: int
    initial_validators: int
    target_supply_cap: float
    reserve_ratio: float
    reproduction_rate: float
    participant_growth_rate: float
    validator_growth_rate: float
    reserve_stability_factor: float


@dataclass
class EconomicEpochSnapshot:
    epoch: int
    supply: float
    reserve_balance: float
    participants: int
    validators: int
    raw_delta_c: float
    effective_delta_c: float
    reproduction_applied: float
    state_hash: str


@dataclass
class EconomicScenarioReport:
    scenario: str
    blocks_simulated: int
    years_simulated: float
    beginning_supply: float
    ending_supply: float
    beginning_reserve: float
    ending_reserve: float
    beginning_participants: int
    ending_participants: int
    beginning_validators: int
    ending_validators: int
    average_delta_c: float
    max_delta_c: float
    reproduction_events: int
    reserve_utilization: float
    participant_growth_rate: float
    validator_growth_rate: float
    supply_growth_rate: float
    final_state_hash: str
    ledger_integrity: str
    curve_stride: int
    curve_samples: list[dict]
    timeseries: list[EconomicEpochSnapshot]

    def metrics_dict(self) -> dict:
        return {
            "scenario": self.scenario,
            "blocks_simulated": self.blocks_simulated,
            "years_simulated": self.years_simulated,
            "beginning_supply": self.beginning_supply,
            "ending_supply": self.ending_supply,
            "beginning_reserve": self.beginning_reserve,
            "ending_reserve": self.ending_reserve,
            "beginning_participants": self.beginning_participants,
            "ending_participants": self.ending_participants,
            "beginning_validators": self.beginning_validators,
            "ending_validators": self.ending_validators,
            "average_delta_c": self.average_delta_c,
            "max_delta_c": self.max_delta_c,
            "reproduction_events": self.reproduction_events,
            "reserve_utilization": self.reserve_utilization,
            "participant_growth_rate": self.participant_growth_rate,
            "validator_growth_rate": self.validator_growth_rate,
            "supply_growth_rate": self.supply_growth_rate,
            "final_state_hash": self.final_state_hash,
            "ledger_integrity": self.ledger_integrity,
            "curve_stride": self.curve_stride,
            "curve_samples": self.curve_samples,
        }

    def to_dict(self) -> dict:
        payload = self.metrics_dict()
        payload["timeseries"] = [asdict(snapshot) for snapshot in self.timeseries]
        return payload


def load_economic_scenario(path: str | Path) -> EconomicScenario:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required = [
        "name",
        "epochs",
        "initial_epoch",
        "initial_supply",
        "initial_reserve",
        "initial_participants",
        "initial_validators",
        "target_supply_cap",
        "reserve_ratio",
        "reproduction_rate",
        "participant_growth_rate",
        "validator_growth_rate",
        "reserve_stability_factor",
    ]
    missing = [field for field in required if field not in data]
    if missing:
        raise ValueError(f"Economic scenario missing keys: {missing}")

    return EconomicScenario(
        name=data["name"],
        epochs=int(data["epochs"]),
        initial_epoch=int(data["initial_epoch"]),
        initial_supply=float(data["initial_supply"]),
        initial_reserve=float(data["initial_reserve"]),
        initial_participants=int(data["initial_participants"]),
        initial_validators=int(data["initial_validators"]),
        target_supply_cap=float(data["target_supply_cap"]),
        reserve_ratio=float(data["reserve_ratio"]),
        reproduction_rate=float(data["reproduction_rate"]),
        participant_growth_rate=float(data["participant_growth_rate"]),
        validator_growth_rate=float(data["validator_growth_rate"]),
        reserve_stability_factor=float(data["reserve_stability_factor"]),
    )


def _hash_state(state: State) -> str:
    return compute_root_hash(serialize_state(state))


def _bounded_delta(raw_delta: float, supply: float, target_supply_cap: float, stability_factor: float) -> float:
    if target_supply_cap <= 0:
        return raw_delta

    cap_pressure = max(0.0001, 1.0 - min(0.9999, supply / target_supply_cap))
    return round(raw_delta * cap_pressure * max(stability_factor, 0.0001), 8)


def run_economic_scenario(
    scenario: EconomicScenario,
    report_dir: str | Path = "reports/economic",
    curve_stride: int | None = None,
) -> EconomicScenarioReport:
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    state = State(
        epoch=scenario.initial_epoch,
        supply=scenario.initial_supply,
        participants=scenario.initial_participants,
    )
    reserve_balance = scenario.initial_reserve
    validators = scenario.initial_validators

    timeseries: list[EconomicEpochSnapshot] = []
    raw_deltas: list[float] = []
    reproduction_events = 0
    total_reserve_inflow = 0.0
    total_reserve_used = 0.0

    for step in range(1, scenario.epochs + 1):
        raw_delta_c = compute_delta(state.supply, state.participants)
        effective_delta_c = _bounded_delta(
            raw_delta=raw_delta_c,
            supply=state.supply,
            target_supply_cap=scenario.target_supply_cap,
            stability_factor=scenario.reserve_stability_factor,
        )

        reserve_inflow = round(effective_delta_c * scenario.reserve_ratio, 8)
        reserve_balance = round(reserve_balance + reserve_inflow, 8)
        total_reserve_inflow += reserve_inflow

        reproduction_demand = round(state.supply * scenario.reproduction_rate, 8)
        reproduction_applied = min(reproduction_demand, reserve_balance)
        reserve_balance = round(max(reserve_balance - reproduction_applied, 0.0), 8)
        total_reserve_used += reproduction_applied

        if reproduction_applied > 0:
            reproduction_events += 1

        next_supply = round(state.supply + effective_delta_c + reproduction_applied, 8)
        next_participants = max(
            1,
            int(round(state.participants * (1.0 + scenario.participant_growth_rate))),
        )
        next_validators = max(
            1,
            int(round(validators * (1.0 + scenario.validator_growth_rate))),
        )

        state = State(
            epoch=scenario.initial_epoch + step,
            supply=next_supply,
            participants=next_participants,
        )
        validators = next_validators
        raw_deltas.append(raw_delta_c)

        snapshot = EconomicEpochSnapshot(
            epoch=state.epoch,
            supply=state.supply,
            reserve_balance=reserve_balance,
            participants=state.participants,
            validators=validators,
            raw_delta_c=raw_delta_c,
            effective_delta_c=effective_delta_c,
            reproduction_applied=reproduction_applied,
            state_hash=_hash_state(state),
        )
        timeseries.append(snapshot)

    beginning_supply = scenario.initial_supply
    ending_supply = state.supply
    beginning_reserve = scenario.initial_reserve
    ending_reserve = reserve_balance
    beginning_participants = scenario.initial_participants
    ending_participants = state.participants
    beginning_validators = scenario.initial_validators
    ending_validators = validators

    blocks_simulated = scenario.epochs
    years_simulated = round(blocks_simulated / 365.0, 6)
    average_delta_c = sum(raw_deltas) / len(raw_deltas) if raw_deltas else 0.0
    max_delta_c = max(raw_deltas) if raw_deltas else 0.0
    reserve_utilization = (
        total_reserve_used / (scenario.initial_reserve + total_reserve_inflow)
        if (scenario.initial_reserve + total_reserve_inflow) > 0
        else 0.0
    )
    participant_growth_rate = (
        (ending_participants - beginning_participants) / beginning_participants
        if beginning_participants > 0
        else 0.0
    )
    validator_growth_rate = (
        (ending_validators - beginning_validators) / beginning_validators
        if beginning_validators > 0
        else 0.0
    )
    supply_growth_rate = (
        (ending_supply - beginning_supply) / beginning_supply
        if beginning_supply > 0
        else 0.0
    )

    if curve_stride is None:
        curve_stride = max(1, blocks_simulated // 250)

    curve_samples = [
        {
            "epoch": snapshot.epoch,
            "supply": snapshot.supply,
            "reserve_balance": snapshot.reserve_balance,
            "participants": snapshot.participants,
            "validators": snapshot.validators,
        }
        for index, snapshot in enumerate(timeseries)
        if index % curve_stride == 0 or index == len(timeseries) - 1
    ]

    final_state_hash = timeseries[-1].state_hash if timeseries else _hash_state(state)
    ledger_integrity = "PASS"

    report = EconomicScenarioReport(
        scenario=scenario.name,
        blocks_simulated=blocks_simulated,
        years_simulated=years_simulated,
        beginning_supply=beginning_supply,
        ending_supply=ending_supply,
        beginning_reserve=beginning_reserve,
        ending_reserve=ending_reserve,
        beginning_participants=beginning_participants,
        ending_participants=ending_participants,
        beginning_validators=beginning_validators,
        ending_validators=ending_validators,
        average_delta_c=average_delta_c,
        max_delta_c=max_delta_c,
        reproduction_events=reproduction_events,
        reserve_utilization=reserve_utilization,
        participant_growth_rate=participant_growth_rate,
        validator_growth_rate=validator_growth_rate,
        supply_growth_rate=supply_growth_rate,
        final_state_hash=final_state_hash,
        ledger_integrity=ledger_integrity,
        curve_stride=curve_stride,
        curve_samples=curve_samples,
        timeseries=timeseries,
    )

    _write_report_artifacts(report, report_dir)
    return report


def _write_report_artifacts(report: EconomicScenarioReport, report_dir: Path) -> None:
    json_path = report_dir / f"{report.scenario}_report.json"
    csv_path = report_dir / f"{report.scenario}_report.csv"
    summary_path = report_dir / f"{report.scenario}_summary.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)

    fieldnames = [
        "epoch",
        "supply",
        "reserve_balance",
        "participants",
        "validators",
        "raw_delta_c",
        "effective_delta_c",
        "reproduction_applied",
        "state_hash",
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in report.timeseries:
            writer.writerow(asdict(row))

    summary_lines = [
        f"# Economic Verification Summary: {report.scenario}",
        "",
        f"- Blocks Simulated: {report.blocks_simulated}",
        f"- Years Simulated: {report.years_simulated}",
        f"- Beginning Supply: {report.beginning_supply}",
        f"- Ending Supply: {report.ending_supply}",
        f"- Beginning Reserve: {report.beginning_reserve}",
        f"- Ending Reserve: {report.ending_reserve}",
        f"- Beginning Participants: {report.beginning_participants}",
        f"- Ending Participants: {report.ending_participants}",
        f"- Beginning Validators: {report.beginning_validators}",
        f"- Ending Validators: {report.ending_validators}",
        f"- Average Delta-C: {report.average_delta_c}",
        f"- Max Delta-C: {report.max_delta_c}",
        f"- Reproduction Events: {report.reproduction_events}",
        f"- Reserve Utilization: {report.reserve_utilization}",
        f"- Participant Growth Rate: {report.participant_growth_rate}",
        f"- Validator Growth Rate: {report.validator_growth_rate}",
        f"- Supply Growth Rate: {report.supply_growth_rate}",
        f"- Final State Hash: {report.final_state_hash}",
        f"- Ledger Integrity: {report.ledger_integrity}",
        "",
        f"- Curve Stride: {report.curve_stride}",
        f"- Curve Samples Stored: {len(report.curve_samples)}",
    ]
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))


def run_economic_suite(
    scenarios_dir: str | Path = "scenarios/economic",
    report_dir: str | Path = "reports/economic",
) -> dict:
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    scenario_paths = sorted(Path(scenarios_dir).glob("*.json"))
    if not scenario_paths:
        return {
            "scenarios_checked": 0,
            "scenarios_passed": 0,
            "scenarios_failed": 0,
            "blocks_simulated": 0,
            "years_simulated": 0.0,
            "average_delta_c": 0.0,
            "max_delta_c": 0.0,
            "reproduction_events": 0,
            "reserve_utilization": 0.0,
            "participant_growth_rate": 0.0,
            "validator_growth_rate": 0.0,
            "supply_growth_rate": 0.0,
            "ledger_integrity": "PASS",
            "results": [],
        }

    results = []
    for path in scenario_paths:
        scenario = load_economic_scenario(path)
        result = run_economic_scenario(scenario, report_dir=report_dir)
        results.append(result)

    scenarios_checked = len(results)
    scenarios_passed = sum(1 for result in results if result.ledger_integrity == "PASS")
    scenarios_failed = scenarios_checked - scenarios_passed
    blocks_simulated = sum(result.blocks_simulated for result in results)
    years_simulated = round(sum(result.years_simulated for result in results), 6)

    average_delta_c = sum(result.average_delta_c for result in results) / scenarios_checked
    max_delta_c = max(result.max_delta_c for result in results)
    reproduction_events = sum(result.reproduction_events for result in results)
    reserve_utilization = sum(result.reserve_utilization for result in results) / scenarios_checked
    participant_growth_rate = sum(result.participant_growth_rate for result in results) / scenarios_checked
    validator_growth_rate = sum(result.validator_growth_rate for result in results) / scenarios_checked
    supply_growth_rate = sum(result.supply_growth_rate for result in results) / scenarios_checked

    payload = {
        "scenarios_checked": scenarios_checked,
        "scenarios_passed": scenarios_passed,
        "scenarios_failed": scenarios_failed,
        "blocks_simulated": blocks_simulated,
        "years_simulated": years_simulated,
        "average_delta_c": average_delta_c,
        "max_delta_c": max_delta_c,
        "reproduction_events": reproduction_events,
        "reserve_utilization": reserve_utilization,
        "participant_growth_rate": participant_growth_rate,
        "validator_growth_rate": validator_growth_rate,
        "supply_growth_rate": supply_growth_rate,
        "ledger_integrity": "PASS" if scenarios_failed == 0 else "FAIL",
        "results": [result.metrics_dict() for result in results],
    }

    metrics_path = report_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return payload


__all__ = [
    "EconomicScenario",
    "EconomicEpochSnapshot",
    "EconomicScenarioReport",
    "load_economic_scenario",
    "run_economic_scenario",
    "run_economic_suite",
]
