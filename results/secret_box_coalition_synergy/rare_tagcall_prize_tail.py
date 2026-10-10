"""Exact all-four-Tag-Call Prize-collapse rate with accepted opening hand.

The paper Aichi deck has 14 Basic Pokémon, 4 non-Basic Tag Call, and 60
total cards. The starting hand is seven cards conditioned on >=1 Basic;
six Prize cards are then drawn from the same uniformly shuffled order.
"""

from fractions import Fraction
from math import comb
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from aichi_vileplume_als import BASICS, DECK_COUNTS, DECK
from aichi_vileplume_secret_box import SECRET_BOX_DECK


def accepted_opening_prize_collapse_probability() -> Fraction:
    """Probability all four Tag Call are Prized, conditional on valid opener."""
    cards = sum(DECK_COUNTS.values())
    basics = sum(DECK_COUNTS.get(name, 0) for name in BASICS)
    tag_calls = DECK_COUNTS["Tag Call"]
    hand_count = 7
    prize_count = 6

    assert cards == 60 and basics == 14 and tag_calls == 4
    all_prized = Fraction(
        comb(cards - tag_calls, prize_count - tag_calls),
        comb(cards, prize_count),
    )
    starting_valid = 1 - Fraction(
        comb(cards - basics, hand_count), comb(cards, hand_count)
    )
    valid_given_prized = 1 - Fraction(
        comb(cards - tag_calls - basics, hand_count),
        comb(cards - tag_calls, hand_count),
    )
    return all_prized * valid_given_prized / starting_valid


def sample_accepted_prize_collapse(trials: int = 500_000) -> tuple[int, int, int]:
    """Replay exact accepted opener seed, tracking rare Prize placement."""
    rng = random.Random(20261007)
    all_prized = 0
    box_in_hand = 0
    box_visible_in_stellar = 0

    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            if any(DECK[i] in BASICS for i in order[:7]):
                break
        if sum(DECK[i] == "Tag Call" for i in order[7:13]) != 4:
            continue
        all_prized += 1
        hand = [SECRET_BOX_DECK[i] for i in order[:7]]
        hand.append(SECRET_BOX_DECK[order[13]])
        box_direct = "Secret Box" in hand
        box_in_hand += int(box_direct)
        # Replicate _raw_state's preferred Active selection: Jirachi if present.
        stellar = (
            not box_direct and "Jirachi" in hand[:-1]
            and "Secret Box" in [
                SECRET_BOX_DECK[i] for i in order[14:19]
            ]
        )
        box_visible_in_stellar += int(stellar)
    return all_prized, box_in_hand, box_visible_in_stellar


def main() -> None:
    exact = accepted_opening_prize_collapse_probability()
    assert exact == Fraction(5_975, 187_007_744)
    expected = exact * 500_000
    sampled = sample_accepted_prize_collapse()
    print("Exact P(all four Tag Call Prized | accepted starter) =", exact)
    print("Expected in 500,000 accepted openings =", float(expected))
    print("Actual seeded 500k count, Box direct, Box via Stellar =", sampled)
    print("First 100k zero-event probability if unconditional collapse:", 
          float((1 - exact) ** 100_000))
    assert 0 <= sampled[1] + sampled[2] <= sampled[0]
    print("Exact rare-Prize incidence model and sampler passed.")


if __name__ == "__main__":
    main()
