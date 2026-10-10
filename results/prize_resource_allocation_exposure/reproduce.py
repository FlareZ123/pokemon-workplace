"""Physical permutation oracle for flexible single-use and multi-axis cards."""

from fractions import Fraction
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief
from prize_top_draw_pool import PrizePoolBelief
from prize_deck_prefix import PrizeDeckPrefixBelief
from prize_resource_allocation_exposure import probability_allocatable_draws


def close(actual, expected):
    assert abs(actual - float(expected)) <= 1e-12, (actual, expected)


def chance(belief, profiles, draws, shuffled=False):
    return probability_allocatable_draws(
        belief,
        requirements=(1, 1),  # one Pokémon-access and one Energy-access channel
        profiles_by_group=profiles,
        draw_count=draws,
        shuffle_first=shuffled,
    )


def main():
    # Four physical cards. FLEX provides P or E, but only one per use.
    groups = {"FLEX": 1, "P": 1, "E": 1}
    prior = PrizePositionTopBelief.from_pool(
        groups, pool_size=4, prize_count=0
    )
    pool = PrizePoolBelief.from_joint_prior(
        prior, groups, pool_size=4
    )
    belief = PrizeDeckPrefixBelief.from_exchangeable_pool(pool, depth=0)
    single_axis = {
        "FLEX": ((1, 0), (0, 1)),
        "P": ((1, 0),),
        "E": ((0, 1),),
    }
    multi_axis = {
        "FLEX": ((1, 1),),
        "P": ((1, 0),),
        "E": ((0, 1),),
    }

    close(chance(belief, single_axis, 2), Fraction(1, 2))
    close(chance(belief, multi_axis, 2), Fraction(2, 3))
    close(chance(belief, single_axis, 1), 0)
    close(chance(belief, multi_axis, 1), Fraction(1, 4))
    close(chance(belief, single_axis, 2, shuffled=True), Fraction(1, 2))

    # Independent exact oracle over 4! physical ordered decks.
    decks = tuple(permutations(("FLEX", "P", "E", "F")))
    assert len(decks) == 24

    def possible(first_two, flexible_multi):
        seen = set(first_two)
        if {"P", "E"} <= seen:
            return True
        if "FLEX" in seen:
            return flexible_multi or ("P" in seen or "E" in seen)
        return False

    exact_single = Fraction(
        sum(possible(deck[:2], False) for deck in decks), len(decks)
    )
    exact_multi = Fraction(
        sum(possible(deck[:2], True) for deck in decks), len(decks)
    )
    assert exact_single == Fraction(1, 2)
    assert exact_multi == Fraction(2, 3)
    # Coverage without allocation would accept FLEX + filler, falsely
    # producing the multi-output 2/3 probability for the single-use FLEX.
    assert exact_single != exact_multi

    # Two FLEX copies: meeting both channels requires drawing both when
    # each card has a one-output choice. A true multi-output card needs one.
    double_prior = PrizePositionTopBelief.from_pool(
        {"FLEX": 2}, pool_size=4, prize_count=0
    )
    double_pool = PrizePoolBelief.from_joint_prior(
        double_prior, {"FLEX": 2}, pool_size=4
    )
    double_belief = PrizeDeckPrefixBelief.from_exchangeable_pool(
        double_pool, depth=0
    )
    close(chance(double_belief, {"FLEX": ((1, 0), (0, 1))}, 2), Fraction(1, 6))
    close(chance(double_belief, {"FLEX": ((1, 1),)}, 2), Fraction(5, 6))

    # Deck order conditions feasible allocations as well as direct exposure.
    known_top_flex = PrizeDeckPrefixBelief.from_exchangeable_pool(
        pool.to_exchangeable_pool() if hasattr(pool, "to_exchangeable_pool") else pool,
        depth=0,
    )
    # Existing grouped top observation can construct a correct conditional pool.
    prior_flex = prior.observe_top("FLEX")
    flex_pool = PrizePoolBelief.from_joint_prior(
        prior_flex, groups, pool_size=4
    )
    top_flex = PrizeDeckPrefixBelief.from_exchangeable_pool(
        flex_pool, depth=0
    )
    close(chance(top_flex, single_axis, 1), 0)
    close(chance(top_flex, multi_axis, 1), 1)

    # Invalid dimensions and card groups are rejected.
    for malformed in (
        {"Z": ((1, 0),)},
        {"FLEX": ((1,),)},
        {"FLEX": ((-1, 1),)},
        {"FLEX": ((1.5, 0),)},
    ):
        try:
            chance(belief, malformed, 2)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid role profile {malformed}")

    print("Flexible resource allocation passed independent 24-deck permutation oracle")
    print("FLEX either P or E: 1/2 success; FLEX simultaneously P and E: 2/3")
    print("Two one-use FLEX among two draws: 1/6; multi-output FLEX: 5/6")


if __name__ == "__main__":
    main()
