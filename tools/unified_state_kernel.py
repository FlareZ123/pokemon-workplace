"""Compositional deterministic state kernel for representative Expanded lines.

This module connects existing repository kernels rather than replacing them. It
keeps one canonical card-zone map while composing:

- Bench residency/capacity state;
- typed play-lock channels and per-Pokemon Tool state;
- Supporter, Stadium, and manual-Energy action windows;
- typed Energy supply and attack-cost reductions;
- grouped Prize beliefs through a belief-weighted reachability adapter.

The represented actions are deliberately narrow. The purpose is to establish a
safe composition boundary for larger planners, not to parse arbitrary card text.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field, replace
from enum import Enum
from math import fsum
from typing import Mapping, Sequence

from bench_state_kernel import (
    BenchResident,
    BenchState,
    change_capacity as change_bench_capacity_state,
)
from energy_action_budget import (
    EnergyRouteProfile,
    EnergyRouteType,
    evaluate_energy_routes,
    unit,
)
from lock_state_kernel import (
    PlayerChannels,
    PokemonState,
    apply_play_lock,
    stealthy_hood_protects,
    suppress_tool_effect,
)
from prize_belief_kernel import PrizeBelief


class Zone(str, Enum):
    DECK = "deck"
    HAND = "hand"
    BENCH = "bench"
    ACTIVE = "active"
    PRIZE = "prize"
    DISCARD = "discard"
    ATTACHED = "attached"
    STADIUM = "stadium"


@dataclass(frozen=True)
class UnifiedState:
    """Small immutable state shared by several mechanical submodels."""

    locations: tuple[tuple[str, str], ...]
    bench: BenchState = field(default_factory=BenchState)
    channels: PlayerChannels = field(default_factory=PlayerChannels)
    active_name: str | None = None
    active_pokemon: PokemonState = field(default_factory=PokemonState)
    active_tags: frozenset[str] = frozenset()
    abilities_allowed: bool = True
    manual_attachment_used: bool = False
    stadium_used: bool = False
    attached_units: tuple[str, ...] = ()
    attack_reductions: tuple[tuple[str, int], ...] = ()
    attacks_allowed: bool = True
    gladion_played: bool = False

    def zone(self, card: str) -> str | None:
        return dict(self.locations).get(card)


Transition = tuple[str, UnifiedState]


def make_state(
    locations: Mapping[str, str],
    *,
    bench: BenchState | None = None,
    channels: PlayerChannels | None = None,
    active_name: str | None = None,
    active_pokemon: PokemonState | None = None,
    active_tags: frozenset[str] | None = None,
    **kwargs: object,
) -> UnifiedState:
    state = UnifiedState(
        locations=tuple(sorted(locations.items())),
        bench=bench if bench is not None else BenchState(),
        channels=channels if channels is not None else PlayerChannels(),
        active_name=active_name,
        active_pokemon=(
            active_pokemon if active_pokemon is not None else PokemonState()
        ),
        active_tags=active_tags if active_tags is not None else frozenset(),
        **kwargs,
    )
    validate_state(state)
    return state


def validate_state(state: UnifiedState) -> None:
    """Check cross-kernel invariants that are meaningful in this scaffold."""

    if len(state.bench.residents) > state.bench.capacity:
        raise ValueError("Bench residents exceed current capacity")

    for resident in state.bench.residents:
        if state.zone(resident.name) != Zone.BENCH.value:
            raise ValueError(
                f"Bench resident {resident.name!r} is not in the Bench zone"
            )

    if state.active_name is not None:
        if state.zone(state.active_name) != Zone.ACTIVE.value:
            raise ValueError("active_name is not in the Active zone")


def _move(state: UnifiedState, card: str, zone: Zone) -> UnifiedState:
    locations = dict(state.locations)
    locations[card] = zone.value
    return replace(state, locations=tuple(sorted(locations.items())))


def _add_bench_resident(
    state: UnifiedState,
    *,
    name: str,
    role: str,
    retention_value: float,
    trigger_name: str | None = None,
) -> UnifiedState | None:
    bench = state.bench
    if bench.turn_ended or len(bench.residents) >= bench.capacity:
        return None
    resident = BenchResident(
        name=name,
        role=role,
        retention_value=retention_value,
        trigger_name=trigger_name,
    )
    next_state = replace(
        state,
        bench=replace(bench, residents=bench.residents + (resident,)),
    )
    next_state = _move(next_state, name, Zone.BENCH)
    validate_state(next_state)
    return next_state


def apply_lock(state: UnifiedState, dimension: str) -> UnifiedState:
    """Apply one typed play lock from the existing lock-state kernel."""

    return replace(state, channels=apply_play_lock(state.channels, dimension))


def quick_ball_for_tapu_lele(state: UnifiedState) -> list[Transition]:
    if not state.channels.item_play:
        return []
    if (
        state.zone("Quick Ball") != Zone.HAND.value
        or state.zone("Fodder") != Zone.HAND.value
        or state.zone("Tapu Lele-GX") != Zone.DECK.value
    ):
        return []

    next_state = _move(state, "Quick Ball", Zone.DISCARD)
    next_state = _move(next_state, "Fodder", Zone.DISCARD)
    next_state = _move(next_state, "Tapu Lele-GX", Zone.HAND)
    return [("Quick Ball -> Tapu Lele-GX to hand", next_state)]


def nest_ball_for_tapu_lele(state: UnifiedState) -> list[Transition]:
    """Put Lele directly on the Bench, deliberately skipping Wonder Tag."""

    if not state.channels.item_play:
        return []
    if (
        state.zone("Nest Ball") != Zone.HAND.value
        or state.zone("Tapu Lele-GX") != Zone.DECK.value
    ):
        return []

    next_state = _move(state, "Nest Ball", Zone.DISCARD)
    next_state = _add_bench_resident(
        next_state,
        name="Tapu Lele-GX",
        role="support",
        retention_value=1.0,
        trigger_name="Wonder Tag",
    )
    if next_state is None:
        return []
    return [("Nest Ball -> Tapu Lele-GX directly to Bench", next_state)]


def play_tapu_lele_from_hand(state: UnifiedState) -> list[Transition]:
    if state.zone("Tapu Lele-GX") != Zone.HAND.value:
        return []

    next_state = _add_bench_resident(
        state,
        name="Tapu Lele-GX",
        role="support",
        retention_value=1.0,
        trigger_name="Wonder Tag",
    )
    if next_state is None:
        return []

    if (
        next_state.abilities_allowed
        and next_state.zone("Gladion") == Zone.DECK.value
    ):
        next_state = _move(next_state, "Gladion", Zone.HAND)
        return [
            (
                "Play Tapu Lele-GX from hand; Wonder Tag -> Gladion",
                next_state,
            )
        ]

    return [("Play Tapu Lele-GX from hand", next_state)]


def play_gladion(state: UnifiedState) -> list[Transition]:
    if (
        not state.channels.supporter_play
        or state.bench.supporter_used
        or state.bench.turn_ended
        or state.zone("Gladion") != Zone.HAND.value
    ):
        return []

    next_state = _move(state, "Gladion", Zone.DISCARD)
    next_state = replace(
        next_state,
        bench=replace(next_state.bench, supporter_used=True),
        gladion_played=True,
    )
    return [("Play Gladion", next_state)]


GLADION_ACTIONS = (
    quick_ball_for_tapu_lele,
    nest_ball_for_tapu_lele,
    play_tapu_lele_from_hand,
    play_gladion,
)


def shortest_gladion_line(
    initial_state: UnifiedState,
    *,
    max_actions: int = 6,
) -> tuple[list[str], UnifiedState] | None:
    """Find the shortest represented current-turn line that plays Gladion."""

    queue: deque[tuple[UnifiedState, list[str]]] = deque([(initial_state, [])])
    seen = {initial_state}

    while queue:
        state, line = queue.popleft()
        if state.gladion_played:
            return line, state
        if len(line) >= max_actions:
            continue

        for action in GLADION_ACTIONS:
            for label, next_state in action(state):
                if next_state in seen:
                    continue
                seen.add(next_state)
                queue.append((next_state, line + [label]))

    return None


def attach_tool_to_active(
    state: UnifiedState,
    *,
    card: str,
) -> UnifiedState | None:
    """Attach one modeled Tool while keeping Item and Tool channels distinct."""

    if (
        not state.channels.tool_play
        or state.active_name is None
        or state.active_pokemon.tool_attached
        or state.zone(card) != Zone.HAND.value
    ):
        return None

    next_state = _move(state, card, Zone.ATTACHED)
    next_state = replace(
        next_state,
        active_pokemon=replace(
            next_state.active_pokemon,
            tool_attached=True,
            tool_effect_enabled=True,
        ),
    )
    return next_state


def suppress_active_tool_effect(state: UnifiedState) -> UnifiedState:
    return replace(
        state,
        active_pokemon=suppress_tool_effect(state.active_pokemon),
    )


def active_tool_protects(state: UnifiedState) -> bool:
    return stealthy_hood_protects(state.active_pokemon)


def attach_dce_to_active(state: UnifiedState) -> UnifiedState | None:
    if (
        not state.channels.special_energy_play
        or state.manual_attachment_used
        or state.active_name is None
        or state.zone("Double Colorless Energy") != Zone.HAND.value
    ):
        return None

    next_state = _move(state, "Double Colorless Energy", Zone.ATTACHED)
    return replace(
        next_state,
        manual_attachment_used=True,
        attached_units=next_state.attached_units + ("C", "C"),
    )


def play_thunder_mountain(state: UnifiedState) -> UnifiedState | None:
    if (
        not state.channels.stadium_play
        or state.stadium_used
        or state.zone("Thunder Mountain Prism Star") != Zone.HAND.value
    ):
        return None

    next_state = _move(state, "Thunder Mountain Prism Star", Zone.STADIUM)
    reductions = next_state.attack_reductions
    if "Lightning" in next_state.active_tags:
        reductions = reductions + (("L", 1),)
    return replace(
        next_state,
        stadium_used=True,
        attack_reductions=reductions,
    )


def attack_ready(
    state: UnifiedState,
    attack_cost: Sequence[str],
) -> bool:
    """Evaluate current attached Energy and active reductions exactly."""

    if not state.attacks_allowed or state.active_name is None:
        return False
    if not state.attached_units and not state.attack_reductions:
        return False

    route = EnergyRouteType(
        "current active Energy state",
        1,
        (
            EnergyRouteProfile(
                units=tuple(unit(symbol) for symbol in state.attached_units),
                reductions=state.attack_reductions,
            ),
        ),
    )
    return evaluate_energy_routes(
        attack_cost,
        {},
        state.active_tags,
        (route,),
    ).exact_feasible


def change_bench_capacity(
    state: UnifiedState,
    *,
    new_capacity: int,
) -> tuple[UnifiedState, tuple[BenchResident, ...]]:
    """Apply Bench contraction and synchronize discarded residents' zones."""

    next_bench, discarded = change_bench_capacity_state(
        state.bench,
        new_capacity=new_capacity,
    )
    next_state = replace(state, bench=next_bench)
    for resident in discarded:
        if next_state.zone(resident.name) == Zone.BENCH.value:
            next_state = _move(next_state, resident.name, Zone.DISCARD)
    validate_state(next_state)
    return next_state, discarded


def apply_singleton_prize_state(
    base_state: UnifiedState,
    prize_counts: Mapping[str, int],
    singleton_groups: Mapping[str, str],
) -> UnifiedState:
    """Instantiate one grouped Prize state for modeled singleton cards.

    Every mapped group represents one physical card that must be in the deck in
    the deterministic base state. This adapter is intentionally conservative:
    multi-copy groups need a richer identity representation.
    """

    state = base_state
    for group, card in singleton_groups.items():
        count = prize_counts.get(group, 0)
        if count not in {0, 1}:
            raise ValueError("singleton Prize groups must have count 0 or 1")
        if base_state.zone(card) != Zone.DECK.value:
            raise ValueError(
                f"Prize-mapped singleton {card!r} must start in the deck"
            )
        if count == 1:
            state = _move(state, card, Zone.PRIZE)
    return state


def gladion_access_probability(
    base_state: UnifiedState,
    belief: PrizeBelief,
    singleton_groups: Mapping[str, str],
) -> float:
    """Return belief-weighted probability that the represented line can play Gladion."""

    if set(singleton_groups) - set(belief.groups):
        raise ValueError("singleton_groups must be represented in the Prize belief")

    masses: list[float] = []
    for prize_counts, probability in belief.state_dicts():
        state = apply_singleton_prize_state(
            base_state,
            prize_counts,
            singleton_groups,
        )
        if shortest_gladion_line(state) is not None:
            masses.append(probability)
    return fsum(masses)
