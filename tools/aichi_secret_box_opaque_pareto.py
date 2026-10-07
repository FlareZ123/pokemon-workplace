"""Pareto frontier for initial and total opaque discard burden.

For the paired Aichi Vileplume Secret Box first-turn model, each successful
continuation is assigned two costs:

1. cards from the compressed "other" category in Secret Box's mandatory
   three-card discard;
2. cards from "other" used across every represented discard payment.

The solver preserves every nondominated cost pair. This reveals whether the
line that minimizes the first payment also minimizes total opaque consumption.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import random

from aichi_secret_box_initial_opaque_frontier import (
    _resolve_box_outputs,
    state_min_initial_opaque,
)
from aichi_secret_box_opaque_discard_frontier import (
    state_min_opaque_discards,
)
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
CostPair = tuple[int, int]
Frontier = tuple[CostPair, ...]


@dataclass(frozen=True)
class OpaqueParetoResult:
    trials: int
    incremental_successes: int
    missing_frontiers: int
    tradeoff_states: int
    frontier_size_histogram: tuple[tuple[int, int], ...]
    frontier_shape_histogram: tuple[tuple[Frontier, int], ...]
    total_penalty_if_minimize_initial: tuple[tuple[int, int], ...]
    initial_penalty_if_minimize_total: tuple[tuple[int, int], ...]
    validation_states: int
    initial_validation_mismatches: int
    total_validation_mismatches: int


def _prune(pairs) -> Frontier:
    unique = sorted(set(pairs))
    keep: list[CostPair] = []
    for candidate in unique:
        if any(
            other != candidate
            and other[0] <= candidate[0]
            and other[1] <= candidate[1]
            for other in unique
        ):
            continue
        keep.append(candidate)
    return tuple(keep)


def _shift(
    frontier: Frontier,
    *,
    initial: int = 0,
    total: int = 0,
) -> tuple[CostPair, ...]:
    return tuple(
        (box_cost + initial, total_cost + total)
        for box_cost, total_cost in frontier
    )


@lru_cache(maxsize=None)
def _core_pareto(state, box_used: bool) -> Frontier:
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
        return ((0, 0),) if box_used else ()

    candidates: list[CostPair] = []

    if not bunnelby_in_play and hand[HAND_INDEX["bunnelby"]] > 0:
        candidates.extend(
            _core_pareto(
                (
                    _dec(hand, HAND_INDEX["bunnelby"]),
                    deck,
                    supporter_used,
                    stadium_used,
                    fan_used,
                    True,
                    fan_rotom_in_play,
                ),
                box_used,
            )
        )

    if not fan_rotom_in_play and hand[HAND_INDEX["fan_rotom"]] > 0:
        candidates.extend(
            _core_pareto(
                (
                    _dec(hand, HAND_INDEX["fan_rotom"]),
                    deck,
                    supporter_used,
                    stadium_used,
                    fan_used,
                    bunnelby_in_play,
                    True,
                ),
                box_used,
            )
        )

    if (
        fan_rotom_in_play
        and not fan_used
        and not bunnelby_in_play
        and deck[DECK_INDEX["bunnelby"]] > 0
    ):
        candidates.extend(
            _core_pareto(
                (
                    _inc(hand, HAND_INDEX["bunnelby"]),
                    _dec(deck, DECK_INDEX["bunnelby"]),
                    supporter_used,
                    stadium_used,
                    True,
                    bunnelby_in_play,
                    fan_rotom_in_play,
                ),
                box_used,
            )
        )

    if (
        not stadium_used
        and hand[HAND_INDEX["artazon"]] > 0
        and not bunnelby_in_play
        and hand[HAND_INDEX["bunnelby"]] == 0
        and deck[DECK_INDEX["bunnelby"]] > 0
    ):
        candidates.extend(
            _core_pareto(
                (
                    _dec(hand, HAND_INDEX["artazon"]),
                    _dec(deck, DECK_INDEX["bunnelby"]),
                    supporter_used,
                    True,
                    fan_used,
                    True,
                    fan_rotom_in_play,
                ),
                box_used,
            )
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

        candidates.extend(
            _core_pareto(
                (
                    tuple(next_hand),
                    tuple(next_deck),
                    supporter_used,
                    stadium_used,
                    fan_used,
                    bunnelby_in_play,
                    fan_rotom_in_play,
                ),
                box_used,
            )
        )

    if not box_used and hand[HAND_INDEX["secret_box"]] > 0:
        base_hand = _dec(hand, HAND_INDEX["secret_box"])
        if sum(base_hand) >= 3:
            for selection in _discard_selections(base_hand, 3):
                next_hand, next_deck = _resolve_box_outputs(
                    base_hand,
                    deck,
                    selection,
                )
                cost = selection[OPAQUE_INDEX]
                candidates.extend(
                    _shift(
                        _core_pareto(
                            (
                                next_hand,
                                next_deck,
                                supporter_used,
                                stadium_used,
                                fan_used,
                                bunnelby_in_play,
                                fan_rotom_in_play,
                            ),
                            True,
                        ),
                        initial=cost,
                        total=cost,
                    )
                )

    if hand[HAND_INDEX["gnh"]] > 0 and not supporter_used:
        base_hand = _dec(hand, HAND_INDEX["gnh"])

        next_hand = list(base_hand)
        next_deck = list(deck)
        if next_deck[DECK_INDEX["artazon"]] > 0:
            next_deck[DECK_INDEX["artazon"]] -= 1
            next_hand[HAND_INDEX["artazon"]] += 1

        candidates.extend(
            _core_pareto(
                (
                    tuple(next_hand),
                    tuple(next_deck),
                    True,
                    stadium_used,
                    fan_used,
                    bunnelby_in_play,
                    fan_rotom_in_play,
                ),
                box_used,
            )
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

                candidates.extend(
                    _shift(
                        _core_pareto(
                            (
                                tuple(candidate_hand),
                                tuple(candidate_deck),
                                True,
                                stadium_used,
                                fan_used,
                                bunnelby_in_play,
                                fan_rotom_in_play,
                            ),
                            box_used,
                        ),
                        total=selection[OPAQUE_INDEX],
                    )
                )

    return _prune(candidates)


def state_opaque_pareto(raw_state) -> Frontier:
    hand, remaining, active, top_five = raw_state
    picks = [None]
    if active == "Jirachi":
        picks.extend(sorted(set(top_five) & STELLAR_TRAINERS))

    candidates: list[CostPair] = []
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
        candidates.extend(_core_pareto(state, False))

    return _prune(candidates)


def analyze_opaque_pareto(
    trials: int,
    *,
    seed: int = 20261007,
    validation_incremental_states: int = 10_000,
) -> OpaqueParetoResult:
    rng = random.Random(seed)
    incremental = 0
    missing = 0
    tradeoff = 0
    sizes: Counter[int] = Counter()
    shapes: Counter[Frontier] = Counter()
    total_penalties: Counter[int] = Counter()
    initial_penalties: Counter[int] = Counter()
    validated = 0
    initial_mismatch = 0
    total_mismatch = 0

    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            baseline_state = _raw_state(BASE_DECK, order)
            if baseline_state is not None:
                break

        secret_state = _raw_state(SECRET_BOX_DECK, order)
        if secret_state is None:
            raise AssertionError("ACE SPEC substitution changed setup acceptance")

        if not _state_succeeds(secret_state) or _state_succeeds(baseline_state):
            continue

        incremental += 1
        frontier = state_opaque_pareto(secret_state)
        if not frontier:
            missing += 1
            continue

        sizes[len(frontier)] += 1
        shapes[frontier] += 1

        min_initial = min(pair[0] for pair in frontier)
        min_total = min(pair[1] for pair in frontier)
        best_total_at_min_initial = min(
            total for initial, total in frontier
            if initial == min_initial
        )
        best_initial_at_min_total = min(
            initial for initial, total in frontier
            if total == min_total
        )
        total_penalty = best_total_at_min_initial - min_total
        initial_penalty = best_initial_at_min_total - min_initial
        total_penalties[total_penalty] += 1
        initial_penalties[initial_penalty] += 1
        tradeoff += int(
            not any(
                initial == min_initial and total == min_total
                for initial, total in frontier
            )
        )

        if validated < validation_incremental_states:
            initial_scalar = state_min_initial_opaque(secret_state)
            total_scalar = state_min_opaque_discards(secret_state)
            initial_mismatch += int(initial_scalar != min_initial)
            total_mismatch += int(total_scalar != min_total)
            validated += 1

    return OpaqueParetoResult(
        trials=trials,
        incremental_successes=incremental,
        missing_frontiers=missing,
        tradeoff_states=tradeoff,
        frontier_size_histogram=tuple(sorted(sizes.items())),
        frontier_shape_histogram=tuple(
            sorted(shapes.items(), key=lambda item: (-item[1], item[0]))
        ),
        total_penalty_if_minimize_initial=tuple(sorted(total_penalties.items())),
        initial_penalty_if_minimize_total=tuple(sorted(initial_penalties.items())),
        validation_states=validated,
        initial_validation_mismatches=initial_mismatch,
        total_validation_mismatches=total_mismatch,
    )


def main() -> None:
    result = analyze_opaque_pareto(100_000)
    print(f"trials={result.trials}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"missing_frontiers={result.missing_frontiers}")
    print(f"tradeoff_states={result.tradeoff_states}")
    print(f"frontier_size_histogram={dict(result.frontier_size_histogram)}")
    print("frontier_shape_histogram=")
    for frontier, count in result.frontier_shape_histogram:
        print(f"  {frontier}: {count}")
    print(
        "total_penalty_if_minimize_initial="
        f"{dict(result.total_penalty_if_minimize_initial)}"
    )
    print(
        "initial_penalty_if_minimize_total="
        f"{dict(result.initial_penalty_if_minimize_total)}"
    )
    print(f"validation_states={result.validation_states}")
    print(
        "initial_validation_mismatches="
        f"{result.initial_validation_mismatches}"
    )
    print(
        "total_validation_mismatches="
        f"{result.total_validation_mismatches}"
    )


if __name__ == "__main__":
    main()
