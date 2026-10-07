"""First-turn core impact of Grand Tree -> Secret Box in Aichi Vileplume.

The model keeps the published Takahiro Ando Aichi 2026 list fixed except for
its ACE SPEC slot.  It compares the current list's Grand Tree with Secret Box
for the first-turn-going-second Bunnelby + TM: Evolution + Jet Energy core.

This is an immediate-line feasibility model.  It intentionally does not score
Grand Tree's later-turn evolution value or the strategic value of cards spent
on discard costs.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import sqrt
import random

from aichi_vileplume_als import BASICS, DECK


HAND_NAMES = (
    "gnh",
    "tag_call",
    "tm_evolution",
    "artazon",
    "jet_energy",
    "secret_box",
    "bunnelby",
    "fan_rotom",
    "other",
)
HAND_INDEX = {name: index for index, name in enumerate(HAND_NAMES)}

DECK_NAMES = (
    "gnh",
    "tag_team_other",
    "tag_call",
    "tm_evolution",
    "tool_other",
    "artazon",
    "jet_energy",
    "special_energy_other",
    "secret_box",
    "bunnelby",
    "supporter_other",
)
DECK_INDEX = {name: index for index, name in enumerate(DECK_NAMES)}

TAG_TEAM_OTHER = {"Bellelba & Brycen-Man"}
TOOL_OTHER = {"Stealthy Hood", "Counter Gain"}
SPECIAL_ENERGY_OTHER = {"Capture Energy", "Memory Energy"}
SUPPORTER_OTHER = {
    "Guzma",
    "Cassius",
    "Karen",
    "Plumeria",
    "Gladion",
    "Faba",
    "Lusamine",
    "Peonia",
    "Team Yell's Cheer",
}
STELLAR_TRAINERS = {
    "Guzma & Hala",
    "Tag Call",
    "Technical Machine: Evolution",
    "Artazon",
    "Secret Box",
}


@dataclass(frozen=True)
class SwapSimulationResult:
    """Paired Monte Carlo result for the two ACE SPEC choices."""

    trials: int
    baseline_successes: int
    secret_box_successes: int
    incremental_successes: int
    baseline_only_successes: int
    secret_box_in_hand: int
    secret_box_stellar_only: int
    incremental_jet_in_hand: int
    incremental_jet_needs_gnh: int
    incremental_started_with_gnh_or_tag_call: int

    @property
    def baseline_probability(self) -> float:
        return self.baseline_successes / self.trials

    @property
    def secret_box_probability(self) -> float:
        return self.secret_box_successes / self.trials

    @property
    def incremental_probability(self) -> float:
        return self.incremental_successes / self.trials

    @property
    def secret_box_access_probability(self) -> float:
        return (self.secret_box_in_hand + self.secret_box_stellar_only) / self.trials

    def normal_95_half_width(self, successes: int) -> float:
        p = successes / self.trials
        return 1.96 * sqrt(p * (1.0 - p) / self.trials)


def _variant_deck(secret_box: bool) -> tuple[str, ...]:
    if not secret_box:
        return DECK
    return tuple(
        "Secret Box" if card == "Grand Tree" else card
        for card in DECK
    )


BASE_DECK = _variant_deck(False)
SECRET_BOX_DECK = _variant_deck(True)


def _dec(values: tuple[int, ...], index: int) -> tuple[int, ...]:
    changed = list(values)
    changed[index] -= 1
    return tuple(changed)


def _inc(values: tuple[int, ...], index: int) -> tuple[int, ...]:
    changed = list(values)
    changed[index] += 1
    return tuple(changed)


def _discard_selections(
    hand: tuple[int, ...],
    cost: int,
):
    """Yield exact compressed hand multisets of the requested size."""

    bounds = tuple(min(count, cost) for count in hand)
    for selection in product(*(range(bound + 1) for bound in bounds)):
        if sum(selection) == cost:
            yield selection


def _compress_hand(cards) -> tuple[int, ...]:
    values = [0] * len(HAND_NAMES)
    for card in cards:
        if card == "Guzma & Hala":
            values[HAND_INDEX["gnh"]] += 1
        elif card == "Tag Call":
            values[HAND_INDEX["tag_call"]] += 1
        elif card == "Technical Machine: Evolution":
            values[HAND_INDEX["tm_evolution"]] += 1
        elif card == "Artazon":
            values[HAND_INDEX["artazon"]] += 1
        elif card == "Jet Energy":
            values[HAND_INDEX["jet_energy"]] += 1
        elif card == "Secret Box":
            values[HAND_INDEX["secret_box"]] += 1
        elif card == "Bunnelby":
            values[HAND_INDEX["bunnelby"]] += 1
        elif card == "Fan Rotom":
            values[HAND_INDEX["fan_rotom"]] += 1
        else:
            values[HAND_INDEX["other"]] += 1
    return tuple(values)


def _compress_deck(cards) -> tuple[int, ...]:
    values = [0] * len(DECK_NAMES)
    for card in cards:
        if card == "Guzma & Hala":
            values[DECK_INDEX["gnh"]] += 1
        elif card in TAG_TEAM_OTHER:
            values[DECK_INDEX["tag_team_other"]] += 1
        elif card == "Tag Call":
            values[DECK_INDEX["tag_call"]] += 1
        elif card == "Technical Machine: Evolution":
            values[DECK_INDEX["tm_evolution"]] += 1
        elif card in TOOL_OTHER:
            values[DECK_INDEX["tool_other"]] += 1
        elif card == "Artazon":
            values[DECK_INDEX["artazon"]] += 1
        elif card == "Jet Energy":
            values[DECK_INDEX["jet_energy"]] += 1
        elif card in SPECIAL_ENERGY_OTHER:
            values[DECK_INDEX["special_energy_other"]] += 1
        elif card == "Secret Box":
            values[DECK_INDEX["secret_box"]] += 1
        elif card == "Bunnelby":
            values[DECK_INDEX["bunnelby"]] += 1
        elif card in SUPPORTER_OTHER:
            values[DECK_INDEX["supporter_other"]] += 1
    return tuple(values)


def _raw_state(
    deck_cards: tuple[str, ...],
    order: list[int],
):
    opening = [deck_cards[index] for index in order[:7]]
    if not any(card in BASICS for card in opening):
        return None

    prizes = [deck_cards[index] for index in order[7:13]]
    draw = deck_cards[order[13]]
    top_five = tuple(deck_cards[index] for index in order[14:19])

    opening_basics = [card for card in opening if card in BASICS]
    if "Jirachi" in opening_basics:
        active = "Jirachi"
    else:
        non_bunnelby = [
            card for card in opening_basics
            if card != "Bunnelby"
        ]
        active = non_bunnelby[0] if non_bunnelby else "Bunnelby"

    hand = Counter(opening + [draw])
    hand[active] -= 1
    if hand[active] == 0:
        del hand[active]

    remaining = Counter(deck_cards)
    for card in opening + prizes + [draw]:
        remaining[card] -= 1
        if remaining[card] == 0:
            del remaining[card]

    return hand, remaining, active, top_five


@lru_cache(maxsize=None)
def _core_possible(state) -> bool:
    (
        hand,
        deck,
        supporter_used,
        stadium_used,
        fan_used,
        bunnelby_in_play,
        fan_rotom_in_play,
    ) = state

    if (
        bunnelby_in_play
        and hand[HAND_INDEX["tm_evolution"]] > 0
        and hand[HAND_INDEX["jet_energy"]] > 0
    ):
        return True

    if not bunnelby_in_play and hand[HAND_INDEX["bunnelby"]] > 0:
        next_hand = _dec(hand, HAND_INDEX["bunnelby"])
        if _core_possible(
            (
                next_hand,
                deck,
                supporter_used,
                stadium_used,
                fan_used,
                True,
                fan_rotom_in_play,
            )
        ):
            return True

    if not fan_rotom_in_play and hand[HAND_INDEX["fan_rotom"]] > 0:
        next_hand = _dec(hand, HAND_INDEX["fan_rotom"])
        if _core_possible(
            (
                next_hand,
                deck,
                supporter_used,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                True,
            )
        ):
            return True

    if (
        fan_rotom_in_play
        and not fan_used
        and not bunnelby_in_play
        and deck[DECK_INDEX["bunnelby"]] > 0
    ):
        next_hand = _inc(hand, HAND_INDEX["bunnelby"])
        next_deck = _dec(deck, DECK_INDEX["bunnelby"])
        if _core_possible(
            (
                next_hand,
                next_deck,
                supporter_used,
                stadium_used,
                True,
                bunnelby_in_play,
                fan_rotom_in_play,
            )
        ):
            return True

    if (
        not stadium_used
        and hand[HAND_INDEX["artazon"]] > 0
        and not bunnelby_in_play
        and hand[HAND_INDEX["bunnelby"]] == 0
        and deck[DECK_INDEX["bunnelby"]] > 0
    ):
        next_hand = _dec(hand, HAND_INDEX["artazon"])
        next_deck = _dec(deck, DECK_INDEX["bunnelby"])
        if _core_possible(
            (
                next_hand,
                next_deck,
                supporter_used,
                True,
                fan_used,
                True,
                fan_rotom_in_play,
            )
        ):
            return True

    if (
        hand[HAND_INDEX["tag_call"]] > 0
        and (
            deck[DECK_INDEX["gnh"]]
            + deck[DECK_INDEX["tag_team_other"]]
            > 0
        )
    ):
        next_hand = list(_dec(hand, HAND_INDEX["tag_call"]))
        next_deck = list(deck)
        slots = 2

        if (
            next_hand[HAND_INDEX["gnh"]] == 0
            and next_deck[DECK_INDEX["gnh"]] > 0
        ):
            next_deck[DECK_INDEX["gnh"]] -= 1
            next_hand[HAND_INDEX["gnh"]] += 1
            slots -= 1

        take = min(slots, next_deck[DECK_INDEX["tag_team_other"]])
        next_deck[DECK_INDEX["tag_team_other"]] -= take
        next_hand[HAND_INDEX["other"]] += take
        slots -= take

        take = min(slots, next_deck[DECK_INDEX["gnh"]])
        next_deck[DECK_INDEX["gnh"]] -= take
        next_hand[HAND_INDEX["gnh"]] += take

        if _core_possible(
            (
                tuple(next_hand),
                tuple(next_deck),
                supporter_used,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                fan_rotom_in_play,
            )
        ):
            return True

    if hand[HAND_INDEX["secret_box"]] > 0:
        base_hand = _dec(hand, HAND_INDEX["secret_box"])
        if sum(base_hand) >= 3:
            for selection in _discard_selections(base_hand, 3):
                next_hand = [
                    count - discarded
                    for count, discarded in zip(base_hand, selection)
                ]
                next_deck = list(deck)

                if next_deck[DECK_INDEX["tag_call"]] > 0:
                    next_deck[DECK_INDEX["tag_call"]] -= 1
                    next_hand[HAND_INDEX["tag_call"]] += 1

                if (
                    next_hand[HAND_INDEX["tm_evolution"]] == 0
                    and next_deck[DECK_INDEX["tm_evolution"]] > 0
                ):
                    next_deck[DECK_INDEX["tm_evolution"]] -= 1
                    next_hand[HAND_INDEX["tm_evolution"]] += 1
                elif next_deck[DECK_INDEX["tool_other"]] > 0:
                    next_deck[DECK_INDEX["tool_other"]] -= 1
                    next_hand[HAND_INDEX["other"]] += 1
                elif next_deck[DECK_INDEX["tm_evolution"]] > 0:
                    next_deck[DECK_INDEX["tm_evolution"]] -= 1
                    next_hand[HAND_INDEX["tm_evolution"]] += 1

                if (
                    next_hand[HAND_INDEX["gnh"]] == 0
                    and next_deck[DECK_INDEX["gnh"]] > 0
                ):
                    next_deck[DECK_INDEX["gnh"]] -= 1
                    next_hand[HAND_INDEX["gnh"]] += 1
                elif next_deck[DECK_INDEX["supporter_other"]] > 0:
                    next_deck[DECK_INDEX["supporter_other"]] -= 1
                    next_hand[HAND_INDEX["other"]] += 1
                elif next_deck[DECK_INDEX["tag_team_other"]] > 0:
                    next_deck[DECK_INDEX["tag_team_other"]] -= 1
                    next_hand[HAND_INDEX["other"]] += 1
                elif next_deck[DECK_INDEX["gnh"]] > 0:
                    next_deck[DECK_INDEX["gnh"]] -= 1
                    next_hand[HAND_INDEX["gnh"]] += 1

                if next_deck[DECK_INDEX["artazon"]] > 0:
                    next_deck[DECK_INDEX["artazon"]] -= 1
                    next_hand[HAND_INDEX["artazon"]] += 1

                if _core_possible(
                    (
                        tuple(next_hand),
                        tuple(next_deck),
                        supporter_used,
                        stadium_used,
                        fan_used,
                        bunnelby_in_play,
                        fan_rotom_in_play,
                    )
                ):
                    return True

    if hand[HAND_INDEX["gnh"]] > 0 and not supporter_used:
        base_hand = _dec(hand, HAND_INDEX["gnh"])

        next_hand = list(base_hand)
        next_deck = list(deck)
        if next_deck[DECK_INDEX["artazon"]] > 0:
            next_deck[DECK_INDEX["artazon"]] -= 1
            next_hand[HAND_INDEX["artazon"]] += 1
        if _core_possible(
            (
                tuple(next_hand),
                tuple(next_deck),
                True,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                fan_rotom_in_play,
            )
        ):
            return True

        if (
            (
                base_hand[HAND_INDEX["tm_evolution"]] == 0
                or base_hand[HAND_INDEX["jet_energy"]] == 0
            )
            and sum(base_hand) >= 2
        ):
            for selection in _discard_selections(base_hand, 2):
                next_hand = [
                    count - discarded
                    for count, discarded in zip(base_hand, selection)
                ]
                next_deck = list(deck)

                if next_deck[DECK_INDEX["artazon"]] > 0:
                    next_deck[DECK_INDEX["artazon"]] -= 1
                    next_hand[HAND_INDEX["artazon"]] += 1

                if (
                    next_hand[HAND_INDEX["tm_evolution"]] == 0
                    and next_deck[DECK_INDEX["tm_evolution"]] > 0
                ):
                    next_deck[DECK_INDEX["tm_evolution"]] -= 1
                    next_hand[HAND_INDEX["tm_evolution"]] += 1
                elif next_deck[DECK_INDEX["tool_other"]] > 0:
                    next_deck[DECK_INDEX["tool_other"]] -= 1
                    next_hand[HAND_INDEX["other"]] += 1
                elif next_deck[DECK_INDEX["tm_evolution"]] > 0:
                    next_deck[DECK_INDEX["tm_evolution"]] -= 1
                    next_hand[HAND_INDEX["tm_evolution"]] += 1

                if (
                    next_hand[HAND_INDEX["jet_energy"]] == 0
                    and next_deck[DECK_INDEX["jet_energy"]] > 0
                ):
                    next_deck[DECK_INDEX["jet_energy"]] -= 1
                    next_hand[HAND_INDEX["jet_energy"]] += 1
                elif next_deck[DECK_INDEX["special_energy_other"]] > 0:
                    next_deck[DECK_INDEX["special_energy_other"]] -= 1
                    next_hand[HAND_INDEX["other"]] += 1
                elif next_deck[DECK_INDEX["jet_energy"]] > 0:
                    next_deck[DECK_INDEX["jet_energy"]] -= 1
                    next_hand[HAND_INDEX["jet_energy"]] += 1

                if _core_possible(
                    (
                        tuple(next_hand),
                        tuple(next_deck),
                        True,
                        stadium_used,
                        fan_used,
                        bunnelby_in_play,
                        fan_rotom_in_play,
                    )
                ):
                    return True

    return False


def _state_succeeds(raw_state) -> bool:
    hand, remaining, active, top_five = raw_state
    picks = [None]
    if active == "Jirachi":
        picks.extend(sorted(set(top_five) & STELLAR_TRAINERS))

    for pick in picks:
        candidate_hand = hand.copy()
        candidate_deck = remaining.copy()
        if pick is not None:
            candidate_hand[pick] += 1
            candidate_deck[pick] -= 1
            if candidate_deck[pick] == 0:
                del candidate_deck[pick]

        state = (
            _compress_hand(candidate_hand.elements()),
            _compress_deck(candidate_deck.elements()),
            False,
            False,
            False,
            active == "Bunnelby",
            active == "Fan Rotom",
        )
        if _core_possible(state):
            return True

    return False


def simulate_swap(
    trials: int,
    *,
    seed: int = 20261007,
) -> SwapSimulationResult:
    """Run paired accepted-opening trials for Grand Tree and Secret Box."""

    rng = random.Random(seed)
    baseline_successes = 0
    secret_box_successes = 0
    incremental_successes = 0
    baseline_only_successes = 0
    secret_box_in_hand = 0
    secret_box_stellar_only = 0
    incremental_jet_in_hand = 0
    incremental_jet_needs_gnh = 0
    incremental_started_with_gnh_or_tag_call = 0

    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            baseline_state = _raw_state(BASE_DECK, order)
            if baseline_state is not None:
                break

        secret_state = _raw_state(SECRET_BOX_DECK, order)
        if secret_state is None:
            raise AssertionError("ACE SPEC substitution changed setup acceptance")

        baseline_ok = _state_succeeds(baseline_state)
        secret_ok = _state_succeeds(secret_state)

        baseline_successes += int(baseline_ok)
        secret_box_successes += int(secret_ok)

        hand, _remaining, active, top_five = secret_state
        box_in_hand = hand["Secret Box"] > 0
        box_stellar = (
            not box_in_hand
            and active == "Jirachi"
            and "Secret Box" in top_five
        )
        secret_box_in_hand += int(box_in_hand)
        secret_box_stellar_only += int(box_stellar)

        if baseline_ok and not secret_ok:
            baseline_only_successes += 1
        elif secret_ok and not baseline_ok:
            incremental_successes += 1
            if hand["Jet Energy"] > 0:
                incremental_jet_in_hand += 1
            else:
                incremental_jet_needs_gnh += 1
            if hand["Guzma & Hala"] > 0 or hand["Tag Call"] > 0:
                incremental_started_with_gnh_or_tag_call += 1

    return SwapSimulationResult(
        trials=trials,
        baseline_successes=baseline_successes,
        secret_box_successes=secret_box_successes,
        incremental_successes=incremental_successes,
        baseline_only_successes=baseline_only_successes,
        secret_box_in_hand=secret_box_in_hand,
        secret_box_stellar_only=secret_box_stellar_only,
        incremental_jet_in_hand=incremental_jet_in_hand,
        incremental_jet_needs_gnh=incremental_jet_needs_gnh,
        incremental_started_with_gnh_or_tag_call=(
            incremental_started_with_gnh_or_tag_call
        ),
    )


def main() -> None:
    result = simulate_swap(100_000)
    print(f"trials={result.trials}")
    print(f"baseline={result.baseline_probability:.6%}")
    print(f"secret_box={result.secret_box_probability:.6%}")
    print(f"increment={result.incremental_probability:.6%}")
    print(f"secret_box_access={result.secret_box_access_probability:.6%}")
    print(f"baseline_only={result.baseline_only_successes}")
    print(f"gain_jet_in_hand={result.incremental_jet_in_hand}")
    print(f"gain_jet_needs_gnh={result.incremental_jet_needs_gnh}")
    print(
        "gain_started_with_gnh_or_tag_call="
        f"{result.incremental_started_with_gnh_or_tag_call}"
    )


if __name__ == "__main__":
    main()
