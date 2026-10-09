"""Standalone exact verification of full-hand deck-return reset geometry."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from catalog_full_hand_replacements import catalog_full_hand_replacements
from hand_destination_reset_geometry import pre_action_delta, singleton_hit_probability


def brute_probability(dest: str, deck: tuple[str, ...], hand: tuple[str, ...],
                      spent: tuple[str, ...], draw: int, target: str) -> Fraction:
    kept = tuple(x for x in hand if x not in spent)
    if target in spent:
        return Fraction(0)
    if dest == "shuffle_into_deck":
        draws = (order[:draw] for order in permutations(deck + kept))
    elif dest == "bottom_deck":
        draws = (d + h for d in permutations(deck) for h in permutations(kept))
        draws = (order[:draw] for order in draws)
    else:
        draws = (order[:draw] for order in permutations(deck))
    successes = count = 0
    for cards in draws:
        count += 1
        if target in cards:
            successes += 1
    return Fraction(successes, count)


def check_geometry() -> None:
    deck = ("T", "D1", "D2")
    for target_deck in (True, False):
        actual_deck = deck if target_deck else ("D1", "D2", "D3")
        hand = ("Q", "C", "H") if target_deck else ("Q", "C", "T")
        for spend in ((), ("Q", "C")):
            for target in ("T", "C"):
                if target == "C" and not spend:
                    initial_zone = "retained_hand"
                elif target == "C":
                    initial_zone = "spent_hand"
                elif target_deck:
                    initial_zone = "deck"
                else:
                    initial_zone = "retained_hand"
                for dest in ("discard", "shuffle_into_deck", "bottom_deck"):
                    for draws in range(7):
                        exact = singleton_hit_probability(
                            deck_size=3, hand_size=3, draw_count=draws,
                            hand_destination=dest, target_zone=initial_zone,
                            spent_hand_cards=len(spend),
                        )
                        brute = brute_probability(dest, actual_deck, hand, spend, draws, target)
                        assert exact == brute, (dest, spend, target, draws, exact, brute)
    assert pre_action_delta(deck_size=46, hand_size=5, draw_count=6,
        hand_destination="shuffle_into_deck", target_initial_zone="hand",
        spent_hand_cards=2, spend_target=True) == -Fraction(2, 17)
    assert pre_action_delta(deck_size=46, hand_size=5, draw_count=6,
        hand_destination="shuffle_into_deck", target_initial_zone="deck",
        spent_hand_cards=2) == Fraction(6,49) - Fraction(6,51)
    assert singleton_hit_probability(deck_size=46, hand_size=5, draw_count=6,
        hand_destination="bottom_deck", target_zone="retained_hand") == 0
    print("Geometry: exhaustive small-state comparisons and three special cases passed")


def check_catalog(resources_root: Path) -> None:
    catalog = catalog_full_hand_replacements(resources_root)
    ids = {card_id for row in catalog for card_id in row.print_ids}
    counts = Counter(row.hand_destination for row in catalog for _ in row.print_ids)
    assert len(catalog) == 65, len(catalog)
    assert len(ids) == 147, len(ids)
    assert counts == {"shuffle_into_deck": 128, "bottom_deck": 19}, counts
    for card_id in ("bw3-92", "sv2-185", "swsh1-169", "swsh10-148",
                    "sv6-165", "swsh11-37", "sv1-151"):
        assert card_id in ids, card_id
    for card_id in ("swsh6-132", "xy12-79", "sm11-206", "sv2-179"):
        assert card_id not in ids, card_id
    print("Card catalog: 147 current-snapshot candidate prints / 65 text variants passed")
    print(f"Destination split: {dict(counts)}")


def main() -> None:
    check_geometry()
    check_catalog(ROOT / "resources")
    print("Example +0.4801920768 percentage points for a deck singleton under shuffle return")
    print("Example -11.7647058824 percentage points if a hand singleton is spent before shuffle return")


if __name__ == "__main__":
    main()
