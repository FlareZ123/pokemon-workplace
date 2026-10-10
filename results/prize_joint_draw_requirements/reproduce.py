"""Independent 120-permutation oracle for joint draw requirements."""

from fractions import Fraction
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief
from prize_top_draw_pool import PrizePoolBelief
from prize_deck_prefix import PrizeDeckPrefixBelief
from prize_prefix_draw_exposure import probability_target_exposure
from prize_joint_draw_requirements import probability_joint_draw_requirements


def close(actual, expected):
    assert abs(actual - float(expected)) <= 1e-12, (actual, expected)


def chance(belief, requirements, draw_count, shuffle_first=False):
    return probability_joint_draw_requirements(
        belief,
        requirements=requirements,
        draw_count=draw_count,
        shuffle_first=shuffle_first,
    )


def main():
    groups = {"P": 2, "E": 1, "X": 1}
    prior = PrizePositionTopBelief.from_pool(
        groups, pool_size=5, prize_count=0
    ).observe_top("X")
    pool = PrizePoolBelief.from_joint_prior(
        prior, groups, pool_size=5
    )
    unord = PrizeDeckPrefixBelief.from_exchangeable_pool(pool, depth=0)

    # Fixed top X, two further random draws from P1,P2,E,F.
    close(chance(unord, {"P": 1, "E": 1}, 3), Fraction(1, 3))
    close(chance(unord, {"P": 1, "E": 1}, 3, True), Fraction(1, 2))
    close(chance(unord, {"P": 2, "E": 1}, 4), Fraction(1, 4))
    close(chance(unord, {"P": 2, "E": 1}, 4, True), Fraction(2, 5))

    # Naive multiplication of the two correct single-target marginals
    # invents 5/12 in place of the exact joint 1/3.
    p_marginal = probability_target_exposure(
        unord, targets=("P",), draw_count=3
    )
    e_marginal = probability_target_exposure(
        unord, targets=("E",), draw_count=3
    )
    close(p_marginal, Fraction(5, 6))
    close(e_marginal, Fraction(1, 2))
    close(p_marginal * e_marginal, Fraction(5, 12))

    # Extra near-term order information changes the joint probability.
    knows_e_second = (
        PrizeDeckPrefixBelief.from_exchangeable_pool(pool, depth=1)
        .observe_deck_position(1, "E")
    )
    close(chance(knows_e_second, {"P": 1, "E": 1}, 3), Fraction(2, 3))
    knows_ep = (
        PrizeDeckPrefixBelief.from_exchangeable_pool(pool, depth=2)
        .observe_deck_position(1, "E")
        .observe_deck_position(2, "P")
    )
    close(chance(knows_ep, {"P": 1, "E": 1}, 3), 1)

    # One category should agree with the preexisting univariate kernel.
    for required in (1, 2):
        close(
            chance(unord, {"P": required}, 3),
            probability_target_exposure(
                unord, targets=("P",), draw_count=3,
                at_least=required,
            ),
        )

    # Independent physical labeled permutation oracle: 5! ordered decks,
    # with top X condition selecting exactly 4!=24 possible orders.
    cards = ("X", "P1", "P2", "E", "F")
    all_decks = tuple(permutations(cards))
    fixed_top = tuple(row for row in all_decks if row[0] == "X")
    assert len(all_decks) == 120 and len(fixed_top) == 24

    def satisfies(row, draws, p_min=1, e_min=1):
        drawn = row[:draws]
        p_count = sum(card in ("P1", "P2") for card in drawn)
        return p_count >= p_min and ("E" in drawn if e_min else True)

    oracle_unshuffled = Fraction(
        sum(satisfies(row, 3) for row in fixed_top), len(fixed_top)
    )
    oracle_shuffled = Fraction(
        sum(satisfies(row, 3) for row in all_decks), len(all_decks)
    )
    oracle_both_p = Fraction(
        sum(satisfies(row, 4, p_min=2) for row in fixed_top),
        len(fixed_top),
    )
    oracle_both_p_shuffled = Fraction(
        sum(satisfies(row, 4, p_min=2) for row in all_decks),
        len(all_decks),
    )
    assert (oracle_unshuffled, oracle_shuffled) == (
        Fraction(1, 3), Fraction(1, 2)
    )
    assert (oracle_both_p, oracle_both_p_shuffled) == (
        Fraction(1, 4), Fraction(2, 5)
    )

    # Validate event domains and zero-requirement identity.
    close(chance(unord, {}, 3), 1)
    close(chance(unord, {"P": 0}, 0), 1)
    close(chance(unord, {"P": 1}, 0), 0)
    for bad in (
        {"Z": 1},
        {"P": -1},
        {"P": 1.5},
    ):
        try:
            chance(unord, bad, 2)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid requirement {bad}")

    print("Joint draw requirements passed exact 120 physical-order oracle")
    print("P(P>=1 & E>=1 within 3): top X -> 1/3, full shuffle -> 1/2")
    print("Naive independent marginals give 5/12, and known second E gives 2/3")


if __name__ == "__main__":
    main()
