"""Prize-Supporter extensions for the Aichi Vileplume first-turn core."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
import random

from aichi_vileplume_als import (
    BASICS,
    DECK,
    RELEVANT_STELLAR,
    _basic_possible_with_artazon_state,
    evaluate_any_route_state,
)

GLADION_STELLAR = RELEVANT_STELLAR | {"Gladion"}
PEONIA_STELLAR = RELEVANT_STELLAR | {"Peonia"}


@dataclass(frozen=True)
class State:
    hand: Counter[str]
    deck: Counter[str]
    prizes: tuple[str, ...]
    active: str
    top_five: tuple[str, ...]


@dataclass(frozen=True)
class Metrics:
    trials: int
    baseline: int
    gladion_state_aware: int
    peonia_blind: int
    both_state_aware: int
    gladion_tag_k1: int
    gladion_tag_or_fan_k1: int
    gladion_added_by_card: dict[str, int]
    gladion_added_via_stellar: int


def accepted_state(rng: random.Random) -> State:
    while True:
        order = rng.sample(range(60), 60)
        opening = [DECK[i] for i in order[:7]]
        if any(card in BASICS for card in opening):
            break
    prizes = tuple(DECK[i] for i in order[7:13])
    draw = DECK[order[13]]
    top_five = tuple(DECK[i] for i in order[14:19])
    basics = [card for card in opening if card in BASICS]
    if "Jirachi" in basics:
        active = "Jirachi"
    else:
        others = [card for card in basics if card != "Bunnelby"]
        active = others[0] if others else "Bunnelby"
    hand = Counter(opening + [draw])
    hand[active] -= 1
    if not hand[active]:
        del hand[active]
    deck = Counter(DECK)
    for card in opening + list(prizes) + [draw]:
        deck[card] -= 1
    return State(hand, deck, prizes, active, top_five)


def picks(state: State, allowed: set[str]) -> list[str | None]:
    out: list[str | None] = [None]
    if state.active == "Jirachi":
        out.extend(sorted(set(state.top_five) & allowed))
    return out


def after_pick(state: State, pick: str | None) -> tuple[Counter[str], Counter[str]]:
    hand, deck = state.hand.copy(), state.deck.copy()
    if pick is not None:
        hand[pick] += 1
        deck[pick] -= 1
    return hand, deck


def core_from_hand(hand: Counter[str], deck: Counter[str], active: str) -> bool:
    if not hand["Technical Machine: Evolution"] or not hand["Jet Energy"]:
        return False
    return _basic_possible_with_artazon_state(
        hand, deck, active, (), artazon_available=hand["Artazon"] > 0
    )


def baseline_success(state: State) -> bool:
    return evaluate_any_route_state(
        state.hand, state.deck, state.active, state.top_five
    )["core"]


def gladion_success(
    state: State, *, k1_gate: str | None = None
) -> tuple[bool, str | None, bool]:
    for pick in picks(state, GLADION_STELLAR):
        hand, deck = after_pick(state, pick)
        if not hand["Gladion"]:
            continue
        if k1_gate == "tag":
            if not hand["Tag Call"]:
                continue
            hand["Tag Call"] -= 1
            if not hand["Tag Call"]:
                del hand["Tag Call"]
        elif k1_gate == "tag_or_fan":
            fan_search = (
                (state.active == "Fan Rotom" or hand["Fan Rotom"] > 0)
                and any(deck[c] > 0 for c in ("Bunnelby", "Pidgey", "Lillipup"))
            )
            if not fan_search:
                if not hand["Tag Call"]:
                    continue
                hand["Tag Call"] -= 1
                if not hand["Tag Call"]:
                    del hand["Tag Call"]
        elif k1_gate is not None:
            raise ValueError(k1_gate)
        hand["Gladion"] -= 1
        if not hand["Gladion"]:
            del hand["Gladion"]
        for recovered in sorted(set(state.prizes)):
            candidate = hand.copy()
            candidate[recovered] += 1
            if core_from_hand(candidate, deck, state.active):
                return True, recovered, pick == "Gladion"
    return False, None, False


def peonia_success(state: State) -> bool:
    for pick in picks(state, PEONIA_STELLAR):
        hand, deck = after_pick(state, pick)
        if not hand["Peonia"]:
            continue
        hand["Peonia"] -= 1
        if not hand["Peonia"]:
            del hand["Peonia"]
        for card in state.prizes[:3]:
            hand[card] += 1
        physical = [card for card, copies in hand.items() for _ in range(copies)]
        seen: set[tuple[str, str, str]] = set()
        for indices in combinations(range(len(physical)), 3):
            returned = tuple(sorted(physical[i] for i in indices))
            if returned in seen:
                continue
            seen.add(returned)
            final_hand = hand.copy()
            for card in returned:
                final_hand[card] -= 1
                if not final_hand[card]:
                    del final_hand[card]
            if core_from_hand(final_hand, deck, state.active):
                return True
    return False


def simulate(trials: int = 100_000, *, seed: int = 20261007) -> Metrics:
    rng = random.Random(seed)
    base = gladion = peonia = both = tag = tagfan = stellar = 0
    recovered: Counter[str] = Counter()
    for _ in range(trials):
        state = accepted_state(rng)
        b = baseline_success(state)
        g, card, via_stellar = gladion_success(state)
        p = peonia_success(state)
        tg, _, _ = gladion_success(state, k1_gate="tag")
        tf, _, _ = gladion_success(state, k1_gate="tag_or_fan")
        base += b
        gladion += b or g
        peonia += b or p
        both += b or g or p
        tag += b or tg
        tagfan += b or tf
        if not b and g:
            assert card is not None
            recovered[card] += 1
            stellar += via_stellar
    return Metrics(
        trials, base, gladion, peonia, both, tag, tagfan, dict(recovered), stellar
    )


if __name__ == "__main__":
    print(simulate())
