"""Compare Gladion Prize destinations inside Aichi Vileplume endpoints."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_prize_supporter_information import (
    GLADION_STELLAR,
    State,
    accepted_state,
    after_pick,
    picks,
)
from aichi_vileplume_als import (
    ANY_ROUTE_ENDPOINTS,
    _basic_possible_with_artazon_state,
    _stage_targets_remain,
    evaluate_any_route_state,
)


@dataclass(frozen=True)
class DestinationMetrics:
    trials: int
    baseline: dict[str, int]
    prize_to_hand: dict[str, int]
    prize_to_deck: dict[str, int]
    either_destination: dict[str, int]


def _gladion_states(
    state: State, *, destination: str
) -> list[tuple[Counter[str], Counter[str]]]:
    out: list[tuple[Counter[str], Counter[str]]] = []
    for pick in picks(state, GLADION_STELLAR):
        hand, deck = after_pick(state, pick)
        if not hand["Gladion"]:
            continue
        hand["Gladion"] -= 1
        if not hand["Gladion"]:
            del hand["Gladion"]

        for recovered in sorted(set(state.prizes)):
            candidate_hand = hand.copy()
            candidate_deck = deck.copy()
            if destination == "hand":
                candidate_hand[recovered] += 1
            elif destination == "deck":
                candidate_deck[recovered] += 1
            else:
                raise ValueError(destination)
            if (
                candidate_hand["Technical Machine: Evolution"]
                and candidate_hand["Jet Energy"]
            ):
                out.append((candidate_hand, candidate_deck))
    return out


def _endpoint_success(
    state: State,
    endpoint: str,
    destination: str,
) -> bool:
    required_basics = ANY_ROUTE_ENDPOINTS[endpoint]
    for hand, deck in _gladion_states(state, destination=destination):
        if not _stage_targets_remain(deck, endpoint):
            continue
        if _basic_possible_with_artazon_state(
            hand,
            deck,
            state.active,
            required_basics,
            artazon_available=hand["Artazon"] > 0,
        ):
            return True
    return False


def simulate(
    trials: int = 20_000, *, seed: int = 20261007
) -> DestinationMetrics:
    rng = random.Random(seed)
    baseline: Counter[str] = Counter()
    hand: Counter[str] = Counter()
    deck: Counter[str] = Counter()
    either: Counter[str] = Counter()

    for _ in range(trials):
        state = accepted_state(rng)
        base = evaluate_any_route_state(
            state.hand, state.deck, state.active, state.top_five
        )
        for endpoint in ANY_ROUTE_ENDPOINTS:
            h = _endpoint_success(state, endpoint, "hand")
            d = _endpoint_success(state, endpoint, "deck")
            baseline[endpoint] += base[endpoint]
            hand[endpoint] += base[endpoint] or h
            deck[endpoint] += base[endpoint] or d
            either[endpoint] += base[endpoint] or h or d

    return DestinationMetrics(
        trials,
        dict(baseline),
        dict(hand),
        dict(deck),
        dict(either),
    )


if __name__ == "__main__":
    print(simulate())
