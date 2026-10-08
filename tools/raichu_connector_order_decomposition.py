"""Decompose why direct connector first beats Quick Ball first in Harto Raichu."""

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass

from raichu_k0_discard_policy import (
    _post_search_success_probability,
    k0_discard_policy_snapshot,
    visible_policy_choice,
)
from raichu_prize_access import (
    _bounded_compositions,
    _choose,
    _multivariate_probability,
    accepted_opening_probability,
)

BUCKETS = (
    "gladion__crobat_missing",
    "gladion__target_deck",
    "gladion__target_prized",
    "disposable__crobat_missing",
    "disposable__target_deck",
    "disposable__target_prized",
)


@dataclass(frozen=True)
class ConnectorOrderDecomposition:
    observable_branch_mass: float
    direct_visible_mass: float
    direct_baseline_success_mass: float
    bucket_mass: dict[str, float]
    bucket_baseline_success_mass: dict[str, float]

    @property
    def direct_gain_mass(self) -> float:
        return self.direct_visible_mass - self.direct_baseline_success_mass

    @property
    def direct_gain_pp(self) -> float:
        return 100 * self.direct_gain_mass / self.observable_branch_mass

    def deficit(self, bucket: str) -> float:
        return self.bucket_mass[bucket] - self.bucket_baseline_success_mass[bucket]

    def gain_pp(self, bucket: str) -> float:
        return 100 * self.deficit(bucket) / self.observable_branch_mass

    def share(self, bucket: str) -> float:
        return self.deficit(bucket) / self.direct_gain_mass


def connector_order_decomposition() -> ConnectorOrderDecomposition:
    deck_size = 60
    prize_count = 6
    opening_hand_size = 7
    sizes = (1, 2, 3, 1, 1, 2, 2, 11, 1, 13, 23)
    accepted = accepted_opening_probability(
        deck_size, sizes[5] + sizes[8] + sizes[9], opening_hand_size
    )
    draw_pool_size = deck_size - opening_hand_size
    prize_denominator = _choose(draw_pool_size - 1, prize_count)

    branch_mass = 0.0
    direct_mass = 0.0
    direct_baseline = 0.0
    bucket_mass = defaultdict(float)
    bucket_success = defaultdict(float)

    for opening in _bounded_compositions(opening_hand_size, sizes):
        if opening[5] + opening[8] + opening[9] == 0:
            continue

        opening_mass = _multivariate_probability(opening, sizes) / accepted
        remaining = [size - count for size, count in zip(sizes, opening)]
        action_opening = list(opening)
        if opening[5] > 0:
            action_opening[5] -= 1
        elif opening[9] > 0:
            action_opening[9] -= 1
        else:
            action_opening[8] -= 1

        for draw_category, draw_count in enumerate(remaining):
            if draw_count == 0:
                continue

            hand = action_opening.copy()
            hand[draw_category] += 1
            prize_pool = remaining.copy()
            prize_pool[draw_category] -= 1
            base_mass = opening_mass * draw_count / draw_pool_size

            if (
                hand[0] > 0
                or hand[6] < 1
                or hand[1] < 1
                or hand[7] + hand[8] < 1
            ):
                continue

            direct_visible = hand[2] > 0 or hand[3] > 0
            choice = visible_policy_choice(tuple(hand))
            focused_pool = (
                prize_pool[0], prize_pool[1], prize_pool[2],
                prize_pool[3], prize_pool[4], prize_pool[5],
                prize_pool[7], prize_pool[8],
                prize_pool[6] + prize_pool[9] + prize_pool[10],
            )

            for prizes in _bounded_compositions(prize_count, focused_pool):
                ways = 1
                for size, count in zip(focused_pool, prizes):
                    ways *= _choose(size, count)
                if ways == 0:
                    continue

                mass = base_mass * ways / prize_denominator
                branch_mass += mass
                if not direct_visible:
                    continue

                deck = prize_pool.copy()
                for index, count in zip(
                    (0, 1, 2, 3, 4, 5, 7, 8), prizes[:8]
                ):
                    deck[index] -= count
                deck[10] = (
                    deck[6] + deck[9] + deck[10] - prizes[8]
                )
                deck[6] = 0
                deck[9] = 0

                success, target_prized, crobat_available = (
                    _post_search_success_probability(
                        hand=tuple(hand),
                        deck=tuple(deck),
                        discard_choice=choice,
                        deck_size=deck_size,
                        prize_count=prize_count,
                        opening_hand_size=opening_hand_size,
                        computer_discard_cost=2,
                    )
                )

                if not crobat_available:
                    state = "crobat_missing"
                elif target_prized:
                    state = "target_prized"
                else:
                    state = "target_deck"
                bucket = f"{choice}__{state}"

                direct_mass += mass
                direct_baseline += mass * success
                bucket_mass[bucket] += mass
                bucket_success[bucket] += mass * success

    baseline = k0_discard_policy_snapshot()
    if abs(branch_mass - baseline.observable_branch_mass) > 1e-12:
        raise AssertionError("branch mass mismatch")

    for bucket in BUCKETS:
        bucket_mass[bucket] += 0.0
        bucket_success[bucket] += 0.0

    result = ConnectorOrderDecomposition(
        observable_branch_mass=branch_mass,
        direct_visible_mass=direct_mass,
        direct_baseline_success_mass=direct_baseline,
        bucket_mass=dict(bucket_mass),
        bucket_baseline_success_mass=dict(bucket_success),
    )
    if abs(
        sum(result.deficit(bucket) for bucket in BUCKETS)
        - result.direct_gain_mass
    ) > 1e-12:
        raise AssertionError("deficit decomposition mismatch")
    return result


if __name__ == "__main__":
    result = connector_order_decomposition()
    print(f"direct_visible_mass={result.direct_visible_mass!r}")
    print(f"direct_baseline_mass={result.direct_baseline_success_mass!r}")
    print(f"direct_gain_pp={result.direct_gain_pp!r}")
    for bucket in BUCKETS:
        print(
            f"{bucket}: mass={result.bucket_mass[bucket]!r} "
            f"baseline={result.bucket_baseline_success_mass[bucket]!r} "
            f"gain_pp={result.gain_pp(bucket)!r} "
            f"share={result.share(bucket)!r}"
        )
