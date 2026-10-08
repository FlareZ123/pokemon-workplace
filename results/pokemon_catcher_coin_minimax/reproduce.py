"""Independent nested chance/decision enumeration for printed gust coinflips."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.gust_prize_minimax import minimum_attacks
from tools.pokemon_catcher_coin_minimax import census, expected_attacks


@lru_cache(None)
def enumerate_expected_turns(a, b, c, needed):
    """Independent generic action evaluator (attack, flip, promotion, repeat)."""
    if needed <= 0:
        return Fraction(0)
    if not b:
        return Fraction(1)

    # An attack action ends the turn. Opponent's promotion is a MAX node.
    def evaluate_attack(target, survivors, next_c):
        reward = Fraction(1)
        if target >= needed or not survivors:
            return reward
        possible_next = [
            enumerate_expected_turns(
                chosen, survivors[:j] + survivors[j + 1:],
                next_c, needed - target
            )
            for j, chosen in enumerate(survivors)
        ]
        return reward + max(possible_next)

    legal_actions = [evaluate_attack(a, b, c)]
    if c:
        # Coin tails returns control to the attacker BEFORE the attack.
        tail = enumerate_expected_turns(a, b, c - 1, needed)
        heads = [
            evaluate_attack(
                target,
                tuple(sorted([a] + [q for j, q in enumerate(b) if i != j])),
                c - 1
            )
            for i, target in enumerate(b)
        ]
        legal_actions.append((tail + min(heads)) * Fraction(1, 2))
    return min(legal_actions)


def main():
    rows = census()
    assert len(rows) == 146
    counts = Counter()
    one_saves = Counter()
    two_saves = Counter()

    for a, b, no, one, two, boss_one, boss_two in rows:
        for copies, value in enumerate((no, one, two)):
            assert value == enumerate_expected_turns(a, b, copies, 6)
            assert isinstance(value, Fraction)
            counts[copies] += 1

        assert no == minimum_attacks(a, b, 0)
        assert boss_two <= two <= no
        assert no >= one >= two
        assert one == (no + boss_one) / 2  # exhaustively witnessed for all boards
        one_saves[no - one] += 1
        two_saves[no - two] += 1

    assert counts == {0:146, 1:146, 2:146}
    assert one_saves == {
        Fraction(0):77, Fraction(1, 2):54, Fraction(1):15
    }
    assert two_saves == {
        Fraction(0):38,
        Fraction(1,4):31,
        Fraction(1,2):8,
        Fraction(3,4):42,
        Fraction(1):10,
        Fraction(5,4):2,
        Fraction(3,2):15,
    }
    better, equal, worse = (
        sum(compare(two, boss_one) == sign for _, _, _, _, two, boss_one, _ in rows)
        for sign in (-1, 0, 1)
    )
    assert (better, equal, worse) == (41, 48, 57)

    assert tuple(expected_attacks(1, (1,3,3), c) for c in range(3)) == (
        Fraction(4), Fraction(4), Fraction(7,2)
    )
    assert tuple(expected_attacks(3, (1,3), c) for c in range(3)) == (
        Fraction(3), Fraction(5,2), Fraction(9,4)
    )
    print("PASS 438 independent expectation comparisons")
    print("One Catcher expected savings:", dict(sorted(one_saves.items())))
    print("Two Catcher expected savings:", dict(sorted(two_saves.items())))
    print("Two stochastic Catchers vs one deterministic Boss:",
          (better, equal, worse), "boards (better,equal,worse)")


def compare(a, b):
    return (a > b) - (a < b)


if __name__ == "__main__":
    main()
