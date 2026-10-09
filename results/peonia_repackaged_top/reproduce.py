"""Exact K0-like hidden target location and Arc-before-Peonia witness.

A single target T is uniformly located in n face-down Prize positions plus
d unknown deck positions; all other hidden cards are inert filler F.
Initially Peonia, one Arc Phone, one Trekking Shoes, and one spare filler
are held. Success requires T and an unused Shoes simultaneously in hand.
"""
from fractions import Fraction

from tools.peonia_timing_policy import initial, normalize, play_peonia, optimal


def uniform_target(n, d):
    """Uniform physical location of one target among n Prize + d deck slots."""
    if n < 3 or d < 1:
        raise ValueError("At least three Prize and one deck slot required")
    mass = Fraction(1, n + d)
    worlds = {}
    for location in range(n + d):
        prizes = ["F"] * n
        deck = ["F"] * d
        if location < n:
            prizes[location] = "T"
        else:
            deck[location - n] = "T"
        worlds[(tuple(prizes), tuple(deck))] = mass
    return normalize(worlds)


def compare(n, d):
    belief = uniform_target(n, d)
    hand = (0, 1, 1, 1)  # T, Arc, Shoes, filler
    play_peonia.cache_clear()
    optimal.cache_clear()
    first = play_peonia(belief, hand, "S")
    flexible = optimal(belief, hand, True, "S")
    return first, flexible


def run():
    # Stronger pure-retrieval version: no Trekking Shoes is held, so
    # Arc-first can stage a deck-top T for Peonia; Peonia-first cannot.
    for n in (4, 5, 6):
        for d in (1, 2, 3, 4):
            belief = uniform_target(n, d)
            hand = (0, 1, 0, 1)
            play_peonia.cache_clear()
            optimal.cache_clear()
            first = play_peonia(belief, hand)
            flexible = optimal(belief, hand, True)
            assert (first, flexible) == (
                Fraction(3, n + d), Fraction(4, n + d)
            ), (n, d, first, flexible)
    print("T-only no-Shoes endpoint: 12 exact strict Arc-first timing tests passed.")
    for n, d in ((5, 2), (6, 2), (4, 3)):
        belief = uniform_target(n, d)
        hand = (0, 1, 0, 0)  # No spare Peonia replacement card.
        play_peonia.cache_clear()
        optimal.cache_clear()
        assert play_peonia(belief, hand) == Fraction(3, n + d)
        assert optimal(belief, hand, True) == Fraction(3, n + d)
    print("No-spare-card ablation: Arc-first timing gain disappears.")


    # Independent counting: Peonia-first can reach 3 random Prize positions.
    # Arc-first additionally relocates deck top T to a known Prize slot.
    for n in (4, 5, 6):
        for d in (1, 2, 3, 4):
            first, flexible = compare(n, d)
            expected = (Fraction(3, n + d), Fraction(4, n + d))
            assert (first, flexible) == expected, (n, d, first, flexible)
            print(f"Prizes={n} deck={d}: first={first} flexible={flexible} "
                  f"gain={flexible-first}")

    # K1-known deck containment is sufficient for a strict timing gain.
    for d in (1, 2, 3, 4):
        belief = initial(tuple("FFFFF"), tuple("T" + "F" * (d - 1)))
        hand = (0, 1, 1, 1)
        play_peonia.cache_clear()
        optimal.cache_clear()
        assert play_peonia(belief, hand, "S") == 0
        assert optimal(belief, hand, True, "S") == Fraction(1, d)
        print(f"K1 T known in deck of {d}: Arc-first={Fraction(1, d)}")

    assert compare(5, 2) == (Fraction(3, 7), Fraction(4, 7))
    print("12 exact belief-state tests passed; Arc-first relocation adds 1/(n+d).")


if __name__ == "__main__":
    run()
