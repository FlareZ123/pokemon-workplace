"""Reproduce asymmetric Prize knowledge after an unrevealed Prize take."""

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_belief_kernel import PrizeBelief
from prize_take_conservation import take_observed_random_prize
from prize_take_information_asymmetry import (
    expected_group_count,
    group_probability,
    remove_unobserved_random_prize,
    remove_unobserved_prizes,
)


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def assert_same_belief(actual: PrizeBelief, expected: PrizeBelief) -> None:
    assert actual.groups == expected.groups
    assert actual.prize_count == expected.prize_count
    actual_rows = dict(actual.masses)
    expected_rows = dict(expected.masses)
    assert set(actual_rows) == set(expected_rows)
    for state in actual_rows:
        assert_close(actual_rows[state], expected_rows[state])


def labeled_remaining_card_distribution() -> dict[str, float]:
    cards = ("A", "B", "F1", "F2", "F3")
    prize_sets = tuple(combinations(cards, 2))
    output = {card: 0.0 for card in cards}

    for prize_set in prize_sets:
        set_probability = 1.0 / len(prize_sets)
        for removed in prize_set:
            path_probability = set_probability / len(prize_set)
            remaining = next(card for card in prize_set if card != removed)
            output[remaining] += path_probability

    return output


def main() -> None:
    belief = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 1},
        pool_size=5,
        prize_count=2,
    )

    # The taking player sees A before it leaves the Prize set.
    taker = take_observed_random_prize(belief, "A")
    assert taker.prize_count == 1
    assert_close(group_probability(taker, "A"), 0.0)
    assert_close(group_probability(taker, "B"), 1.0 / 4.0)

    # The opponent sees the Prize count fall but not the card identity.
    observer = remove_unobserved_random_prize(belief)
    assert observer.prize_count == 1
    assert_close(observer.probability_mass(), 1.0)
    assert_close(group_probability(observer, "A"), 1.0 / 5.0)
    assert_close(group_probability(observer, "B"), 1.0 / 5.0)
    assert_close(expected_group_count(observer, "A"), 1.0 / 5.0)
    assert_close(expected_group_count(observer, "B"), 1.0 / 5.0)
    assert observer.entropy_bits() > taker.entropy_bits()

    labeled = labeled_remaining_card_distribution()
    assert_close(labeled["A"], 1.0 / 5.0)
    assert_close(labeled["B"], 1.0 / 5.0)
    assert_close(sum(labeled.values()), 1.0)

    # Stronger property: a uniform random Prize subset followed by hidden random
    # removals leaves a uniform smaller Prize subset from the original pool.
    prior = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 2},
        pool_size=7,
        prize_count=3,
    )
    after_two_hidden_takes = remove_unobserved_prizes(prior, 2)
    direct_one_prize_prior = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 2},
        pool_size=7,
        prize_count=1,
    )
    assert_same_belief(after_two_hidden_takes, direct_one_prize_prior)

    unchanged = remove_unobserved_prizes(prior, 0)
    assert unchanged == prior

    try:
        remove_unobserved_prizes(prior, 4)
    except ValueError:
        pass
    else:
        raise AssertionError("removed more hidden Prizes than remain")

    empty = PrizeBelief.from_exact({}, prize_count=0)
    try:
        remove_unobserved_random_prize(empty)
    except ValueError:
        pass
    else:
        raise AssertionError("removed hidden Prize from empty Prize set")

    print("Prize-taking information-asymmetry regressions passed")


if __name__ == "__main__":
    main()
