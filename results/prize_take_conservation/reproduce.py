"""Reproduce physical Prize taking plus grouped belief updates."""

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from prize_belief_kernel import PrizeBelief
from prize_take_conservation import (
    exchangeable_prize_count,
    observation_probability,
    take_observed_prizes,
    take_observed_random_prize,
    take_prizes_and_update_belief,
)


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def labeled_toy_metrics() -> tuple[float, float]:
    cards = ("A", "B", "F1", "F2", "F3")
    prize_sets = tuple(combinations(cards, 2))
    event_a = 0.0
    event_a_then_b_remaining = 0.0

    for prize_set in prize_sets:
        set_probability = 1.0 / len(prize_sets)
        for taken in prize_set:
            path_probability = set_probability / len(prize_set)
            remaining = next(card for card in prize_set if card != taken)
            if taken == "A":
                event_a += path_probability
                if remaining == "B":
                    event_a_then_b_remaining += path_probability

    return event_a, event_a_then_b_remaining / event_a


def distribution(belief: PrizeBelief) -> dict[tuple[int, ...], float]:
    return dict(belief.masses)


def main() -> None:
    labeled_a_probability, labeled_b_after_a = labeled_toy_metrics()

    belief = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 1},
        pool_size=5,
        prize_count=2,
    )
    assert_close(belief.probability_mass(), 1.0)
    assert_close(
        observation_probability(belief, "A"),
        labeled_a_probability,
    )
    assert_close(labeled_a_probability, 1.0 / 5.0)

    after_a = take_observed_random_prize(belief, "A")
    assert after_a.prize_count == 1
    assert_close(after_a.probability_mass(), 1.0)
    by_state = distribution(after_a)
    assert_close(by_state[(0, 1)], labeled_b_after_a)
    assert_close(labeled_b_after_a, 1.0 / 4.0)
    assert_close(by_state[(0, 0)], 3.0 / 4.0)
    assert_close(observation_probability(after_a, None), 3.0 / 4.0)

    after_a_then_filler = take_observed_random_prize(after_a, None)
    assert after_a_then_filler.prize_count == 0
    assert after_a_then_filler.is_exact()
    assert distribution(after_a_then_filler) == {(0, 0): 1.0}

    forward_path_probability = (
        observation_probability(belief, "A")
        * observation_probability(after_a, None)
    )
    after_filler = take_observed_random_prize(belief, None)
    reverse_path_probability = (
        observation_probability(belief, None)
        * observation_probability(after_filler, "A")
    )
    assert_close(forward_path_probability, 3.0 / 20.0)
    assert_close(reverse_path_probability, 3.0 / 20.0)

    reverse = take_observed_prizes(belief, (None, "A"))
    forward = take_observed_prizes(belief, ("A", None))
    assert reverse.prize_count == forward.prize_count == 0
    assert distribution(reverse) == distribution(forward) == {(0, 0): 1.0}

    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("A-class", "prize"): 1,
                ("F1-class", "prize"): 1,
                ("B-class", "deck"): 1,
                ("F2-class", "deck"): 1,
                ("F3-class", "deck"): 1,
            }
        )
    )
    first_take = take_prizes_and_update_belief(
        initial,
        belief,
        (("A-class", "A"),),
    )
    assert exchangeable_prize_count(first_take.ledger) == 1
    assert first_take.ledger.exchangeable.count("A-class", "hand") == 1
    assert first_take.ledger.exchangeable.count("F1-class", "prize") == 1
    assert first_take.belief.prize_count == 1
    assert_close(distribution(first_take.belief)[(0, 1)], 1.0 / 4.0)
    assert_conserved(initial, first_take.ledger)

    second_take = take_prizes_and_update_belief(
        first_take.ledger,
        first_take.belief,
        (("F1-class", None),),
    )
    assert exchangeable_prize_count(second_take.ledger) == 0
    assert second_take.ledger.exchangeable.count("A-class", "hand") == 1
    assert second_take.ledger.exchangeable.count("F1-class", "hand") == 1
    assert second_take.belief.prize_count == 0
    assert second_take.belief.is_exact()
    assert distribution(second_take.belief) == {(0, 0): 1.0}
    assert_conserved(initial, second_take.ledger)

    exact = PrizeBelief.from_exact({"A": 1}, prize_count=1)
    try:
        take_observed_random_prize(exact, None)
    except ValueError:
        pass
    else:
        raise AssertionError("zero-probability Prize observation was accepted")

    try:
        take_prizes_and_update_belief(
            initial,
            PrizeBelief.from_exact({"A": 1}, prize_count=1),
            (("A-class", "A"),),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("physical/belief Prize-count mismatch was accepted")

    print("Prize take conservation and belief regressions passed")


if __name__ == "__main__":
    main()
