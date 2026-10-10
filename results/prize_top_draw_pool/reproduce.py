"""Independent 120-deal oracle for correlated Prize/top draws."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief
from prize_top_draw_pool import PrizePoolBelief, PrizePoolWorld


def close(actual, expected):
    assert abs(actual - float(expected)) <= 1e-12, (actual, expected)


def main():
    groups = {"A": 1, "B": 1, "C": 1}
    prior = PrizePositionTopBelief.from_pool(
        groups, pool_size=5, prize_count=2
    )
    pool = PrizePoolBelief.from_joint_prior(
        prior, groups, pool_size=5
    )

    # Arc Phone: actor observes initial top A, swaps it into Prize0,
    # then draws the outgoing former Prize0 and sees that it was B.
    actor_before_draw = (
        pool.observe_top("A")
        .swap_top_with_face_down(0)
        .observe_top("B")
    )
    close(actor_before_draw.probability_prize_at(0, "A"), 1)
    close(actor_before_draw.probability_prize_at(1, "C"), Fraction(1, 3))

    actor_after_draw = actor_before_draw.draw_top_and_refill()
    close(actor_after_draw.probability_top("C"), Fraction(1, 3))
    close(actor_after_draw.probability_prize_at(1, "C"), Fraction(1, 3))
    close(actor_after_draw.probability_both(
        top="C", prize_position=1, prize_group="C"
    ), 0)

    # Independently enumerate all 5P4 = 120 physical *ordered* deals:
    # Prize0, Prize1, original top, and the next top already in the deck.
    cards = ("A", "B", "C", "F1", "F2")
    all_deals = tuple(permutations(cards, 4))
    assert len(all_deals) == 120
    matches = tuple(
        deal for deal in all_deals
        if deal[2] == "A" and deal[0] == "B"
    )
    assert len(matches) == 6

    def group(card):
        return card if card in groups else None

    oracle = defaultdict(Fraction)
    for old_p0, old_p1, old_top, next_top in matches:
        assert old_p0 == "B" and old_top == "A"
        prize_groups = ("A", group(old_p1))
        new_top = group(next_top)
        consumed = Counter(("A", group(old_p1), new_top))
        remaining = tuple(
            initial - consumed[key]
            for key, initial in (("A", 1), ("B", 1), ("C", 1), (None, 2))
        )
        # The drawn B moved to a tracked hand zone.
        hand_counts = (0, 1, 0, 0)
        expected_world = PrizePoolWorld(
            prize_groups, new_top, remaining, hand_counts
        )
        oracle[expected_world] += Fraction(1, len(matches))

    actual = dict(actor_after_draw.masses)
    assert set(oracle) == set(actual)
    for world, mass in actual.items():
        close(mass, oracle[world])
        assert world.drawn == (0, 1, 0, 0)
        assert sum(world.remainder) == 1

    # Independent marginals are invalid: assigning P(C both in Prize1
    # and next top) = (1/3)*(1/3) invents the physically impossible 1/9.
    assert Fraction(1, 3) * Fraction(1, 3) == Fraction(1, 9)
    close(actor_after_draw.probability_both(
        top="C", prize_position=1, prize_group="C"
    ), 0)

    # If the outgoing drawn card identity B is not known to an observer,
    # its unconditioned next-top probability for C is only 1/4.
    uninformed = (
        pool.observe_top("A")
        .swap_top_with_face_down(0)
        .draw_top_and_refill()
    )
    close(uninformed.probability_top("C"), Fraction(1, 4))
    close(uninformed.probability_prize_at(1, "C"), Fraction(1, 4))

    # The previously defined Prize/top joint kernel is an information-losing
    # projection of the conserved deck/hand inventory.
    projected = actor_after_draw.collapse_joint_top_prizes()
    close(
        sum(mass for (prizes, top), mass in projected.masses if top == "C"),
        Fraction(1, 3),
    )

    # Reject impossible pool counts and a draw with no replacement top.
    try:
        PrizePoolBelief.from_joint_prior(
            prior, {"A": 1, "B": 1, "C": 0}, pool_size=5
        )
    except ValueError:
        pass
    else:
        raise AssertionError("accepted physical world exceeding group pool copies")

    three = PrizePositionTopBelief.from_pool(
        {"A": 1, "B": 1, "C": 1}, pool_size=3, prize_count=2
    )
    try:
        PrizePoolBelief.from_joint_prior(
            three, {"A": 1, "B": 1, "C": 1}, pool_size=3
        ).draw_top_and_refill()
    except ValueError:
        pass
    else:
        raise AssertionError("drew beyond the last card without replacement")

    print("Conserved Prize/top draw passed independent 120-deal ordered-card oracle")
    print("P(C next|observed outgoing B)=1/3; without outgoing observation=1/4")
    print("P(C next and C still Prized)=0; independent marginals invent 1/9")


if __name__ == "__main__":
    main()
