"""Independent exhaustive checks and a 60-card opponent-bonus benchmark."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.opponent_bonus_assembly import (  # noqa: E402
    OpponentBonusAssembly,
    optimize_setup_against_bonus,
)
from tools.setup_hand_value_policy import (  # noqa: E402
    SetupHandState,
    opening_hand_distribution,
    optimize_linear_mulligan_penalty,
)


def exhaustive_small(
    n: int, h: int, prizes: int, starters: int, groups: tuple[int, ...],
    draws: int, overlaps: tuple[int, ...] = ()
) -> Fraction:
    """Enumerate accepted hands, Prize subsets, and later bonus subsets."""
    cards = set(range(n))
    starter_set = set(range(starters))
    required = []
    basic_cursor = 0
    nonbasic_cursor = starters
    for count, shared in zip(groups, overlaps or (0,) * len(groups)):
        chosen = set(range(basic_cursor, basic_cursor + shared))
        chosen.update(range(nonbasic_cursor, nonbasic_cursor + count - shared))
        required.append(chosen)
        basic_cursor += shared
        nonbasic_cursor += count - shared

    good = total = 0
    for opening in combinations(range(n), h):
        opening_set = set(opening)
        if not opening_set.intersection(starter_set):
            continue
        remaining = cards - opening_set
        for prize in combinations(sorted(remaining), prizes):
            available = remaining - set(prize)
            for bonus in combinations(sorted(available), draws):
                seen = opening_set.union(bonus)
                good += int(all(seen.intersection(group) for group in required))
                total += 1
    return Fraction(good, total)


def test_small_enumeration() -> None:
    examples = [
        (9, 2, 1, 2, (1, 1), 0, (0, 0)),
        (9, 2, 1, 2, (1, 1), 2, (0, 0)),
        (9, 2, 1, 2, (2, 1), 1, (0, 0)),
        (10, 3, 2, 2, (1, 2), 2, (0, 0)),
        (9, 2, 1, 2, (2, 1), 1, (1, 0)),
        (10, 3, 2, 3, (2, 2), 2, (1, 1)),
    ]
    for n, h, prizes, starters, groups, draws, overlaps in examples:
        model = OpponentBonusAssembly(
            n, h, prizes, starters, groups, overlaps
        )
        exact = model.assembly_probability(draws)
        enumerated = exhaustive_small(
            n, h, prizes, starters, groups, draws, overlaps
        )
        assert exact == enumerated, (examples, exact, enumerated)


def own_value(state: SetupHandState) -> float:
    return float(state.feature_counts[0] > 0)


def test_benchmark() -> None:
    opponent = OpponentBonusAssembly(60, 7, 6, 12, (4, 4))
    points = [float(opponent.assembly_probability(i)) for i in range(13)]
    assert abs(points[0] - 0.129648289) < 1e-8
    assert abs(points[4] - 0.29114847) < 1e-7
    assert abs(points[12] - 0.611316918750416) < 1e-12
    assert all(a <= b for a, b in zip(points, points[1:]))
    increments = [b - a for a, b in zip(points, points[1:])]
    assert increments.index(max(increments)) == 4
    assert increments[0] < increments[1] < increments[2]
    assert increments[4] > increments[5] > increments[6]

    one_basic_target = OpponentBonusAssembly(9, 2, 1, 2, (2,), (2,))
    assert one_basic_target.assembly_probability(0) == 1
    assert one_basic_target.assembly_probability(3) == 1

    # The same required components can have different marginal draw value
    # when some of their copies are eligible starting Basics.
    one_basic_group = OpponentBonusAssembly(60, 7, 6, 12, (4, 4), (4, 0))
    two_basic_groups = OpponentBonusAssembly(60, 7, 6, 12, (4, 4), (4, 4))
    overlap_1 = [float(one_basic_group.assembly_probability(m)) for m in range(13)]
    overlap_2 = [float(two_basic_groups.assembly_probability(m)) for m in range(13)]
    assert abs(overlap_1[0] - 0.17965662) < 1e-7
    assert overlap_1[0] == overlap_2[0]
    assert overlap_1[0] > points[0]
    gains_1 = [b - a for a, b in zip(overlap_1, overlap_1[1:])]
    gains_2 = [b - a for a, b in zip(overlap_2, overlap_2[1:])]
    assert gains_1.index(max(gains_1)) == 3
    assert gains_2.index(max(gains_2)) == 0
    assert gains_2[0] > increments[0]

    policy = optimize_setup_against_bonus(
        opponent,
        payoff=6.0,
        draw_cap=12,
        own_forced_starters=4,
        own_optional_groups=(4,),
        own_feature_groups=(4,),
        own_terminal_value=own_value,
    )
    optional = {
        state
        for state, _ in opening_hand_distribution(60, 4, (4,), (4,))
        if state.forced_in_hand == 0 and sum(state.optional_counts) > 0
    }
    good = {state for state in optional if own_value(state) > 0}

    # At m=0,1 preserve only good optional hands; at m=2..5 accept all;
    # at m>=6 become selective again.
    expected = [good] * 2 + [optional] * 4 + [good] * 6
    for index, (step, kept) in enumerate(zip(policy.prefix_steps, expected)):
        assert step.optional_keep_states == kept, index
    assert policy.tail_step.optional_keep_states == good
    assert abs(policy.start.expected_utility - 0.252107) < 1e-5

    # Independent Bellman oracle, using the distribution of physical opening
    # hands. The existing solver is only used for the stationary zero-cost tail.
    distribution = opening_hand_distribution(60, 4, (4,), (4,))
    tail = optimize_linear_mulligan_penalty(
        60, 4, (4,), (4,), own_value, mulligan_penalty=0.0
    )
    value = tail.metrics.expected_utility
    costs = opponent.bonus_marginal_costs(6.0, draw_cap=12)
    for m in reversed(range(12)):
        reject = value - costs[m]
        value = sum(
            mass
            * (
                own_value(state)
                if state.forced_in_hand > 0
                else max(own_value(state), reject)
                if sum(state.optional_counts) > 0
                else reject
            )
            for state, mass in distribution
        )
        assert abs(value - policy.prefix_steps[m].expected_utility) < 1e-12

    # Independently mix the accepted-hand outcomes over the geometric
    # rejection process, including the exact zero-cost stationary tail.
    distribution = opening_hand_distribution(60, 4, (4,), (4,))
    probability_reaching = 1.0
    expected_opponent_assembly = 0.0
    expected_own_quality = 0.0
    expected_mulligans = 0.0
    probability_middle_keep = 0.0
    for count in range(200):
        step = (
            policy.prefix_steps[count]
            if count < 12
            else policy.tail_step
        )
        p_accept = step.acceptance_probability
        p_finished = probability_reaching * p_accept
        mean_kept_value = sum(
            mass * own_value(state)
            for state, mass in distribution
            if state.forced_in_hand > 0
            or state in step.optional_keep_states
        ) / p_accept
        expected_own_quality += p_finished * mean_kept_value
        expected_opponent_assembly += (
            p_finished
            * float(opponent.assembly_probability(min(count, 12)))
        )
        expected_mulligans += count * p_finished
        if 2 <= count <= 5:
            probability_middle_keep += probability_reaching * sum(
                mass
                for state, mass in distribution
                if state in optional and own_value(state) == 0
            )
        probability_reaching *= 1.0 - p_accept
    assert probability_reaching < 1e-14
    assert abs(expected_mulligans - 0.8897264934765043) < 1e-11
    assert abs(expected_opponent_assembly - 0.16439748741017363) < 1e-11
    assert abs(probability_middle_keep - 0.059230213077835575) < 1e-11
    net = expected_own_quality - 6.0 * (
        expected_opponent_assembly - points[0]
    )
    assert abs(net - policy.start.expected_utility) < 1e-12

    print("Probability of accepting an optional-only no-key hand in middle:", 
          f"{probability_middle_keep:.9%}")
    print(f"Optimal expected mulligans: {expected_mulligans:.9f}")
    print(f"Optimal expected opponent assembly: {expected_opponent_assembly:.9%}")

    print("When both target groups are all Basic starters, the marginal")
    print("bonus-draw assembly gain peaks at the first draw.")
    print("Opponent P(two groups) at bonus draws 0,1,4,12:")
    print(*(f"{i}: {points[i]:.9%}" for i in (0, 1, 4, 12)))
    print("Marginal assembly gains (percentage points), first 7 draws:")
    print(*(f"{100 * delta:.6f}" for delta in increments[:7]))
    print("Optimal no-key optional keeps at counts 0..11:")
    print(*(str(i) for i, step in enumerate(policy.prefix_steps)
            if step.optional_keep_states == optional))
    print(f"Optimal incremental net utility: {policy.start.expected_utility:.9f}")


if __name__ == "__main__":
    test_small_enumeration()
    test_benchmark()
    print("PASS: exhaustive combinatorics, nonlinear cost shape, and Bellman policy")
