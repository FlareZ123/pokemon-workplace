"""Model the unresolved *same physical Stadium copy* re-entry usage question.

This adapter owns no duplicate Stadium zones. StadiumEntryState is the only
material owner; every change in the Stadium zone delegates to the existing
entry kernel. Each observed entry gets a monotonically increasing epoch.

Official Brooklet Hill Q&A establishes a fresh use for a *different copy*
after replacement. It does not directly settle whether a used physical copy
that leaves play and returns later in the same turn can activate again.
Consequently the return-copy policies here are explicit model alternatives,
not purported tournament rulings.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from stadium_entry_channels import StadiumEntryState, teleport_room_options
from stadium_effect_instance_usage import (
    StadiumCard,
    StadiumEffectState,
    StadiumInPlay,
    use_current_stadium_effect,
)

UsagePolicy = Literal["entry", "physical_copy", "name"]


@dataclass(frozen=True)
class StadiumUse:
    epoch: int
    copy_id: str
    name: str


@dataclass(frozen=True)
class StadiumReentryState:
    entry: StadiumEntryState
    epoch: int = 0
    uses: tuple[StadiumUse, ...] = ()

    def __post_init__(self) -> None:
        if self.epoch < 0 or any(use.epoch > self.epoch for use in self.uses):
            raise ValueError("Stadium-use epochs must be nonnegative and ordered")
        if len({use.epoch for use in self.uses}) != len(self.uses):
            raise ValueError("One voluntary use is permitted per entry epoch")

    def effect_view(self) -> StadiumEffectState:
        """Project a transient effect source without duplicating the inventory."""
        live = self.entry.in_play
        projected = (
            StadiumInPlay(StadiumCard(live.copy_id, live.name), str(self.epoch))
            if live is not None
            else None
        )
        return StadiumEffectState(
            budget=self.entry.budget,
            in_play=projected,
            used_effect_instances=frozenset(str(use.epoch) for use in self.uses),
        )


def can_activate(
    state: StadiumReentryState,
    policy: UsagePolicy,
    *,
    stadium_name: str = "Grand Tree",
) -> bool:
    """Interpret a once-per-turn voluntary use under a declared identity scope."""
    if policy not in ("entry", "physical_copy", "name"):
        raise ValueError("Unknown stadium-use policy")
    live = state.entry.in_play
    if state.entry.budget.turn_ended or live is None or live.name != stadium_name:
        return False
    if policy == "entry":
        return all(use.epoch != state.epoch for use in state.uses)
    if policy == "physical_copy":
        return all(use.copy_id != live.copy_id for use in state.uses)
    return all(use.name != live.name for use in state.uses)


def activate(
    state: StadiumReentryState,
    policy: UsagePolicy,
    *,
    stadium_name: str = "Grand Tree",
) -> StadiumReentryState | None:
    """Record one successful abstract Stadium activation.

    Physical evolutionary targets and deck search are intentionally outside
    this identity-scope adapter. Call only after a legal effect body succeeds.
    """
    if not can_activate(state, policy, stadium_name=stadium_name):
        return None
    effect = use_current_stadium_effect(state.effect_view())
    if effect is None:
        return None
    live = state.entry.in_play
    assert live is not None
    assert str(state.epoch) in effect.used_effect_instances
    return replace(
        state,
        uses=state.uses + (StadiumUse(state.epoch, live.copy_id, live.name),),
    )


def teleport_successors(
    state: StadiumReentryState,
    source_id: str,
) -> tuple[StadiumReentryState, ...]:
    """Enumerate actual Gothitelle moves; one entry epoch per new occupant."""
    out = []
    for next_entry in teleport_room_options(state.entry, source_id):
        if next_entry.in_play is None:
            out.append(replace(state, entry=next_entry))
        else:
            out.append(replace(state, entry=next_entry, epoch=state.epoch + 1))
    return tuple(out)


def max_activations(
    initial: StadiumReentryState,
    policy: UsagePolicy,
    *,
    stadium_name: str = "Grand Tree",
) -> tuple[int, tuple[str, ...]]:
    """Exhaustively search a finite turn with fixed Teleport Room sources.

    Only permitted actions: activate the named Stadium effect or use one
    remaining Gothitelle source. Ordinary Stadium play is excluded, so the
    benchmark uses a pre-spent Stadium-play allowance.
    """
    agenda = [(initial, ())]
    seen = {initial}
    best = (len(initial.uses), ())
    while agenda:
        state, trace = agenda.pop()
        if len(state.uses) > best[0]:
            best = (len(state.uses), trace)
        after_use = activate(state, policy, stadium_name=stadium_name)
        if after_use is not None and after_use not in seen:
            seen.add(after_use)
            agenda.append((after_use, trace + ("use:" + after_use.uses[-1].copy_id,)))
        for source in sorted(
            state.entry.teleport_room_sources - state.entry.teleport_room_used
        ):
            for successor in teleport_successors(state, source):
                if successor not in seen:
                    seen.add(successor)
                    name = (
                        successor.entry.in_play.copy_id
                        if successor.entry.in_play is not None
                        else "empty"
                    )
                    agenda.append((successor, trace + (source + "->" + name,)))
    return best
