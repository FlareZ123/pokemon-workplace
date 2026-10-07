"""Conservative deferral kernel for effects triggered during another effect."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActiveEffect:
    effect_id: str
    remaining_steps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.effect_id:
            raise ValueError("effect_id must be non-empty")
        if not self.remaining_steps:
            raise ValueError("active effect must have at least one remaining step")
        if any(not step for step in self.remaining_steps):
            raise ValueError("effect step labels must be non-empty")


@dataclass(frozen=True)
class TriggerDeferralState:
    ready_effects: frozenset[str] = frozenset()
    active: ActiveEffect | None = None
    deferred_effects: frozenset[str] = frozenset()
    completed_effects: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        all_ids = set(self.ready_effects) | set(self.deferred_effects)
        if self.active is not None:
            all_ids.add(self.active.effect_id)
        all_ids.update(self.completed_effects)
        expected = (
            len(self.ready_effects)
            + len(self.deferred_effects)
            + (1 if self.active is not None else 0)
            + len(self.completed_effects)
        )
        if len(all_ids) != expected:
            raise ValueError("effect IDs must occupy exactly one scheduler state")
        if any(not effect_id for effect_id in all_ids):
            raise ValueError("effect IDs must be non-empty")


def make_trigger_state(*ready_effect_ids: str) -> TriggerDeferralState:
    if len(ready_effect_ids) != len(set(ready_effect_ids)):
        raise ValueError("ready effect IDs must be unique")
    return TriggerDeferralState(frozenset(ready_effect_ids))


def start_ready_effect(
    state: TriggerDeferralState,
    *,
    effect_id: str,
    steps: tuple[str, ...],
) -> TriggerDeferralState | None:
    """Start one caller-selected ready effect.

    Ordering authority is deliberately upstream. The caller may select any
    member of ready_effects only while no effect is currently resolving.
    """

    if state.active is not None or effect_id not in state.ready_effects:
        return None

    return TriggerDeferralState(
        ready_effects=state.ready_effects - {effect_id},
        active=ActiveEffect(effect_id, steps),
        deferred_effects=state.deferred_effects,
        completed_effects=state.completed_effects,
    )


def record_trigger(
    state: TriggerDeferralState,
    *,
    effect_id: str,
) -> TriggerDeferralState | None:
    """Record an effect that has just become triggered.

    A trigger created while another effect is resolving is deferred. A trigger
    created while no effect is active becomes immediately ready.
    """

    occupied = (
        set(state.ready_effects)
        | set(state.deferred_effects)
        | set(state.completed_effects)
    )
    if state.active is not None:
        occupied.add(state.active.effect_id)
    if not effect_id or effect_id in occupied:
        return None

    if state.active is None:
        return TriggerDeferralState(
            ready_effects=state.ready_effects | {effect_id},
            completed_effects=state.completed_effects,
        )

    return TriggerDeferralState(
        ready_effects=state.ready_effects,
        active=state.active,
        deferred_effects=state.deferred_effects | {effect_id},
        completed_effects=state.completed_effects,
    )


def resolve_next_step(
    state: TriggerDeferralState,
) -> tuple[str, TriggerDeferralState] | None:
    """Resolve the next step of the active effect.

    Newly triggered effects become ready only after the active effect has no
    remaining steps. This models the non-interruption boundary without deciding
    which ready effect should be chosen next.
    """

    if state.active is None:
        return None

    step = state.active.remaining_steps[0]
    remaining = state.active.remaining_steps[1:]

    if remaining:
        return (
            step,
            TriggerDeferralState(
                ready_effects=state.ready_effects,
                active=ActiveEffect(state.active.effect_id, remaining),
                deferred_effects=state.deferred_effects,
                completed_effects=state.completed_effects,
            ),
        )

    return (
        step,
        TriggerDeferralState(
            ready_effects=state.ready_effects | state.deferred_effects,
            active=None,
            deferred_effects=frozenset(),
            completed_effects=state.completed_effects + (state.active.effect_id,),
        ),
    )
