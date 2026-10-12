"""Independent physical deal oracle for Fog-funded search-Item payments."""
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from results.competitive_deck_baselines import shadow_rider_reproduce as baseline
from tools.shadow_rider_forest_stone_frontier import MODES
from tools.shadow_rider_stone_host_bridge import payable_search_source
from tools.shadow_rider_fog_energy_payment import exact_increment

TOYS = (
    (1, 2, 1, 1, 1, 2, 2, 2),
    (1, 2, 2, 1, 1, 2, 1, 3),
)


def physical_oracle(
    counts: tuple[int, ...], v_count: int = 1,
    fog_count: int = 1,
) -> dict[str, Fraction]:
    cards = []
    for category, number in enumerate(counts):
        for i in range(number):
            marker = (
                "V" if category == 5 and i < v_count
                else "Stone" if category == 7 and i == 0
                else "Fog" if category == 7 and 1 <= i <= fog_count
                else ""
            )
            cards.append((category, marker))
    indices = set(range(len(cards)))
    hits = {mode: 0 for mode in MODES}
    denominator = 0
    for opening_ids in combinations(range(len(cards)), 3):
        opening = [cards[i] for i in opening_ids]
        if not any(c in (0, 5) for c, _ in opening):
            continue
        remaining = indices.difference(opening_ids)
        for prize_ids in combinations(remaining, 2):
            for drawn in remaining.difference(prize_ids):
                denominator += 1
                hand = opening + [cards[drawn]]
                deck = [
                    cards[i] for i in remaining.difference(prize_ids)
                    if i != drawn
                ]
                hand_types = [c for c, _ in hand]
                deck_types = [c for c, _ in deck]
                hand_flags = [flag for _, flag in hand]
                deck_flags = [flag for _, flag in deck]
                if (
                    not any(c == 5 for c, _ in opening)
                    or 0 not in deck_types
                    or deck_types.count(1) < 2
                    or 6 in hand_types or 6 not in deck_types
                    or not (2 in hand_types or 4 in hand_types)
                    or "Fog" not in hand_flags
                ):
                    continue
                if "Stone" in hand_flags and (
                    "V" in hand_flags or "V" in deck_flags
                ):
                    continue
                hand_counts = tuple(
                    hand_types.count(i) for i in range(len(counts))
                )
                for mode in MODES:
                    if not payable_search_source(hand_counts, mode):
                        hits[mode] += 1
    return {
        mode: Fraction(value, denominator)
        for mode, value in hits.items()
    }


def verify() -> None:
    baseline.verify()
    assert baseline.TRAINERS["Fog Crystal"] == 4
    assert baseline.ENERGY["Psychic Energy"] == 11

    root = Path(__file__).resolve().parents[2]
    print_id = baseline.PRINT_IDS["Fog Crystal"]
    set_id = print_id.rsplit("-", 1)[0]
    cards = json.loads(
        (root / "resources" / "cards" / "en"
         / (set_id + ".json")).read_text(encoding="utf-8")
    )
    card = next(c for c in cards if c["id"] == print_id)
    assert any(
        "Search your deck for a Psychic Energy card" in text
        for text in card["rules"]
    )

    for counts in TOYS:
        grouped = exact_increment(
            counts, 3, 2, v_count=1, fog_count=1
        )
        assert grouped == physical_oracle(counts), counts

    increment = exact_increment()
    assert increment["unrestricted"] == 0
    assert increment["energy"] == Fraction(
        92077745330269, 2719429211699200
    )
    assert increment["energy_or_extra_search"] == Fraction(
        13409399294303, 543885842339840
    )
    for mode in MODES:
        print(mode, f"+{100 * float(increment[mode]):.9f} points")
    print("Two independent labeled physical toy oracles passed.")


if __name__ == "__main__":
    verify()
