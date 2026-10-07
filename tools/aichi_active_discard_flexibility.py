"""Measure starting-Active effects on Guzma & Hala discard flexibility.

This analysis is restricted to accepted Aichi Vileplume openings without Jirachi
where the current Active heuristic and a Bunnelby-first heuristic differ. It
holds the sampled state fixed and enumerates every card-name discard pair that
can still execute each named endpoint through the same G&H route model.

The metric is structural rather than a full DCI score:
- number of feasible discard pairs;
- minimum number of singleton-deck cards in a feasible pair.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_active_choice import (
    _sample_state,
    bunnelby_first_active,
    default_active,
)
from aichi_vileplume_als import (
    ANY_ROUTE_ENDPOINTS,
    DECK_COUNTS,
    _basic_possible_with_artazon_state,
    _stage_targets_remain,
)


@dataclass(frozen=True)
class RouteFlex:
    natural: bool
    feasible_pairs: frozenset[tuple[str, str]]

    @property
    def succeeds(self) -> bool:
        return self.natural or bool(self.feasible_pairs)

    @property
    def min_singletons(self) -> int | None:
        if self.natural:
            return 0
        if not self.feasible_pairs:
            return None
        return min(
            int(DECK_COUNTS[first] == 1) + int(DECK_COUNTS[second] == 1)
            for first, second in self.feasible_pairs
        )


@dataclass(frozen=True)
class FlexResult:
    trials: int
    policy_difference_states: int
    both_gnh: dict[str, int]
    bunnelby_more_pairs: dict[str, int]
    bunnelby_fewer_pairs: dict[str, int]
    bunnelby_lower_singleton_floor: dict[str, int]
    bunnelby_higher_singleton_floor: dict[str, int]
    default_natural_only: dict[str, int]
    bunnelby_natural_only: dict[str, int]
    pair_totals_default: dict[str, int]
    pair_totals_bunnelby: dict[str, int]


def _hand_for_active(state, active: str) -> Counter[str]:
    hand = Counter(state.opening + (state.draw,))
    hand[active] -= 1
    if hand[active] == 0:
        del hand[active]
    return hand


def route_flex(state, active: str, endpoint: str) -> RouteFlex:
    hand = _hand_for_active(state, active)
    remaining = state.remaining.copy()
    required = ANY_ROUTE_ENDPOINTS[endpoint]

    if not _stage_targets_remain(remaining, endpoint):
        return RouteFlex(False, frozenset())

    if (
        hand["Technical Machine: Evolution"] > 0
        and hand["Jet Energy"] > 0
        and _basic_possible_with_artazon_state(
            hand,
            remaining,
            active,
            required,
            artazon_available=hand["Artazon"] > 0,
        )
    ):
        return RouteFlex(True, frozenset())

    work_hand = hand.copy()
    work_deck = remaining.copy()
    if work_hand["Guzma & Hala"] > 0:
        pass
    elif work_hand["Tag Call"] > 0 and work_deck["Guzma & Hala"] > 0:
        work_hand["Tag Call"] -= 1
        if work_hand["Tag Call"] == 0:
            del work_hand["Tag Call"]
        work_deck["Guzma & Hala"] -= 1
        work_hand["Guzma & Hala"] += 1
    else:
        return RouteFlex(False, frozenset())

    work_hand["Guzma & Hala"] -= 1
    if work_hand["Guzma & Hala"] == 0:
        del work_hand["Guzma & Hala"]

    physical_cards: list[str] = []
    for card, copies in work_hand.items():
        physical_cards.extend([card] * copies)

    pairs = {
        tuple(sorted((physical_cards[left], physical_cards[right])))
        for left in range(len(physical_cards))
        for right in range(left + 1, len(physical_cards))
    }

    feasible: set[tuple[str, str]] = set()
    for first, second in pairs:
        candidate_hand = work_hand.copy()
        candidate_hand[first] -= 1
        if candidate_hand[first] == 0:
            del candidate_hand[first]
        candidate_hand[second] -= 1
        if candidate_hand[second] == 0:
            del candidate_hand[second]

        candidate_deck = work_deck.copy()
        searchable = True
        for card in ("Technical Machine: Evolution", "Jet Energy"):
            if candidate_hand[card] == 0:
                if candidate_deck[card] == 0:
                    searchable = False
                    break
                candidate_deck[card] -= 1
                candidate_hand[card] += 1
        if not searchable:
            continue

        if _basic_possible_with_artazon_state(
            candidate_hand,
            candidate_deck,
            active,
            required,
            artazon_available=(
                candidate_hand["Artazon"] > 0
                or candidate_deck["Artazon"] > 0
            ),
        ):
            feasible.add((first, second))

    return RouteFlex(False, frozenset(feasible))


def simulate_flex(
    trials: int,
    *,
    seed: int = 20261007,
) -> FlexResult:
    rng = random.Random(seed)
    policy_difference_states = 0
    both_gnh: Counter[str] = Counter()
    more: Counter[str] = Counter()
    fewer: Counter[str] = Counter()
    lower_singleton: Counter[str] = Counter()
    higher_singleton: Counter[str] = Counter()
    default_natural_only: Counter[str] = Counter()
    bunnelby_natural_only: Counter[str] = Counter()
    pair_default: Counter[str] = Counter()
    pair_bunnelby: Counter[str] = Counter()

    for _ in range(trials):
        state = _sample_state(rng)
        basics = state.opening_basics
        if "Jirachi" in basics or "Bunnelby" not in basics:
            continue

        default_name = default_active(basics)
        bunnelby_name = bunnelby_first_active(basics)
        if default_name == bunnelby_name:
            continue

        policy_difference_states += 1
        for endpoint in ANY_ROUTE_ENDPOINTS:
            default = route_flex(state, default_name, endpoint)
            bunnelby = route_flex(state, bunnelby_name, endpoint)

            if default.natural and not bunnelby.natural:
                default_natural_only[endpoint] += 1
            if bunnelby.natural and not default.natural:
                bunnelby_natural_only[endpoint] += 1

            if (
                not default.natural
                and not bunnelby.natural
                and default.feasible_pairs
                and bunnelby.feasible_pairs
            ):
                both_gnh[endpoint] += 1
                d_count = len(default.feasible_pairs)
                b_count = len(bunnelby.feasible_pairs)
                pair_default[endpoint] += d_count
                pair_bunnelby[endpoint] += b_count
                if b_count > d_count:
                    more[endpoint] += 1
                elif b_count < d_count:
                    fewer[endpoint] += 1

                d_floor = default.min_singletons
                b_floor = bunnelby.min_singletons
                if b_floor is None or d_floor is None:
                    raise AssertionError("successful G&H route lacked discard pair")
                if b_floor < d_floor:
                    lower_singleton[endpoint] += 1
                elif b_floor > d_floor:
                    higher_singleton[endpoint] += 1

    return FlexResult(
        trials=trials,
        policy_difference_states=policy_difference_states,
        both_gnh=dict(both_gnh),
        bunnelby_more_pairs=dict(more),
        bunnelby_fewer_pairs=dict(fewer),
        bunnelby_lower_singleton_floor=dict(lower_singleton),
        bunnelby_higher_singleton_floor=dict(higher_singleton),
        default_natural_only=dict(default_natural_only),
        bunnelby_natural_only=dict(bunnelby_natural_only),
        pair_totals_default=dict(pair_default),
        pair_totals_bunnelby=dict(pair_bunnelby),
    )


def main() -> None:
    trials = 100_000
    result = simulate_flex(trials)
    print(f"trials={trials}, seed=20261007")
    print(f"policy_difference_states={result.policy_difference_states}")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        both = result.both_gnh.get(endpoint, 0)
        d_pairs = result.pair_totals_default.get(endpoint, 0)
        b_pairs = result.pair_totals_bunnelby.get(endpoint, 0)
        print(
            endpoint,
            f"both_gnh={both}",
            f"mean_pairs_default={d_pairs / both if both else 0:.4f}",
            f"mean_pairs_bunnelby={b_pairs / both if both else 0:.4f}",
            f"b_more={result.bunnelby_more_pairs.get(endpoint, 0)}",
            f"b_fewer={result.bunnelby_fewer_pairs.get(endpoint, 0)}",
            "b_lower_singleton="
            f"{result.bunnelby_lower_singleton_floor.get(endpoint, 0)}",
            "b_higher_singleton="
            f"{result.bunnelby_higher_singleton_floor.get(endpoint, 0)}",
            "default_natural_only="
            f"{result.default_natural_only.get(endpoint, 0)}",
            "bunnelby_natural_only="
            f"{result.bunnelby_natural_only.get(endpoint, 0)}",
        )


if __name__ == "__main__":
    main()
