"""Reproduce variable-depth ordered deck prefix with exact physical oracle."""

from collections import Counter
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief
from prize_top_draw_pool import PrizePoolBelief
from prize_top_two_order import PrizeTopTwoBelief
from prize_deck_prefix import PrizeDeckPrefixBelief


def close(actual, expected):
    assert abs(actual - float(expected)) <= 1e-12, (actual, expected)


def compare_pool(left, right):
    a = dict(left.masses)
    b = dict(right.masses)
    assert set(a) == set(b), (set(a) - set(b), set(b) - set(a))
    for world in a:
        close(a[world], b[world])


def main():
    groups = {"A": 1, "B": 1, "C": 1, "D": 1}
    prior = PrizePositionTopBelief.from_pool(
        groups, pool_size=6, prize_count=2
    )
    filtered = tuple(
        (world, mass) for world, mass in prior.masses
        if world[0] == ("B", None) and world[1] == "A"
    )
    total = sum(mass for _, mass in filtered)
    assert total > 0
    conditioned = PrizePositionTopBelief(
        prior.groups, prior.face_up,
        tuple((world, mass / total) for world, mass in filtered),
    )
    pool = PrizePoolBelief.from_joint_prior(
        conditioned, groups, pool_size=6
    )

    # depth 0 agrees with the prior exchangeable pool draw transition.
    depth_zero = PrizeDeckPrefixBelief.from_exchangeable_pool(pool, depth=0)
    assert depth_zero.depth == 0
    compare_pool(
        depth_zero.swap_top_with_face_down(0)
        .draw_top_and_advance()
        .to_exchangeable_pool(),
        pool.swap_top_with_face_down(0).draw_top_and_refill(),
    )

    # depth 1 agrees with the existing fixed two-card kernel before and
    # after one swap/draw under the same unknown-order distribution.
    depth_one = PrizeDeckPrefixBelief.from_exchangeable_pool(pool, depth=1)
    old_two = PrizeTopTwoBelief.from_exchangeable_pool(pool)
    expected_one = {
        (world.pool, world.second): mass
        for world, mass in old_two.masses
    }
    assert set(expected_one) == {
        (world.pool, world.suffix_prefix[0])
        for world, _ in depth_one.masses
    }
    for world, mass in depth_one.masses:
        close(mass, expected_one[(world.pool, world.suffix_prefix[0])])
    compare_pool(
        depth_one.swap_top_with_face_down(0)
        .draw_top_and_advance().to_exchangeable_pool(),
        old_two.swap_top_with_face_down(0)
        .draw_top_and_shift_window().to_exchangeable_pool(),
    )

    # Deck suffix has exactly one C, one D and one filler, uniformly ordered.
    depth_two = PrizeDeckPrefixBelief.from_exchangeable_pool(pool, depth=2)
    assert depth_two.depth == 2
    close(depth_two.probability_at_deck_position(1, "C"), Fraction(1, 3))
    observed_c = depth_two.observe_deck_position(1, "C")
    close(observed_c.probability_at_deck_position(2, "D"), Fraction(1, 2))
    observed_cd = observed_c.observe_deck_position(2, "D")
    close(observed_cd.probability_at_deck_position(2, "D"), 1)

    # Arc Phone: swap original top A with Prize0 B, draw B, next top C,
    # following deck position D; later draws deterministically shift D/filler.
    swapped = observed_cd.swap_top_with_face_down(0)
    after_b = swapped.draw_top_and_advance()
    assert after_b.depth == 2
    close(after_b.probability_at_deck_position(0, "C"), 1)
    close(after_b.probability_at_deck_position(1, "D"), 1)
    close(after_b.probability_at_deck_position(2, None), 1)

    after_c = after_b.draw_top_and_advance()
    assert after_c.depth == 1
    close(after_c.probability_at_deck_position(0, "D"), 1)
    close(after_c.probability_at_deck_position(1, None), 1)

    after_d = after_c.draw_top_and_advance()
    assert after_d.depth == 0
    close(after_d.probability_at_deck_position(0, None), 1)
    assert len(after_d.masses) == 1
    final_world = after_d.masses[0][0].pool
    assert final_world.prizes == ("A", None)
    assert final_world.drawn == (0, 1, 1, 1, 0)
    assert sum(final_world.remainder) == 0

    # Removing the deep order observation but retaining the exact same group
    # inventory aliases distinct action outcomes. k1 sees D or filler 1/2.
    one_observed_c = depth_one.observe_deck_position(1, "C")
    after_b_only_c = (
        one_observed_c.swap_top_with_face_down(0)
        .draw_top_and_advance()
    )
    close(after_b_only_c.probability_at_deck_position(1, "D"), Fraction(1, 2))

    # k0 forgets even the next card and predicts C after B with 1/3.
    after_b_noknowledge = (
        depth_zero.swap_top_with_face_down(0)
        .draw_top_and_advance()
    )
    close(after_b_noknowledge.probability_at_deck_position(0, "C"), Fraction(1, 3))
    close(
        observed_cd.to_exchangeable_pool()
        .swap_top_with_face_down(0)
        .draw_top_and_refill().probability_top("C"),
        Fraction(1, 3),
    )

    # Independent exact labeled oracle enumerates 6P5=720 initial ordered
    # physical deals P0,P1,top,second,third before any swap/draw.
    deals = tuple(permutations(("A", "B", "C", "D", "F1", "F2"), 5))
    assert len(deals) == 720
    eligible = [
        deal for deal in deals
        if deal[0] == "B" and deal[1] in ("F1", "F2")
        and deal[2] == "A"
    ]
    assert len(eligible) == 12
    saw_c = [deal for deal in eligible if deal[3] == "C"]
    saw_cd = [deal for deal in saw_c if deal[4] == "D"]
    assert len(saw_c) == 4
    assert len(saw_cd) == 2
    assert Fraction(len(saw_c), len(eligible)) == Fraction(1, 3)
    assert Fraction(len(saw_cd), len(saw_c)) == Fraction(1, 2)
    assert all(deal[3:5] == ("C", "D") for deal in saw_cd)

    # Finiteness checks: no unmodeled position and no extra physical card.
    try:
        PrizeDeckPrefixBelief.from_exchangeable_pool(pool, depth=4)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted a prefix longer than remaining deck")
    try:
        observed_cd.observe_deck_position(2, "A")
    except ValueError:
        pass
    else:
        raise AssertionError("accepted zero-probability deep-card observation")
    try:
        after_d.draw_top_and_advance()
    except ValueError:
        pass
    else:
        raise AssertionError("manufactured new top after deck exhausted")

    print("Variable-depth deck prefix passed 720 labeled physical-order oracle")
    print("k=0,1 agree with existing pool and top-two kernels")
    print("A,B top swap/draw: known next C then D then filler; prefix depths 2->1->0")


if __name__ == "__main__":
    main()
