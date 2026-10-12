"""Independent labeled physical-card test and pinned real-60 bridge totals."""
import json
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from results.competitive_deck_baselines import shadow_rider_reproduce as baseline
from tools.shadow_rider_forest_stone_frontier import (
    MODES, exact_stone, success,
)
from tools.shadow_rider_stone_host_bridge import (
    exact_extension, payable_search_source,
)

TOYS = (
    (1, 2, 1, 1, 1, 2, 2, 2),
    (1, 2, 2, 1, 1, 2, 1, 3),
)


def physical_oracle(
    counts: tuple[int, ...], v_copies: int = 1,
) -> dict[str, dict[str, Fraction]]:
    cards = []
    for category, copies in enumerate(counts):
        for i in range(copies):
            marker = (
                "V" if category == 5 and i < v_copies
                else "Stone" if category == 7 and i == 0
                else ""
            )
            cards.append((category, marker))
    indices = set(range(len(cards)))
    counts_by_policy = {mode: defaultdict(int) for mode in MODES}
    denominator = 0
    for opener in combinations(range(len(cards)), 3):
        opening = [cards[i] for i in opener]
        if not any(c in (0, 5) for c, _ in opening):
            continue
        remaining = indices.difference(opener)
        for prize in combinations(remaining, 2):
            prize_cards = [cards[i] for i in prize]
            for draw in remaining.difference(prize):
                denominator += 1
                hand = opening + [cards[draw]]
                deck = [
                    cards[i] for i in remaining.difference(prize)
                    if i != draw
                ]
                if (
                    not any(c == 5 for c, _ in opening)
                    or 0 not in [c for c, _ in prize_cards]
                    or 3 not in [c for c, _ in deck]
                    or sum(c == 1 for c, _ in deck) < 2
                    or any(flag == "V" for _, flag in hand)
                    or not any(flag == "V" for _, flag in deck)
                    or not any(flag == "Stone" for _, flag in hand)
                ):
                    continue
                hand_counts = tuple(
                    sum(c == category for c, _ in hand)
                    for category in range(len(counts))
                )
                for mode, tally in counts_by_policy.items():
                    source = payable_search_source(hand_counts, mode)
                    if source:
                        tally[source] += 1
    return {
        mode: {
            key: Fraction(value, denominator)
            for key, value in tally.items()
        }
        for mode, tally in counts_by_policy.items()
    }


def verify() -> None:
    baseline.verify()
    root = Path(__file__).resolve().parents[2]
    ids = baseline.PRINT_IDS
    for name, fragment in (
        ("Mysterious Treasure", "Psychic or Dragon Pokémon"),
        ("Quick Ball", "Basic Pokémon"),
        ("Forest Seal Stone", "The Pokémon V this card is attached to"),
    ):
        card_id = ids[name]
        set_id = card_id.rsplit("-", 1)[0]
        records = json.loads(
            (root / "resources" / "cards" / "en"
             / (set_id + ".json")).read_text(encoding="utf-8")
        )
        card = next(record for record in records if record["id"] == card_id)
        assert any(fragment in text for text in card["rules"])
    for counts in TOYS:
        actual = exact_extension(counts, 3, 2, v_copies=1)
        expected = physical_oracle(counts)
        for mode in MODES:
            assert dict(actual[mode]) == expected[mode], (counts, mode)

    extension = exact_extension()
    original = exact_stone()
    totals = {
        "unrestricted": Fraction(638960917760013, 1196548853147648),
        "energy": Fraction(82320421005554629, 179482327972147200),
        "energy_or_extra_search": Fraction(
            2879628170698861, 5982744265738240
        ),
    }
    for mode in MODES:
        additional = sum(extension[mode].values(), Fraction())
        assert success(original[mode]) + additional == totals[mode]
        print(
            mode,
            f"{100 * float(totals[mode]):.9f}% total",
            f"+{100 * float(additional):.9f} points",
        )
    print("Two independent labeled physical-card oracles passed.")


if __name__ == "__main__":
    verify()
