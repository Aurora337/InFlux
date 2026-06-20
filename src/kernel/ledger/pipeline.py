try:
    from kernel.state import State
    from kernel.economic.delta_c import compute_delta
except ModuleNotFoundError:
    from state import State
    from economic.delta_c import compute_delta


def process_pipeline(state: State) -> State:

    delta = compute_delta(
        state.supply,
        state.participants
    )

    return State(
        epoch=state.epoch + 1,
        supply=state.supply + delta,
        participants=state.participants
    )
