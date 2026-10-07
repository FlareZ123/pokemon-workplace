from __future__ import annotations

from dataclasses import dataclass, replace

from bench_capacity_transition import BenchOccupant, resolve_capacity_transition


@dataclass(frozen=True)
class BenchResident:
    name: str
    role: str
    retention_value: float
    trigger_name: str | None = None


@dataclass(frozen=True)
class BenchState:
    turn: int = 1
    capacity: int = 5
    residents: tuple[BenchResident, ...] = ()
    trigger_counts: tuple[tuple[str, int], ...] = ()
    supporter_used: bool = False
    turn_ended: bool = False

    def trigger_count(self, name: str) -> int:
        return dict(self.trigger_counts).get(name, 0)


def _with_trigger(state: BenchState, trigger_name: str) -> BenchState:
    counts = dict(state.trigger_counts)
    counts[trigger_name] = counts.get(trigger_name, 0) + 1
    return replace(state, trigger_counts=tuple(sorted(counts.items())))


def add_core(state: BenchState, *, name: str, retention_value: float) -> BenchState | None:
    if state.turn_ended or len(state.residents) >= state.capacity:
        return None
    resident = BenchResident(name=name, role="core", retention_value=retention_value)
    return replace(state, residents=state.residents + (resident,))


def add_support(
    state: BenchState,
    *,
    name: str,
    retention_value: float,
    trigger_name: str,
    entry_mode: str,
) -> BenchState | None:
    """Bench a transactional support with typed entry-zone semantics."""

    if entry_mode not in {"hand", "direct"}:
        raise ValueError("entry_mode must be 'hand' or 'direct'")
    if state.turn_ended or len(state.residents) >= state.capacity:
        return None

    resident = BenchResident(
        name=name,
        role="support",
        retention_value=retention_value,
        trigger_name=trigger_name,
    )
    next_state = replace(state, residents=state.residents + (resident,))
    if entry_mode == "hand":
        next_state = _with_trigger(next_state, trigger_name)
    return next_state


def release_resident(
    state: BenchState,
    *,
    resident_index: int,
    action_class: str,
) -> BenchState | None:
    """Remove one resident through a typed release action."""

    if action_class not in {"item", "ability", "supporter", "attack"}:
        raise ValueError("unknown action_class")
    if state.turn_ended or not 0 <= resident_index < len(state.residents):
        return None
    if action_class == "supporter" and state.supporter_used:
        return None

    residents = state.residents[:resident_index] + state.residents[resident_index + 1 :]
    return replace(
        state,
        residents=residents,
        supporter_used=state.supporter_used or action_class == "supporter",
        turn_ended=action_class == "attack",
    )


def next_turn(state: BenchState) -> BenchState:
    return replace(
        state,
        turn=state.turn + 1,
        supporter_used=False,
        turn_ended=False,
    )


def change_capacity(
    state: BenchState,
    *,
    new_capacity: int,
) -> tuple[BenchState, tuple[BenchResident, ...]]:
    """Change capacity and discard lowest-value residents when required."""

    if new_capacity < 0:
        raise ValueError("new_capacity must be non-negative")
    if len(state.residents) <= new_capacity:
        return replace(state, capacity=new_capacity), ()

    occupants = tuple(
        BenchOccupant(row.name, row.role, row.retention_value)
        for row in state.residents
    )
    resolved = resolve_capacity_transition(
        occupants,
        old_capacity=max(state.capacity, len(state.residents)),
        new_capacity=new_capacity,
    )

    retained_keys = {(row.name, row.role, row.retention_value) for row in resolved.retained}
    retained: list[BenchResident] = []
    discarded: list[BenchResident] = []
    for row in state.residents:
        key = (row.name, row.role, row.retention_value)
        if key in retained_keys:
            retained.append(row)
            retained_keys.remove(key)
        else:
            discarded.append(row)

    return (
        replace(state, capacity=new_capacity, residents=tuple(retained)),
        tuple(discarded),
    )
