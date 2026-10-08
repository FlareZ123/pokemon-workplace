"""Legal pre-Quick-Ball Forest Seal sequencing in the Harto Raichu model."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from raichu_k0_discard_policy import (
    _post_search_success_probability,
    k0_discard_policy_snapshot,
)
from raichu_prize_access import (
    _bounded_compositions,
    _choose,
    _multivariate_probability,
    accepted_opening_probability,
)


@dataclass(frozen=True)
class ForestSealPresearchResult:
    observable_branch_mass: float
    baseline_optimal_mass: float
    improved_optimal_mass: float
    hidden_state_oracle_mass: float
    hosted_forest_mass: float
    hosted_forest_baseline_success_mass: float
    observation_count: int
    hosted_observation_count: int

    def _conditional(self, value: float) -> float:
        return value / self.observable_branch_mass

    @property
    def baseline_optimal_success(self) -> float:
        return self._conditional(self.baseline_optimal_mass)

    @property
    def improved_optimal_success(self) -> float:
        return self._conditional(self.improved_optimal_mass)

    @property
    def hidden_state_oracle_success(self) -> float:
        return self._conditional(self.hidden_state_oracle_mass)

    @property
    def hosted_forest_fraction(self) -> float:
        return self._conditional(self.hosted_forest_mass)

    @property
    def hosted_forest_baseline_success(self) -> float:
        return (
            self.hosted_forest_baseline_success_mass
            / self.hosted_forest_mass
        )

    @property
    def gain(self) -> float:
        return self.improved_optimal_success - self.baseline_optimal_success

    @property
    def remaining_oracle_gap(self) -> float:
        return self.hidden_state_oracle_success - self.improved_optimal_success

    @property
    def recovered_oracle_gap_fraction(self) -> float:
        original_gap = (
            self.hidden_state_oracle_mass
            - self.baseline_optimal_mass
        )
        return (
            self.improved_optimal_mass
            - self.baseline_optimal_mass
        ) / original_gap


def forest_seal_presearch_snapshot() -> ForestSealPresearchResult:
    """Re-evaluate the validated Harto branch with hosted Forest Seal first."""

    deck_size = 60
    prize_count = 6
    opening_hand_size = 7
    computer_discard_cost = 2

    # target, Gladion, Ultra Ball, Computer Search, Forest Seal Stone,
    # Crobat V, Quick Ball, disposable nonstarter, disposable starter,
    # other starter, other
    sizes = (1, 2, 3, 1, 1, 2, 2, 11, 1, 13, 23)
    starter_cards = sizes[5] + sizes[8] + sizes[9]
    accepted = accepted_opening_probability(
        deck_size,
        starter_cards,
        opening_hand_size,
    )
    draw_pool_size = deck_size - opening_hand_size
    prize_pool_size = draw_pool_size - 1
    prize_denominator = _choose(prize_pool_size, prize_count)

    # [mass, discard-Gladion success mass, discard-disposable success mass,
    #  hosted Forest Seal observable]
    rows: dict[
        tuple[str, tuple[int, ...]],
        list[float | bool],
    ] = defaultdict(lambda: [0.0, 0.0, 0.0, False])

    branch_mass = 0.0
    oracle_mass = 0.0

    for opening in _bounded_compositions(opening_hand_size, sizes):
        if opening[5] + opening[8] + opening[9] == 0:
            continue

        opening_mass = _multivariate_probability(opening, sizes) / accepted
        remaining = [size - count for size, count in zip(sizes, opening)]

        hand0 = list(opening)
        if opening[5] > 0:
            hand0[5] -= 1
            active_kind = "crobat_v"
        elif opening[9] > 0:
            hand0[9] -= 1
            active_kind = "other_starter"
        else:
            hand0[8] -= 1
            active_kind = "disposable_starter"

        for draw_category, draw_count in enumerate(remaining):
            if draw_count == 0:
                continue

            hand = hand0.copy()
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

            observation = (active_kind, tuple(hand))
            hosted_forest = (
                hand[4] > 0
                and (active_kind == "crobat_v" or hand[5] > 0)
            )
            if hosted_forest:
                rows[observation][3] = True

            focused_pool = (
                prize_pool[0],
                prize_pool[1],
                prize_pool[2],
                prize_pool[3],
                prize_pool[4],
                prize_pool[5],
                prize_pool[7],
                prize_pool[8],
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

                deck = prize_pool.copy()
                for index, count in zip(
                    (0, 1, 2, 3, 4, 5, 7, 8),
                    prizes[:8],
                ):
                    deck[index] -= count

                grouped_other = (
                    deck[6] + deck[9] + deck[10] - prizes[8]
                )
                if grouped_other < 0:
                    raise AssertionError("invalid grouped Prize count")
                deck[6] = 0
                deck[9] = 0
                deck[10] = grouped_other

                gladion_value, _, _ = _post_search_success_probability(
                    hand=tuple(hand),
                    deck=tuple(deck),
                    discard_choice="gladion",
                    deck_size=deck_size,
                    prize_count=prize_count,
                    opening_hand_size=opening_hand_size,
                    computer_discard_cost=computer_discard_cost,
                )
                disposable_value, _, _ = _post_search_success_probability(
                    hand=tuple(hand),
                    deck=tuple(deck),
                    discard_choice="disposable",
                    deck_size=deck_size,
                    prize_count=prize_count,
                    opening_hand_size=opening_hand_size,
                    computer_discard_cost=computer_discard_cost,
                )

                row = rows[observation]
                row[0] = float(row[0]) + mass
                row[1] = float(row[1]) + mass * gladion_value
                row[2] = float(row[2]) + mass * disposable_value
                oracle_mass += mass * max(gladion_value, disposable_value)

    baseline_mass = 0.0
    improved_mass = 0.0
    hosted_mass = 0.0
    hosted_baseline_mass = 0.0
    hosted_observations = 0

    for mass_raw, gladion_raw, disposable_raw, hosted_raw in rows.values():
        mass = float(mass_raw)
        baseline = max(float(gladion_raw), float(disposable_raw))
        baseline_mass += baseline

        if bool(hosted_raw):
            # Star Alchemy either searches deck-resident Raichu directly or
            # reveals that it is Prized, after which the branch's visible
            # Gladion retrieves it. This action is observation-consistent.
            improved_mass += mass
            hosted_mass += mass
            hosted_baseline_mass += baseline
            hosted_observations += 1
        else:
            improved_mass += baseline

    baseline = k0_discard_policy_snapshot()
    if abs(branch_mass - baseline.observable_branch_mass) > 1e-12:
        raise AssertionError("branch mass diverged from validated baseline")
    if abs(baseline_mass - baseline.optimal_k0_success_mass) > 1e-12:
        raise AssertionError("K0 mass diverged from validated baseline")
    if abs(oracle_mass - baseline.hidden_state_oracle_success_mass) > 1e-12:
        raise AssertionError("oracle mass diverged from validated baseline")

    return ForestSealPresearchResult(
        observable_branch_mass=branch_mass,
        baseline_optimal_mass=baseline_mass,
        improved_optimal_mass=improved_mass,
        hidden_state_oracle_mass=oracle_mass,
        hosted_forest_mass=hosted_mass,
        hosted_forest_baseline_success_mass=hosted_baseline_mass,
        observation_count=len(rows),
        hosted_observation_count=hosted_observations,
    )


if __name__ == "__main__":
    result = forest_seal_presearch_snapshot()
    print(f"hosted fraction={result.hosted_forest_fraction:.9%}")
    print(
        f"hosted baseline={result.hosted_forest_baseline_success:.9%}"
    )
    print(
        f"baseline={result.baseline_optimal_success:.9%} "
        f"improved={result.improved_optimal_success:.9%} "
        f"gain_pp={result.gain * 100:.9f}"
    )
    print(
        f"remaining_oracle_gap_pp="
        f"{result.remaining_oracle_gap * 100:.9f} "
        f"recovered={result.recovered_oracle_gap_fraction:.9%}"
    )
