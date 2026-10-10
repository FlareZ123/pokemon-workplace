from itertools import permutations
from fractions import Fraction
from math import factorial


def outcomes(hand: tuple[str, ...], deck: tuple[str, ...], *, top: bool) -> set[tuple]:
    result = set()
    for returned in (c for c in hand if c.startswith("P")):
        pool = ((returned,) + deck) if top else (deck + (returned,))
        hand_left = tuple(c for c in hand if c != returned)
        for selected in (None,) + tuple(c for c in pool if c.startswith("P")):
            hand_new = hand_left + ((selected,) if selected else ())
            remainder = tuple(c for c in pool if c != selected)
            reveal = (returned,) + ((selected,) if selected else ())
            prob = Fraction(1, factorial(len(remainder)))
            result.update(
                (returned, selected, hand_new, order, reveal, prob)
                for order in permutations(remainder)
            )
    return result


def verify() -> tuple[int, int]:
    worlds = 0
    paths = 0
    for hp in range(3):
        for hf in range(2):
            hand = tuple(f"P-H{i}" for i in range(hp)) + tuple(f"F-H{i}" for i in range(hf))
            for dp in range(3):
                for df in range(3):
                    deck = tuple(f"P-D{i}" for i in range(dp)) + tuple(f"F-D{i}" for i in range(df))
                    old = outcomes(hand, deck, top=True)
                    modern = outcomes(hand, deck, top=False)
                    assert old == modern, (hand, deck)
                    worlds += 1
                    paths += len(old)
    return worlds, paths
