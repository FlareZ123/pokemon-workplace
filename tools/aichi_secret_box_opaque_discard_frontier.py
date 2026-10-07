"""Opaque-discard frontier for the Aichi Vileplume Secret Box gain.

This extends the existing paired Grand Tree -> Secret Box first-turn model.
The original planner compresses all cards outside its immediate core categories
into one hand category named "other". This module asks, among states that are
Secret-Box-only successes in that existing model, what is the minimum number of
those opaque "other" cards that must be discarded by Secret Box and/or
Guzma & Hala.

The quantity is a preservation stress test, not a card-value estimate. The
"other" bucket mixes cards with very different future strategic values.
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
    _dec,
    _discard_selections,
    _inc,
    _raw_state,
    _state_succeeds,
)

OPAQUE_INDEX = HAND_INDEX["other"]


@dataclass(frozen=True)
class OpaqueDiscardFrontierResult:
    trials: int
    baseline_successes: int
    secret_box_successes: int
    incremental_successes: int
    baseline_only_successes: int
    opaque_histogram: tuple[tuple[int, int], ...]
    validation_states: int
    validation_mismatches: int

    def successes_with_budget(self, budget: int) -> int:
        if budget < 0:
            return 0
        return sum(
            count
            for opaque, count in self.opaque_histogram
            if opaque <= budget
        )

    def incremental_probability_with_budget(self, budget: int) -> float:
        return self.successes_with_budget(budget) / self.trials

    def incremental_survival_share(self, budget: int) -> float:
        if self.incremental_successes == 0:
            return 1.0
        return self.successes_with_budget(budget) / self.incremental_successes


def _min_value(current: int | None, candidate: int | None) -> int | None:
    if candidate is None:
        return current
    if current is None or candidate < current:
        return candidate
    return current


@lru_cache(maxsize=None)
def _core_min_opaque_discards(state) -> int | None:
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
        return 0

    best: int | None = None

    if not bunnelby_in_play and hand[HAND_INDEX["bunnelby"]] > 0:
        next_hand = _dec(hand, HAND_INDEX["bunnelby"])
        best = _min_value(
            best,
            _core_min_opaque_discards(
                (
                    next_hand,
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
        next_hand = _dec(hand, HAND_INDEX["fan_rotom"])
        best = _min_value(
            best,
            _core_min_opaque_discards(
                (
                    next_hand,
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
        next_hand = _inc(hand, HAND_INDEX["bunnelby"])
        next_deck = _dec(deck, DECK_INDEX["bunnelby"])
        best = _min_value(
            best,
            _core_min_opaque_discards(
                (
                    next_hand,
                    next_deck,
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
        next_hand = _dec(hand, HAND_INDEX["artazon"])
        next_deck = _dec(deck, DECK_INDEX["bunnelby"])
        best = _min_value(
            best,
            _core_min_opaque_discards(
                (
                    next_hand,
                    next_deck,
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
            _core_min_opaque_discards(
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

                child = _core_min_opaque_discards(
                    (
                        tuple(next_hand),
                        tuple(next_deck),
                        supporter_used,
                        stadium_used,
                        fan_used,
                        bunnelby_in_play,
                        fan_rotom_in_play,
                    )
                )
                if child is not None:
                    best = _min_value(
                        best,
                        selection[OPAQUE_INDEX] + child,
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
            _core_min_opaque_discards(
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

                child = _core_min_opaque_discards(
                    (
                        tuple(next_hand),
                        tuple(next_deck),
                        True,
                        stadium_used,
                        fan_used,
                        bunnelby_in_play,
                        fan_rotom_in_play,
                    )
                )
                if child is not None:
                    best = _min_value(
                        best,
                        selection[OPAQUE_INDEX] + child,
                    )

    return best


def state_min_opaque_discards(raw_state) -> int | None:
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
        best = _min_value(best, _core_min_opaque_discards(state))

    return best


def analyze_incremental_opaque_frontier(
    trials: int,
    *,
    seed: int = 20261007,
    validation_states: int = 10_000,
) -> OpaqueDiscardFrontierResult:
    rng = random.Random(seed)
    baseline_successes = 0
    secret_box_successes = 0
    incremental_successes = 0
    baseline_only_successes = 0
    histogram: Counter[int] = Counter()
    mismatches = 0
    validated = 0

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

        if validated < validation_states:
            baseline_cost = state_min_opaque_discards(baseline_state)
            secret_cost = state_min_opaque_discards(secret_state)
            mismatches += int((baseline_cost is not None) != baseline_ok)
            mismatches += int((secret_cost is not None) != secret_ok)
            validated += 1

        if baseline_ok and not secret_ok:
            baseline_only_successes += 1
        elif secret_ok and not baseline_ok:
            incremental_successes += 1
            cost = state_min_opaque_discards(secret_state)
            if cost is None:
                raise AssertionError("cost solver rejected a known success")
            histogram[cost] += 1

    return OpaqueDiscardFrontierResult(
        trials=trials,
        baseline_successes=baseline_successes,
        secret_box_successes=secret_box_successes,
        incremental_successes=incremental_successes,
        baseline_only_successes=baseline_only_successes,
        opaque_histogram=tuple(sorted(histogram.items())),
        validation_states=validated,
        validation_mismatches=mismatches,
    )


def main() -> None:
    result = analyze_incremental_opaque_frontier(100_000)
    print(f"trials={result.trials}")
    print(f"baseline_successes={result.baseline_successes}")
    print(f"secret_box_successes={result.secret_box_successes}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"baseline_only_successes={result.baseline_only_successes}")
    print(f"opaque_histogram={dict(result.opaque_histogram)}")
    print(f"validation_states={result.validation_states}")
    print(f"validation_mismatches={result.validation_mismatches}")
    for budget in range(6):
        print(
            f"budget={budget}: "
            f"count={result.successes_with_budget(budget)}, "
            f"gain={result.incremental_probability_with_budget(budget):.6%}, "
            f"survival={result.incremental_survival_share(budget):.6%}"
        )


if __name__ == "__main__":
    main()
