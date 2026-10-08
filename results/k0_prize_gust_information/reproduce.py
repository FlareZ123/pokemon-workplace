"""K0 hidden-Prize gust policy: exact deal census and independent two-stage oracle."""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.gust_prize_minimax import enumerate_boards
from tools.k0_prize_gust_information import (
    expected_opening_deal_attacks as k0_expectation,
    first_action_values,
    minimum_expected_attacks,
)
from tools.prize_refill_gust import (
    _after_draw as k1_after_draw,
    expected_opening_deal_attacks as k1_expectation,
)


def hypergeom_prize_worlds(unseen_boss, deck_size, prize_size):
    """Enumerate exact concealed Prize compositions before a search."""
    total = deck_size + prize_size
    for prized in range(max(0, unseen_boss - deck_size), min(unseen_boss, prize_size) + 1):
        weight = Fraction(
            comb(prize_size, prized) * comb(deck_size, unseen_boss - prized),
            comb(total, unseen_boss)
        )
        yield prized, weight


@lru_cache(None)
def oracle_draw(a, bench, hand, unseen, deck, prize, refill):
    """Independent two-step draw: Prize composition then deck-card identity."""
    result = Fraction()
    for prized, p_prior in hypergeom_prize_worlds(unseen, deck, prize):
        in_deck = unseen - prized
        if in_deck:
            result += p_prior * Fraction(in_deck, deck) * oracle_act(
                a, bench, hand + 1, unseen - 1, deck - 1, prize, refill
            )
        if deck > in_deck:
            result += p_prior * Fraction(deck - in_deck, deck) * oracle_act(
                a, bench, hand, unseen, deck - 1, prize, refill
            )
    return result


@lru_cache(None)
def oracle_act(a, bench, hand, unseen, deck, prize, refill):
    """Separate hidden-Prize composition mixture from Prize-taking draws."""
    choices = [(a, bench, hand)]
    if hand:
        for i, reward in enumerate(bench):
            choices.append(
                (reward, tuple(sorted((a,) + bench[:i] + bench[i + 1:])), hand - 1)
            )
    costs = []
    for reward, rest, left in choices:
        if reward >= prize or not rest:
            costs.append(Fraction(1))
            continue
        possibilities = []
        for prized, p_prior in hypergeom_prize_worlds(unseen, deck, prize):
            for hit in range(
                max(0, reward - (prize - prized)), min(prized, reward) + 1
            ):
                weight = p_prior * Fraction(
                    comb(prized, hit) * comb(prize - prized, reward - hit),
                    comb(prize, reward)
                )
                next_values = tuple(
                    oracle_draw(
                        promoted, rest[:j] + rest[j + 1:],
                        left + (hit if refill else 0),
                        unseen - hit, deck, prize - reward, refill
                    )
                    for j, promoted in enumerate(rest)
                )
                possibilities.append((weight, next_values))
        costs.append(
            Fraction(1) + max(
                sum((weight * vals[j] for weight, vals in possibilities), Fraction())
                for j in range(len(rest))
            )
        )
    return min(costs)


def main():
    boards = tuple(enumerate_boards())
    assert len(boards) == 146

    expected_advantages = {
        2: Fraction(4, 885),
        3: Fraction(128, 8555),
        4: Fraction(5008, 162545),
    }
    witness_shapes = {
        (2, (1, 1, 3, 3)),
        (2, (1, 1, 1, 3, 3)),
        (2, (1, 1, 2, 3, 3)),
        (2, (1, 1, 3, 3, 3)),
    }
    checked = 0
    for refill in (True, False):
        for copies in range(5):
            advantaged = {}
            for a, bench, _ in boards:
                k0 = k0_expectation(copies, a, bench, refill)
                k1 = k1_expectation(copies, a, bench, refill)
                assert k0 >= k1, (copies, a, bench, k0, k1)
                if k0 > k1:
                    advantaged[(a, bench)] = k0 - k1
                checked += 1
            if not refill or copies < 2:
                assert not advantaged
            else:
                assert set(advantaged) == witness_shapes
                assert set(advantaged.values()) == {expected_advantages[copies]}
                print(
                    f"K={copies} with Prize refill: K1 improves "
                    f"{len(advantaged)} of {len(boards)} boards by "
                    f"{expected_advantages[copies]} expected attacks"
                )
    assert checked == 1460

    # A specific local K0 decision differs from the K1 policy:
    # after the natural draw, one Boss is in hand, one remains unseen,
    # and the current opponent Active is worth two Prizes.
    a, bench = 2, (1, 1, 3, 3)
    opaque = first_action_values(a, bench, 1, 1, 46, 6)
    by_action = dict(opaque)
    assert by_action["attack_active"] == 3
    assert by_action["gust_3"] == Fraction(99, 26)
    assert min(v for _, v in opaque) == 3
    assert k1_after_draw(a, bench, 1, 0, 46, 1, 6, True, False) == Fraction(17, 6)
    assert k1_after_draw(a, bench, 1, 1, 45, 0, 6, True, False) == 3

    # Independent two-stage Prize-composition enumeration reproduces the
    # marginalized K0 draw/prize transitions in small hidden-card states.
    tiny_boards = (
        (1, (3, 3)),
        (3, (1, 3)),
        (2, (1, 1, 3, 3)),
    )
    independent_checks = 0
    for a, bench in tiny_boards:
        for hand in range(3):
            for unseen in range(3):
                for refill in (True, False):
                    assert minimum_expected_attacks(
                        a, bench, hand, unseen, 5, 6, refill
                    ) == oracle_draw(a, bench, hand, unseen, 5, 6, refill)
                    independent_checks += 1
    assert independent_checks == 54
    print(
        f"PASS {checked} K0/K1 full-deal comparisons and "
        f"{independent_checks} independent two-stage hidden-zone checks"
    )


if __name__ == "__main__":
    main()
