"""Visible connector sequencing before Quick Ball in Harto's Raichu branch.

The validated baseline fixes Quick Ball as the first connector and optimizes only
its one-card payment. This module broadens the legal visible action family.

In the baseline branch, Quick Ball, at least one Gladion, and at least one
conservative disposable are already in hand. If Ultra Ball or Computer Search
is also visible, that stronger connector can be paid with exactly:
- the visible Quick Ball; and
- one visible conservative disposable.

That fixed payment is observation-consistent and preserves Gladion. The direct
connector searches Alolan Raichu if it is in deck; if Raichu is Prized, the
deck inspection establishes K1 and the preserved Gladion retrieves it.
"""

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
class VisibleConnectorSequencingResult:
    observable_branch_mass: float
    baseline_optimal_mass: float
    quick_ball_oracle_mass: float
    direct_visible_mass: float
    direct_visible_baseline_mass: float
    ultra_visible_mass: float
    ultra_visible_baseline_mass: float
    computer_visible_mass: float
    computer_visible_baseline_mass: float
    direct_overlap_mass: float
    forest_visible_mass: float
    direct_forest_overlap_mass: float
    combined_visible_mass: float
    combined_visible_baseline_mass: float
    direct_policy_mass: float
    combined_policy_mass: float
    observation_count: int
    direct_observation_count: int
    combined_observation_count: int

    def _conditional(self, value: float) -> float:
        return value / self.observable_branch_mass

    @property
    def baseline_optimal_success(self) -> float:
        return self._conditional(self.baseline_optimal_mass)

    @property
    def quick_ball_oracle_success(self) -> float:
        return self._conditional(self.quick_ball_oracle_mass)

    @property
    def direct_visible_fraction(self) -> float:
        return self._conditional(self.direct_visible_mass)

    @property
    def direct_visible_baseline_success(self) -> float:
        return self.direct_visible_baseline_mass / self.direct_visible_mass

    @property
    def ultra_visible_fraction(self) -> float:
        return self._conditional(self.ultra_visible_mass)

    @property
    def ultra_visible_baseline_success(self) -> float:
        return self.ultra_visible_baseline_mass / self.ultra_visible_mass

    @property
    def computer_visible_fraction(self) -> float:
        return self._conditional(self.computer_visible_mass)

    @property
    def computer_visible_baseline_success(self) -> float:
        return self.computer_visible_baseline_mass / self.computer_visible_mass

    @property
    def direct_overlap_fraction(self) -> float:
        return self._conditional(self.direct_overlap_mass)

    @property
    def forest_visible_fraction(self) -> float:
        return self._conditional(self.forest_visible_mass)

    @property
    def direct_forest_overlap_fraction(self) -> float:
        return self._conditional(self.direct_forest_overlap_mass)

    @property
    def combined_visible_fraction(self) -> float:
        return self._conditional(self.combined_visible_mass)

    @property
    def combined_visible_baseline_success(self) -> float:
        return self.combined_visible_baseline_mass / self.combined_visible_mass

    @property
    def direct_policy_success(self) -> float:
        return self._conditional(self.direct_policy_mass)

    @property
    def combined_policy_success(self) -> float:
        return self._conditional(self.combined_policy_mass)

    @property
    def direct_gain(self) -> float:
        return self.direct_policy_success - self.baseline_optimal_success

    @property
    def combined_gain(self) -> float:
        return self.combined_policy_success - self.baseline_optimal_success

    @property
    def direct_over_quick_ball_oracle(self) -> float:
        return self.direct_policy_success - self.quick_ball_oracle_success

    @property
    def combined_over_quick_ball_oracle(self) -> float:
        return self.combined_policy_success - self.quick_ball_oracle_success


def visible_connector_sequencing_snapshot() -> VisibleConnectorSequencingResult:
    """Compare legal visible connector-first policies on the exact baseline state space."""

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

    # Per visible observation:
    # [mass, QB-discard-Gladion success mass, QB-discard-disposable success mass,
    #  Ultra visible, Computer visible, hosted Forest Seal visible]
    rows: dict[
        tuple[str, tuple[int, ...]],
        list[float | bool],
    ] = defaultdict(lambda: [0.0, 0.0, 0.0, False, False, False])

    branch_mass = 0.0
    quick_ball_oracle_mass = 0.0

    for opening in _bounded_compositions(opening_hand_size, sizes):
        if opening[5] + opening[8] + opening[9] == 0:
            continue

        opening_mass = _multivariate_probability(opening, sizes) / accepted
        remaining = [size - count for size, count in zip(sizes, opening)]

        action_opening = list(opening)
        if opening[5] > 0:
            action_opening[5] -= 1
            active_kind = "crobat_v"
        elif opening[9] > 0:
            action_opening[9] -= 1
            active_kind = "other_starter"
        else:
            action_opening[8] -= 1
            active_kind = "disposable_starter"

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

            observation = (active_kind, tuple(hand))
            row = rows[observation]
            row[3] = hand[2] > 0
            row[4] = hand[3] > 0
            row[5] = (
                hand[4] > 0
                and (active_kind == "crobat_v" or hand[5] > 0)
            )

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

                grouped_other = deck[6] + deck[9] + deck[10] - prizes[8]
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

                row[0] = float(row[0]) + mass
                row[1] = float(row[1]) + mass * gladion_value
                row[2] = float(row[2]) + mass * disposable_value
                quick_ball_oracle_mass += mass * max(
                    gladion_value,
                    disposable_value,
                )

    baseline_optimal_mass = 0.0
    direct_visible_mass = 0.0
    direct_visible_baseline_mass = 0.0
    ultra_visible_mass = 0.0
    ultra_visible_baseline_mass = 0.0
    computer_visible_mass = 0.0
    computer_visible_baseline_mass = 0.0
    direct_overlap_mass = 0.0
    forest_visible_mass = 0.0
    direct_forest_overlap_mass = 0.0
    combined_visible_mass = 0.0
    combined_visible_baseline_mass = 0.0
    direct_policy_mass = 0.0
    combined_policy_mass = 0.0
    direct_observations = 0
    combined_observations = 0

    for (
        mass_raw,
        gladion_raw,
        disposable_raw,
        ultra_raw,
        computer_raw,
        forest_raw,
    ) in rows.values():
        mass = float(mass_raw)
        baseline = max(float(gladion_raw), float(disposable_raw))
        ultra = bool(ultra_raw)
        computer = bool(computer_raw)
        forest = bool(forest_raw)
        direct = ultra or computer
        combined = direct or forest

        baseline_optimal_mass += baseline

        if direct:
            direct_observations += 1
            direct_visible_mass += mass
            direct_visible_baseline_mass += baseline
            direct_policy_mass += mass
        else:
            direct_policy_mass += baseline

        if ultra:
            ultra_visible_mass += mass
            ultra_visible_baseline_mass += baseline
        if computer:
            computer_visible_mass += mass
            computer_visible_baseline_mass += baseline
        if ultra and computer:
            direct_overlap_mass += mass
        if forest:
            forest_visible_mass += mass
        if direct and forest:
            direct_forest_overlap_mass += mass

        if combined:
            combined_observations += 1
            combined_visible_mass += mass
            combined_visible_baseline_mass += baseline
            combined_policy_mass += mass
        else:
            combined_policy_mass += baseline

    baseline = k0_discard_policy_snapshot()
    if abs(branch_mass - baseline.observable_branch_mass) > 1e-12:
        raise AssertionError("branch mass diverged from validated baseline")
    if abs(baseline_optimal_mass - baseline.optimal_k0_success_mass) > 1e-12:
        raise AssertionError("K0 mass diverged from validated baseline")
    if abs(
        quick_ball_oracle_mass
        - baseline.hidden_state_oracle_success_mass
    ) > 1e-12:
        raise AssertionError("Quick Ball oracle diverged from validated baseline")

    return VisibleConnectorSequencingResult(
        observable_branch_mass=branch_mass,
        baseline_optimal_mass=baseline_optimal_mass,
        quick_ball_oracle_mass=quick_ball_oracle_mass,
        direct_visible_mass=direct_visible_mass,
        direct_visible_baseline_mass=direct_visible_baseline_mass,
        ultra_visible_mass=ultra_visible_mass,
        ultra_visible_baseline_mass=ultra_visible_baseline_mass,
        computer_visible_mass=computer_visible_mass,
        computer_visible_baseline_mass=computer_visible_baseline_mass,
        direct_overlap_mass=direct_overlap_mass,
        forest_visible_mass=forest_visible_mass,
        direct_forest_overlap_mass=direct_forest_overlap_mass,
        combined_visible_mass=combined_visible_mass,
        combined_visible_baseline_mass=combined_visible_baseline_mass,
        direct_policy_mass=direct_policy_mass,
        combined_policy_mass=combined_policy_mass,
        observation_count=len(rows),
        direct_observation_count=direct_observations,
        combined_observation_count=combined_observations,
    )


if __name__ == "__main__":
    result = visible_connector_sequencing_snapshot()
    print(
        f"direct visible={result.direct_visible_fraction:.9%} "
        f"baseline there={result.direct_visible_baseline_success:.9%}"
    )
    print(
        f"baseline={result.baseline_optimal_success:.9%} "
        f"direct-first={result.direct_policy_success:.9%} "
        f"combined={result.combined_policy_success:.9%}"
    )
    print(
        f"QB-first oracle={result.quick_ball_oracle_success:.9%} "
        f"direct-over-oracle_pp="
        f"{result.direct_over_quick_ball_oracle * 100:.9f}"
    )
