"""Integrated state search for the Iron Thorns ex first-turn attack line.

This targeted research model composes card-zone transitions, Item/Supporter/
Stadium action windows, discard costs, the normal Energy attachment, and the
existing typed Energy evaluator. It is intentionally narrower than a full TCG
rules engine.
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
    ACTIVE = "active"
    HAND = "hand"
    DECK = "deck"
    DISCARD = "discard"
    STADIUM = "stadium"
    ATTACHED = "attached"
    PRIZE = "prize"


@dataclass(frozen=True)
class State:
    locations: tuple[tuple[str, str], ...]
    items_allowed: bool = True
    supporters_allowed: bool = True
    stadiums_allowed: bool = True
    attacks_allowed: bool = True
    supporter_used: bool = False
    stadium_played: bool = False
    manual_attachment_used: bool = False
    volt_cyclone_used: bool = False

    def zone(self, card: str) -> str | None:
        return dict(self.locations).get(card)


Transition = tuple[str, State]
Action = Callable[[State], list[Transition]]

IRON_THORNS = "Iron Thorns ex"
TAG_CALL = "Tag Call"
GUZMA_HALA = "Guzma & Hala"
THUNDER_MOUNTAIN = "Thunder Mountain ◇"
DCE = "Double Colorless Energy"
FODDER_A = "Fodder A"
FODDER_B = "Fodder B"


def make_state(locations: dict[str, str], **kwargs: object) -> State:
    return State(tuple(sorted(locations.items())), **kwargs)


def _move(state: State, card: str, zone: Zone) -> State:
    locations = dict(state.locations)
    locations[card] = zone.value
    return replace(state, locations=tuple(sorted(locations.items())))


def tag_call_for_guzma_hala(state: State) -> list[Transition]:
    if not state.items_allowed:
        return []
    if state.zone(TAG_CALL) != Zone.HAND.value:
        return []
    if state.zone(GUZMA_HALA) != Zone.DECK.value:
        return []

    next_state = _move(state, TAG_CALL, Zone.DISCARD)
    next_state = _move(next_state, GUZMA_HALA, Zone.HAND)
    return [("Play Tag Call -> Guzma & Hala to hand", next_state)]


def guzma_hala_for_attack_package(state: State) -> list[Transition]:
    if not state.supporters_allowed or state.supporter_used:
        return []
    if state.zone(GUZMA_HALA) != Zone.HAND.value:
        return []
    if state.zone(THUNDER_MOUNTAIN) != Zone.DECK.value:
        return []
    if state.zone(DCE) != Zone.DECK.value:
        return []
    if state.zone(FODDER_A) != Zone.HAND.value:
        return []
    if state.zone(FODDER_B) != Zone.HAND.value:
        return []

    next_state = _move(state, GUZMA_HALA, Zone.DISCARD)
    next_state = _move(next_state, FODDER_A, Zone.DISCARD)
    next_state = _move(next_state, FODDER_B, Zone.DISCARD)
    next_state = _move(next_state, THUNDER_MOUNTAIN, Zone.HAND)
    next_state = _move(next_state, DCE, Zone.HAND)
    next_state = replace(next_state, supporter_used=True)
    return [
        (
            "Play Guzma & Hala; discard 2 -> Thunder Mountain ◇ + DCE to hand",
            next_state,
        )
    ]


def play_thunder_mountain(state: State) -> list[Transition]:
    if not state.stadiums_allowed or state.stadium_played:
        return []
    if state.zone(THUNDER_MOUNTAIN) != Zone.HAND.value:
        return []

    next_state = _move(state, THUNDER_MOUNTAIN, Zone.STADIUM)
    next_state = replace(next_state, stadium_played=True)
    return [("Play Thunder Mountain ◇", next_state)]


def attach_double_colorless(state: State) -> list[Transition]:
    if state.manual_attachment_used:
        return []
    if state.zone(DCE) != Zone.HAND.value:
        return []
    if state.zone(IRON_THORNS) != Zone.ACTIVE.value:
        return []

    next_state = _move(state, DCE, Zone.ATTACHED)
    next_state = replace(next_state, manual_attachment_used=True)
    return [("Attach Double Colorless Energy to Iron Thorns ex", next_state)]


def volt_cyclone_ready(state: State) -> bool:
    if state.zone(IRON_THORNS) != Zone.ACTIVE.value:
        return False

    routes: list[EnergyRouteType] = []
    if state.zone(DCE) == Zone.ATTACHED.value:
        routes.append(
            EnergyRouteType(
                "attached Double Colorless Energy",
                1,
                (
                    EnergyRouteProfile(
                        units=(unit("C"), unit("C")),
                    ),
                ),
            )
        )

    if state.zone(THUNDER_MOUNTAIN) == Zone.STADIUM.value:
        routes.append(
            EnergyRouteType(
                "Thunder Mountain ◇ in play",
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

    result = evaluate_energy_routes(
        ("L", "C", "C"),
        {},
        {"Lightning", "Basic", "Future", "ex"},
        tuple(routes),
    )
    return result.exact_feasible


def use_volt_cyclone(state: State) -> list[Transition]:
    if not state.attacks_allowed or state.volt_cyclone_used:
        return []
    if not volt_cyclone_ready(state):
        return []

    return [
        (
            "Use Volt Cyclone",
            replace(state, volt_cyclone_used=True),
        )
    ]


ACTIONS: tuple[Action, ...] = (
    tag_call_for_guzma_hala,
    guzma_hala_for_attack_package,
    play_thunder_mountain,
    attach_double_colorless,
    use_volt_cyclone,
)


def shortest_volt_cyclone_line(
    initial_state: State,
    *,
    max_actions: int = 8,
) -> tuple[list[str], State] | None:
    """Return the shortest represented line that successfully uses Volt Cyclone."""
    queue: deque[tuple[State, list[str]]] = deque([(initial_state, [])])
    seen = {initial_state}

    while queue:
        state, line = queue.popleft()
        if state.volt_cyclone_used:
            return line, state
        if len(line) >= max_actions:
            continue

        for action in ACTIONS:
            for label, next_state in action(state):
                if next_state in seen:
                    continue
                seen.add(next_state)
                queue.append((next_state, line + [label]))

    return None
