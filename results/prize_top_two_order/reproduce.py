"""Second-position memory defeats exchangeable-suffix top-draw predictions."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief
from prize_top_draw_pool import PrizePoolBelief
from prize_top_two_order import PrizeTopTwoBelief


def close(actual, expected):
    assert abs(actual - float(expected)) <= 1e-12, (actual, expected)


def main():
    groups = {"A": 1, "B": 1, "C": 1}
    prior = PrizePositionTopBelief.from_pool(
        groups, pool_size=5, prize_count=2
    )

    # Fix original top A, Prize0 B, untouched Prize1 a filler.
    # Thus the deck suffix has exactly C and another filler, but its order
    # remains unknown until a source-authorized look at the second card.
    conditioned = [
        (world, mass) for world, mass in prior.masses
        if world[1] == "A" and world[0][0] == "B"
        and world[0][1] is None
    ]
    total = sum(mass for _, mass in conditioned)
    restricted = PrizePositionTopBelief(
        prior.groups, prior.face_up,
        tuple((world, mass / total) for world, mass in conditioned),
    )
    pool = PrizePoolBelief.from_joint_prior(
        restricted, groups, pool_size=5
    )
    second_unknown = PrizeTopTwoBelief.from_exchangeable_pool(pool)
    close(second_unknown.probability_second("C"), Fraction(1, 2))

    # Arc Phone swaps A into Prize0, B becomes the current deck top.
    # If player now draws B while the second card is still hidden, next C=1/2.
    coarse = pool.swap_top_with_face_down(0).draw_top_and_refill()
    close(coarse.probability_top("C"), Fraction(1, 2))

    # Privately observing that the original second card is C leaves the
    # *same physical card inventory* but fixes the next draw with certainty.
    learned = second_unknown.observe_second("C")
    known_postdraw = (
        learned.swap_top_with_face_down(0)
        .draw_top_and_shift_window()
    )
    close(known_postdraw.probability_top("C"), 1)
    close(known_postdraw.probability_second(None), 1)
    close(known_postdraw.to_exchangeable_pool().probability_top("C"), 1)
    for world, mass in known_postdraw.masses:
        assert world.pool.prizes == ("A", None)
        assert world.pool.top == "C"
        assert world.pool.drawn == (0, 1, 0, 0)
        assert sum(world.pool.remainder) == 1

    # Forgetting *which* of two remaining deck cards is next and then using
    # an exchangeable-draw kernel incorrectly predicts only P(C next)=1/2.
    coarsened_after_learning = (
        learned.to_exchangeable_pool()
        .swap_top_with_face_down(0)
        .draw_top_and_refill()
    )
    close(coarsened_after_learning.probability_top("C"), Fraction(1, 2))

    # Knowing that the second is filler instead forces C into third place.
    saw_filler = second_unknown.observe_second(None)
    after_filler = (
        saw_filler.swap_top_with_face_down(0)
        .draw_top_and_shift_window()
    )
    close(after_filler.probability_top("C"), 0)
    close(after_filler.probability_second("C"), 1)

    # Independent exact physical-order oracle over all 5P4=120 ordered
    # assignments P0,P1,original top,original second from five unique cards.
    orders = tuple(permutations(("A", "B", "C", "F1", "F2"), 4))
    assert len(orders) == 120
    eligible = [
        order for order in orders
        if order[0] == "B" and order[1] in ("F1", "F2")
        and order[2] == "A"
    ]
    assert len(eligible) == 4
    matches_second_c = [order for order in eligible if order[3] == "C"]
    assert len(matches_second_c) == 2
    assert Fraction(len(matches_second_c), len(eligible)) == Fraction(1, 2)
    # Every physical history with a privately observed second C draws C next.
    assert all(order[3] == "C" for order in matches_second_c)
    assert Counter(order[3] for order in eligible) == Counter({"C": 2, "F1": 1, "F2": 1})

    # Neither the known-order model nor the coarse model may create cards.
    for world, mass in known_postdraw.masses:
        assert len(world.pool.prizes) == 2
        assert world.pool.top == "C"
        assert sum(world.pool.remainder) == 1
        assert sum(world.pool.drawn) == 1

    try:
        second_unknown.observe_second("A")
    except ValueError:
        pass
    else:
        raise AssertionError("accepted impossible second-card observation")

    print("Top-two deck-order model passed independent 120 ordered physical deals")
    print("Same residual C + filler: known C second -> P(next=C)=1; unknown -> 1/2")
    print("Known filler second -> P(next=C)=0; order-free model aliases both")


if __name__ == "__main__":
    main()
