"""Independent labeled-oracle tests for deck-prefix target exposure and shuffle value."""

from fractions import Fraction
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief
from prize_top_draw_pool import PrizePoolBelief
from prize_deck_prefix import PrizeDeckPrefixBelief
from prize_prefix_draw_exposure import (
    probability_target_exposure,
    uniform_shuffle_value,
)


def close(actual, expected):
    assert abs(actual - float(expected)) <= 1e-12, (actual, expected)


def hit(belief, targets, draws, at_least=1, shuffled=False):
    return probability_target_exposure(
        belief,
        targets=targets,
        draw_count=draws,
        at_least=at_least,
        shuffle_first=shuffled,
    )


def main():
    groups = {"A": 1, "B": 1, "C": 1, "D": 1}
    prior = PrizePositionTopBelief.from_pool(
        groups, pool_size=6, prize_count=2
    )
    filtered = [(w, m) for w, m in prior.masses if w == (("B", None), "A")]
    total = sum(m for _, m in filtered)
    prior = PrizePositionTopBelief(
        prior.groups, prior.face_up,
        tuple((w, m / total) for w, m in filtered)
    )
    pool = PrizePoolBelief.from_joint_prior(prior, groups, pool_size=6)

    # Observe original second C and third D, then exchange A with Prize0 B.
    ordered = (
        PrizeDeckPrefixBelief.from_exchangeable_pool(pool, depth=2)
        .observe_deck_position(1, "C")
        .observe_deck_position(2, "D")
        .swap_top_with_face_down(0)
    )
    close(hit(ordered, ("C",), 2), 1)
    close(hit(ordered, ("D",), 2), 0)
    close(hit(ordered, ("C", "D"), 3, at_least=2), 1)

    # Full uniform shuffle destroys order but preserves deck composition B,C,D,F.
    close(hit(ordered, ("C",), 2, shuffled=True), Fraction(1, 2))
    close(hit(ordered, ("D",), 2, shuffled=True), Fraction(1, 2))
    close(hit(ordered, ("C", "D"), 3, at_least=2, shuffled=True), Fraction(1, 2))
    close(uniform_shuffle_value(
        ordered, targets=("C",), draw_count=2
    ), Fraction(-1, 2))
    close(uniform_shuffle_value(
        ordered, targets=("D",), draw_count=2
    ), Fraction(1, 2))

    # Same inventory without ordered prefix: the top B is known to miss,
    # and C is uniform among three residual positions.
    coarsened = PrizeDeckPrefixBelief.from_exchangeable_pool(
        ordered.to_exchangeable_pool(), depth=0
    )
    close(hit(coarsened, ("C",), 2), Fraction(1, 3))

    # Independent physical oracle: all 4! ordered shuffles of B,C,D,filler.
    shuffled_orders = tuple(permutations(("B", "C", "D", "F")))
    assert len(shuffled_orders) == 24
    oracle_c_2 = Fraction(
        sum("C" in ordered_cards[:2] for ordered_cards in shuffled_orders),
        len(shuffled_orders),
    )
    oracle_d_2 = Fraction(
        sum("D" in ordered_cards[:2] for ordered_cards in shuffled_orders),
        len(shuffled_orders),
    )
    oracle_cd_3 = Fraction(
        sum(
            {"C", "D"} <= set(ordered_cards[:3])
            for ordered_cards in shuffled_orders
        ),
        len(shuffled_orders),
    )
    assert (oracle_c_2, oracle_d_2, oracle_cd_3) == (
        Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)
    )

    # Multi-copy hypergeometric witness. Known top B, two copies of A among
    # four exchangeable deeper cards (A1,A2,F1,F2).
    small_groups = {"A": 2, "B": 1}
    small_prior = PrizePositionTopBelief.from_pool(
        small_groups, pool_size=5, prize_count=0
    ).observe_top("B")
    small_pool = PrizePoolBelief.from_joint_prior(
        small_prior, small_groups, pool_size=5
    )
    small = PrizeDeckPrefixBelief.from_exchangeable_pool(
        small_pool, depth=0
    )
    close(hit(small, ("A",), 3, at_least=2), Fraction(1, 6))
    close(hit(small, ("A",), 3, at_least=2, shuffled=True), Fraction(3, 10))

    labels = ("A1", "A2", "B", "F1", "F2")
    all_ordered = tuple(permutations(labels))
    conditional = [row for row in all_ordered if row[0] == "B"]
    assert len(conditional) == 24
    oracle_no_shuffle = Fraction(
        sum(set(("A1", "A2")) <= set(row[:3]) for row in conditional),
        len(conditional),
    )
    oracle_shuffle = Fraction(
        sum(set(("A1", "A2")) <= set(row[:3]) for row in all_ordered),
        len(all_ordered),
    )
    assert oracle_no_shuffle == Fraction(1, 6)
    assert oracle_shuffle == Fraction(3, 10)

    # Formal boundary checks for invalid draw requirements.
    for kwargs in (
        {"targets": (), "draw_count": 1},
        {"targets": ("unmodeled",), "draw_count": 1},
        {"targets": ("C",), "draw_count": 5},
        {"targets": ("C",), "draw_count": -1},
        {"targets": ("C",), "draw_count": 2, "at_least": -1},
    ):
        try:
            probability_target_exposure(ordered, **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid draw question {kwargs}")

    print("Prefix draw exposure: known-order and 24-permutation oracle passed")
    print("Shuffle value for 2 draws: C=-1/2, D=+1/2")
    print("Multi-copy oracle: P(2 A in 3) 1/6 vs shuffled 3/10")


if __name__ == "__main__":
    main()
