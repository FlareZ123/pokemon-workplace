"""Minimum opaque-card burden in the initial Secret Box payment.

This keeps the existing Aichi Secret Box planner's compressed state and asks a
narrow question for paired Secret-Box-only first-turn successes: before Secret
Box resolves, how many cards from the compressed "other" category must its
mandatory three-card discard contain?

Later actions are evaluated by the published Boolean core planner. Their
discard choices do not contribute to this metric.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import random

from aichi_vileplume_secret_box import (
    BASE_DECK,
    DECK_INDEX,
    HAND_INDEX,
    SECRET_BOX_DECK,
    STELLAR_TRAINERS,
    _compress_deck,
    _compress_hand,
    _core_possible,
    _dec,
    _discard_selections,
    _inc,
    _raw_state,
    _state_succeeds,
)


OPAQUE_INDEX = HAND_INDEX["other"]


@dataclass(frozen=True)
class InitialOpaqueFrontierResult:
    trials: int
    incremental_successes: int
    histogram: tuple[tuple[int, int], ...]
    missing_cost_witnesses: int

    def successes_with_budget(self, budget: int) -> int:
        if budget < 0:
            return 0
        return sum(
            count for cost, count in self.histogram if cost <= budget
        )

    def survival_share(self, budget: int) -> float:
        if self.incremental_successes == 0:
            return 1.0
        return self.successes_with_budget(budget) / self.incremental_successes


def _min_value(current: int | None, candidate: int | None) -> int | None:
    if candidate is None:
        return current
    if current is None or candidate < current:
        return candidate
    return current


def _resolve_box_outputs(
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    selection: tuple[int, ...],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    next_hand = [
        count - discarded
        for count, discarded in zip(hand, selection)
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

    return tuple(next_hand), tuple(next_deck)


@lru_cache(maxsize=None)
def _min_initial_opaque(state) -> int | None:
    (
        hand,
        deck,
        supporter_used,
        stadium_used,
        fan_used,
        bunnelby_in_play,
        fan_rotom_in_play,
    ) = state

    # This metric requires Secret Box to contribute before the endpoint exists.
    if (
        bunnelby_in_play
        and hand[HAND_INDEX["tm_evolution"]] > 0
        and hand[HAND_INDEX["jet_energy"]] > 0
    ):
        return None

    best: int | None = None

    if hand[HAND_INDEX["secret_box"]] > 0:
        base_hand = _dec(hand, HAND_INDEX["secret_box"])
        if sum(base_hand) >= 3:
            for selection in _discard_selections(base_hand, 3):
                next_hand, next_deck = _resolve_box_outputs(
                    base_hand,
                    deck,
                    selection,
                )
                if _core_possible(
                    (
                        next_hand,
                        next_deck,
                        supporter_used,
                        stadium_used,
                        fan_used,
                        bunnelby_in_play,
                        fan_rotom_in_play,
                    )
                ):
                    best = _min_value(
                        best,
                        selection[OPAQUE_INDEX],
                    )

    if not bunnelby_in_play and hand[HAND_INDEX["bunnelby"]] > 0:
        best = _min_value(
            best,
            _min_initial_opaque(
                (
                    _dec(hand, HAND_INDEX["bunnelby"]),
                    deck,
                    supporter_used,
                    stadium_used,
                    fan_used,
                    True,
                    fan_rotom_in_play,
                )
            ),
        )

    if not fan_rotom_in_play and hand[HAND_INDEX["fan_rotom"]] > 0:
        best = _min_value(
            best,
            _min_initial_opaque(
                (
                    _dec(hand, HAND_INDEX["fan_rotom"]),
                    deck,
                    supporter_used,
                    stadium_used,
                    fan_used,
                    bunnelby_in_play,
                    True,
                )
            ),
        )

    if (
        fan_rotom_in_play
        and not fan_used
        and not bunnelby_in_play
        and deck[DECK_INDEX["bunnelby"]] > 0
    ):
        best = _min_value(
            best,
            _min_initial_opaque(
                (
                    _inc(hand, HAND_INDEX["bunnelby"]),
                    _dec(deck, DECK_INDEX["bunnelby"]),
                    supporter_used,
                    stadium_used,
                    True,
                    bunnelby_in_play,
                    fan_rotom_in_play,
                )
            ),
        )

    if (
        not stadium_used
        and hand[HAND_INDEX["artazon"]] > 0
        and not bunnelby_in_play
        and hand[HAND_INDEX["bunnelby"]] == 0
        and deck[DECK_INDEX["bunnelby"]] > 0
    ):
        best = _min_value(
            best,
            _min_initial_opaque(
                (
                    _dec(hand, HAND_INDEX["artazon"]),
                    _dec(deck, DECK_INDEX["bunnelby"]),
                    supporter_used,
                    True,
                    fan_used,
                    True,
                    fan_rotom_in_play,
                )
            ),
        )

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

        best = _min_value(
            best,
            _min_initial_opaque(
                (
                    tuple(next_hand),
                    tuple(next_deck),
                    supporter_used,
                    stadium_used,
                    fan_used,
                    bunnelby_in_play,
                    fan_rotom_in_play,
                )
            ),
        )

    if hand[HAND_INDEX["gnh"]] > 0 and not supporter_used:
        base_hand = _dec(hand, HAND_INDEX["gnh"])

        next_hand = list(base_hand)
        next_deck = list(deck)
        if next_deck[DECK_INDEX["artazon"]] > 0:
            next_deck[DECK_INDEX["artazon"]] -= 1
            next_hand[HAND_INDEX["artazon"]] += 1
        best = _min_value(
            best,
            _min_initial_opaque(
                (
                    tuple(next_hand),
                    tuple(next_deck),
                    True,
                    stadium_used,
                    fan_used,
                    bunnelby_in_play,
                    fan_rotom_in_play,
                )
            ),
        )

        if (
            (
                base_hand[HAND_INDEX["tm_evolution"]] == 0
                or base_hand[HAND_INDEX["jet_energy"]] == 0
            )
            and sum(base_hand) >= 2
        ):
            for selection in _discard_selections(base_hand, 2):
                candidate_hand = [
                    count - discarded
                    for count, discarded in zip(base_hand, selection)
                ]
                candidate_deck = list(deck)

                if candidate_deck[DECK_INDEX["artazon"]] > 0:
                    candidate_deck[DECK_INDEX["artazon"]] -= 1
                    candidate_hand[HAND_INDEX["artazon"]] += 1

                if (
                    candidate_hand[HAND_INDEX["tm_evolution"]] == 0
                    and candidate_deck[DECK_INDEX["tm_evolution"]] > 0
                ):
                    candidate_deck[DECK_INDEX["tm_evolution"]] -= 1
                    candidate_hand[HAND_INDEX["tm_evolution"]] += 1
                elif candidate_deck[DECK_INDEX["tool_other"]] > 0:
                    candidate_deck[DECK_INDEX["tool_other"]] -= 1
                    candidate_hand[HAND_INDEX["other"]] += 1
                elif candidate_deck[DECK_INDEX["tm_evolution"]] > 0:
                    candidate_deck[DECK_INDEX["tm_evolution"]] -= 1
                    candidate_hand[HAND_INDEX["tm_evolution"]] += 1

                if (
                    candidate_hand[HAND_INDEX["jet_energy"]] == 0
                    and candidate_deck[DECK_INDEX["jet_energy"]] > 0
                ):
                    candidate_deck[DECK_INDEX["jet_energy"]] -= 1
                    candidate_hand[HAND_INDEX["jet_energy"]] += 1
                elif candidate_deck[DECK_INDEX["special_energy_other"]] > 0:
                    candidate_deck[DECK_INDEX["special_energy_other"]] -= 1
                    candidate_hand[HAND_INDEX["other"]] += 1
                elif candidate_deck[DECK_INDEX["jet_energy"]] > 0:
                    candidate_deck[DECK_INDEX["jet_energy"]] -= 1
                    candidate_hand[HAND_INDEX["jet_energy"]] += 1

                best = _min_value(
                    best,
                    _min_initial_opaque(
                        (
                            tuple(candidate_hand),
                            tuple(candidate_deck),
                            True,
                            stadium_used,
                            fan_used,
                            bunnelby_in_play,
                            fan_rotom_in_play,
                        )
                    ),
                )

    return best


def state_min_initial_opaque(raw_state) -> int | None:
    hand, remaining, active, top_five = raw_state
    picks = [None]
    if active == "Jirachi":
        picks.extend(sorted(set(top_five) & STELLAR_TRAINERS))

    best: int | None = None
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
        best = _min_value(best, _min_initial_opaque(state))

    return best


def analyze_initial_opaque_frontier(
    trials: int,
    *,
    seed: int = 20261007,
) -> InitialOpaqueFrontierResult:
    rng = random.Random(seed)
    incremental = 0
    histogram: Counter[int] = Counter()
    missing = 0

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
        if secret_ok and not baseline_ok:
            incremental += 1
            cost = state_min_initial_opaque(secret_state)
            if cost is None:
                missing += 1
            else:
                histogram[cost] += 1

    return InitialOpaqueFrontierResult(
        trials=trials,
        incremental_successes=incremental,
        histogram=tuple(sorted(histogram.items())),
        missing_cost_witnesses=missing,
    )


def main() -> None:
    result = analyze_initial_opaque_frontier(100_000)
    print(f"trials={result.trials}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"histogram={dict(result.histogram)}")
    print(f"missing_cost_witnesses={result.missing_cost_witnesses}")
    for budget in range(4):
        print(
            f"budget={budget}: "
            f"count={result.successes_with_budget(budget)}, "
            f"survival={result.survival_share(budget):.6%}"
        )


if __name__ == "__main__":
    main()
