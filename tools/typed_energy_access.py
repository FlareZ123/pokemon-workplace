"""Typed zone/action search for representative Energy setup lines.

This scaffold composes card-zone transitions with the exact Energy action budget
semantics in energy_action_budget.py. It deliberately models a small set of
Expanded lines rather than arbitrary card text.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable

from energy_action_budget import (
    EnergyRouteProfile,
    EnergyRouteType,
    evaluate_energy_routes,
    unit,
)


class Zone(str, Enum):
    DECK = "deck"
    HAND = "hand"
    DISCARD = "discard"
    PLAY = "play"
    ACTIVE = "active"
    ATTACHED = "attached"


@dataclass(frozen=True)
class EnergyAccessState:
    locations: tuple[tuple[str, str], ...]
    supporter_used: bool = False
    stadium_used: bool = False
    manual_attachment_used: bool = False
    thunder_mountain_active: bool = False
    attached_units: tuple[str, ...] = ()
    items_allowed: bool = True
    supporters_allowed: bool = True
    stadiums_allowed: bool = True
    manual_attachment_allowed: bool = True
    attacks_allowed: bool = True

    def zone(self, card: str) -> str | None:
        return dict(self.locations).get(card)


Transition = tuple[str, EnergyAccessState]
Action = Callable[[EnergyAccessState], list[Transition]]


def make_state(locations: dict[str, str], **kwargs: object) -> EnergyAccessState:
    return EnergyAccessState(tuple(sorted(locations.items())), **kwargs)


def _move(state: EnergyAccessState, card: str, zone: Zone) -> EnergyAccessState:
    locations = dict(state.locations)
    locations[card] = zone.value
    return replace(state, locations=tuple(sorted(locations.items())))


def tag_call_for_guzma_hala(state: EnergyAccessState) -> list[Transition]:
    if not state.items_allowed:
        return []
    if (
        state.zone("Tag Call") != Zone.HAND.value
        or state.zone("Guzma & Hala") != Zone.DECK.value
    ):
        return []
    next_state = _move(state, "Tag Call", Zone.DISCARD)
    next_state = _move(next_state, "Guzma & Hala", Zone.HAND)
    return [("Tag Call -> Guzma & Hala to hand", next_state)]


def guzma_hala_search(state: EnergyAccessState) -> list[Transition]:
    if not state.supporters_allowed or state.supporter_used:
        return []
    if (
        state.zone("Guzma & Hala") != Zone.HAND.value
        or state.zone("Thunder Mountain Prism Star") != Zone.DECK.value
    ):
        return []

    base = _move(state, "Guzma & Hala", Zone.DISCARD)
    base = _move(base, "Thunder Mountain Prism Star", Zone.HAND)
    base = replace(base, supporter_used=True)
    transitions: list[Transition] = [
        ("Play Guzma & Hala -> Thunder Mountain Prism Star to hand", base)
    ]

    if (
        state.zone("Double Colorless Energy") == Zone.DECK.value
        and state.zone("Fodder A") == Zone.HAND.value
        and state.zone("Fodder B") == Zone.HAND.value
    ):
        enhanced = _move(base, "Fodder A", Zone.DISCARD)
        enhanced = _move(enhanced, "Fodder B", Zone.DISCARD)
        enhanced = _move(enhanced, "Double Colorless Energy", Zone.HAND)
        transitions.append(
            (
                "Play Guzma & Hala; discard 2 -> Thunder Mountain + DCE to hand",
                enhanced,
            )
        )
    return transitions


def play_thunder_mountain(state: EnergyAccessState) -> list[Transition]:
    if not state.stadiums_allowed or state.stadium_used:
        return []
    if state.zone("Thunder Mountain Prism Star") != Zone.HAND.value:
        return []
    next_state = _move(state, "Thunder Mountain Prism Star", Zone.PLAY)
    next_state = replace(
        next_state,
        stadium_used=True,
        thunder_mountain_active=True,
    )
    return [("Play Thunder Mountain Prism Star", next_state)]


def attach_dce_to_iron_thorns(state: EnergyAccessState) -> list[Transition]:
    if (
        not state.manual_attachment_allowed
        or state.manual_attachment_used
        or state.zone("Double Colorless Energy") != Zone.HAND.value
        or state.zone("Iron Thorns ex") != Zone.ACTIVE.value
    ):
        return []
    next_state = _move(state, "Double Colorless Energy", Zone.ATTACHED)
    next_state = replace(
        next_state,
        manual_attachment_used=True,
        attached_units=state.attached_units + ("C", "C"),
    )
    return [("Attach Double Colorless Energy to Iron Thorns ex", next_state)]


def volt_cyclone_ready(state: EnergyAccessState) -> bool:
    if not state.attacks_allowed:
        return False
    if state.zone("Iron Thorns ex") != Zone.ACTIVE.value:
        return False

    routes: list[EnergyRouteType] = []
    if state.attached_units:
        routes.append(
            EnergyRouteType(
                "already attached Energy",
                1,
                (
                    EnergyRouteProfile(
                        units=tuple(unit(symbol) for symbol in state.attached_units),
                    ),
                ),
            )
        )
    if state.thunder_mountain_active:
        routes.append(
            EnergyRouteType(
                "active Thunder Mountain Prism Star",
                1,
                (
                    EnergyRouteProfile(
                        reductions=(("L", 1),),
                        required_target_tags=frozenset({"Lightning"}),
                    ),
                ),
            )
        )
    if not routes:
        return False

    return evaluate_energy_routes(
        ("L", "C", "C"),
        {},
        {"Lightning", "Basic"},
        routes,
    ).exact_feasible


IRON_THORNS_ACTIONS: tuple[Action, ...] = (
    tag_call_for_guzma_hala,
    guzma_hala_search,
    play_thunder_mountain,
    attach_dce_to_iron_thorns,
)


def shortest_volt_cyclone_setup(
    initial_state: EnergyAccessState,
    *,
    max_actions: int = 8,
) -> tuple[list[str], EnergyAccessState] | None:
    """Return the shortest represented line that makes Volt Cyclone payable."""
    queue: deque[tuple[EnergyAccessState, list[str]]] = deque(
        [(initial_state, [])]
    )
    seen = {initial_state}

    while queue:
        state, line = queue.popleft()
        if volt_cyclone_ready(state):
            return line, state
        if len(line) >= max_actions:
            continue
        for action in IRON_THORNS_ACTIONS:
            for label, next_state in action(state):
                if next_state in seen:
                    continue
                seen.add(next_state)
                queue.append((next_state, line + [label]))
    return None
