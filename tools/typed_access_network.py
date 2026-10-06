"""Minimal typed state-transition engine for Supporter-access semantics.

The engine is intentionally small. It formalizes a few representative Expanded
connector lines while preserving zones, current Supporter usage, Bench capacity,
and Item/Ability/Supporter lock state.

It is a research scaffold rather than a complete Pokemon TCG simulator.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable


class Zone(str, Enum):
    DECK = "deck"
    HAND = "hand"
    BENCH = "bench"
    DISCARD = "discard"
    PLAYED = "played"


@dataclass(frozen=True)
class State:
    locations: tuple[tuple[str, str], ...]
    supporter_used: bool = False
    turn_index: int = 0
    gladion_played: bool = False
    bench_count: int = 0
    bench_limit: int = 5
    items_allowed: bool = True
    abilities_allowed: bool = True
    supporters_allowed: bool = True

    def zone(self, card: str) -> str | None:
        return dict(self.locations).get(card)


Transition = tuple[str, State]
Action = Callable[[State], list[Transition]]


def make_state(locations: dict[str, str], **kwargs: object) -> State:
    return State(tuple(sorted(locations.items())), **kwargs)


def _move(state: State, card: str, zone: Zone) -> State:
    locations = dict(state.locations)
    locations[card] = zone.value
    return replace(state, locations=tuple(sorted(locations.items())))


def _resolve_event(state: State, event: str, card: str) -> State:
    if (
        event == "play_from_hand_to_bench"
        and card == "Tapu Lele-GX"
        and state.abilities_allowed
        and state.zone("Gladion") == Zone.DECK.value
    ):
        return _move(state, "Gladion", Zone.HAND)
    return state


def play_tapu_lele_from_hand(state: State) -> list[Transition]:
    if (
        state.zone("Tapu Lele-GX") != Zone.HAND.value
        or state.bench_count >= state.bench_limit
    ):
        return []

    next_state = _move(state, "Tapu Lele-GX", Zone.BENCH)
    next_state = replace(next_state, bench_count=state.bench_count + 1)
    next_state = _resolve_event(
        next_state,
        event="play_from_hand_to_bench",
        card="Tapu Lele-GX",
    )
    return [("Play Tapu Lele-GX from hand onto Bench", next_state)]


def quick_ball_for_tapu_lele(state: State) -> list[Transition]:
    if not state.items_allowed:
        return []
    if (
        state.zone("Quick Ball") != Zone.HAND.value
        or state.zone("Tapu Lele-GX") != Zone.DECK.value
        or state.zone("Fodder") != Zone.HAND.value
    ):
        return []

    next_state = _move(state, "Quick Ball", Zone.DISCARD)
    next_state = _move(next_state, "Fodder", Zone.DISCARD)
    next_state = _move(next_state, "Tapu Lele-GX", Zone.HAND)
    return [("Quick Ball -> Tapu Lele-GX to hand", next_state)]


def nest_ball_for_tapu_lele(state: State) -> list[Transition]:
    if not state.items_allowed:
        return []
    if (
        state.zone("Nest Ball") != Zone.HAND.value
        or state.zone("Tapu Lele-GX") != Zone.DECK.value
        or state.bench_count >= state.bench_limit
    ):
        return []

    next_state = _move(state, "Nest Ball", Zone.DISCARD)
    next_state = _move(next_state, "Tapu Lele-GX", Zone.BENCH)
    next_state = replace(next_state, bench_count=state.bench_count + 1)

    # This is a deck-to-Bench placement. It deliberately does not emit the
    # play_from_hand_to_bench event required by Wonder Tag.
    return [("Nest Ball -> Tapu Lele-GX directly to Bench", next_state)]


def battle_compressor_for_gladion(state: State) -> list[Transition]:
    if not state.items_allowed:
        return []
    if (
        state.zone("Battle Compressor") != Zone.HAND.value
        or state.zone("Gladion") != Zone.DECK.value
    ):
        return []

    next_state = _move(state, "Battle Compressor", Zone.DISCARD)
    next_state = _move(next_state, "Gladion", Zone.DISCARD)
    return [("Battle Compressor -> Gladion to discard", next_state)]


def vs_seeker_for_gladion(state: State) -> list[Transition]:
    if not state.items_allowed:
        return []
    if (
        state.zone("VS Seeker") != Zone.HAND.value
        or state.zone("Gladion") != Zone.DISCARD.value
    ):
        return []

    next_state = _move(state, "VS Seeker", Zone.DISCARD)
    next_state = _move(next_state, "Gladion", Zone.HAND)
    return [("VS Seeker -> Gladion to hand", next_state)]


def skyla_for_gladion(state: State) -> list[Transition]:
    if not state.supporters_allowed or state.supporter_used:
        return []
    if (
        state.zone("Skyla") != Zone.HAND.value
        or state.zone("Gladion") != Zone.DECK.value
    ):
        return []

    next_state = _move(state, "Skyla", Zone.DISCARD)
    next_state = _move(next_state, "Gladion", Zone.HAND)
    next_state = replace(next_state, supporter_used=True)
    return [("Play Skyla -> Gladion to hand", next_state)]


def play_gladion(state: State) -> list[Transition]:
    if (
        not state.supporters_allowed
        or state.supporter_used
        or state.zone("Gladion") != Zone.HAND.value
    ):
        return []

    next_state = _move(state, "Gladion", Zone.PLAYED)
    next_state = replace(
        next_state,
        supporter_used=True,
        gladion_played=True,
    )
    return [("Play Gladion", next_state)]


def advance_supporter_window(state: State) -> list[Transition]:
    return [
        (
            "Advance to next Supporter window",
            replace(
                state,
                supporter_used=False,
                turn_index=state.turn_index + 1,
            ),
        )
    ]


CURRENT_WINDOW_ACTIONS: tuple[Action, ...] = (
    quick_ball_for_tapu_lele,
    nest_ball_for_tapu_lele,
    play_tapu_lele_from_hand,
    battle_compressor_for_gladion,
    vs_seeker_for_gladion,
    skyla_for_gladion,
    play_gladion,
)


def shortest_gladion_line(
    initial_state: State,
    *,
    max_future_windows: int = 0,
    max_actions: int = 8,
) -> tuple[list[str], State] | None:
    """Return the shortest line that plays Gladion within the allowed windows."""
    queue: deque[tuple[State, list[str]]] = deque([(initial_state, [])])
    seen = {initial_state}

    while queue:
        state, line = queue.popleft()
        if state.gladion_played:
            return line, state
        if len(line) >= max_actions:
            continue

        actions = list(CURRENT_WINDOW_ACTIONS)
        if state.turn_index < max_future_windows:
            actions.append(advance_supporter_window)

        for action in actions:
            for label, next_state in action(state):
                if next_state in seen:
                    continue
                seen.add(next_state)
                queue.append((next_state, line + [label]))

    return None
