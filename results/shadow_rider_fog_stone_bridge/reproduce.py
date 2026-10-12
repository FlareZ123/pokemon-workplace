"""Physical Fog/Stone/V exact oracle and pinned Aichi 60-card totals."""
import json
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
from tools.shadow_rider_fog_stone_bridge import exact_increment


TOYS = (
    (1, 2, 1, 1, 1, 2, 2, 2),
    (1, 2, 2, 1, 1, 2, 1, 3),
)


def physical_oracle(
    counts: tuple[int, ...], v_count: int = 1,
    fog_count: int = 1,
) -> dict[str, Fraction]:
    cards = []
    for category, amount in enumerate(counts):
        for i in range(amount):
            marker = (
                "V" if category == 5 and i < v_count
                else "Stone" if category == 7 and i == 0
                else "Fog" if category == 7 and 1 <= i <= fog_count
                else ""
            )
            cards.append((category, marker))
    indices = set(range(len(cards)))
    frequencies = {mode: 0 for mode in MODES}
    denominator = 0
    for opening_ids in combinations(range(len(cards)), 3):
        opening = [cards[i] for i in opening_ids]
        if not any(c in (0, 5) for c, _ in opening):
            continue
        remaining = indices.difference(opening_ids)
        for prize_ids in combinations(remaining, 2):
            prizes = [cards[i] for i in prize_ids]
            for draw_id in remaining.difference(prize_ids):
                denominator += 1
                hand = opening + [cards[draw_id]]
                deck = [
                    cards[i] for i in remaining.difference(prize_ids)
                    if i != draw_id
                ]
                if (
                    not any(c == 5 for c, _ in opening)
                    or sum(c == 1 for c, _ in deck) < 2
                    or not (
                        any(c == 0 for c, _ in deck)
                        or (
                            any(c == 0 for c, _ in prizes)
                            and any(c == 3 for c, _ in deck)
                        )
                    )
                    or any(marker == "V" for _, marker in hand)
                    or not any(marker == "V" for _, marker in deck)
                    or not any(marker == "Stone" for _, marker in hand)
                    or not any(marker == "Fog" for _, marker in hand)
                ):
                    continue
                hand_counts = tuple(
                    sum(c == i for c, _ in hand)
                    for i in range(len(counts))
                )
                for mode in MODES:
                    if not payable_search_source(hand_counts, mode):
                        frequencies[mode] += 1
    return {
        mode: Fraction(n, denominator)
        for mode, n in frequencies.items()
    }


def verify() -> None:
    baseline.verify()
    assert baseline.TRAINERS["Fog Crystal"] == 4
    assert baseline.TRAINERS["Forest Seal Stone"] == 1
    assert baseline.POKEMON["Shadow Rider Calyrex V"] == 3
    root = Path(__file__).resolve().parents[2]
    for name, type_name in (
        ("Radiant Eternatus", "Dragon"),
        ("Shadow Rider Calyrex V", "Psychic"),
    ):
        card_id = baseline.PRINT_IDS[name]
        set_id = card_id.rsplit("-", 1)[0]
        records = json.loads(
            (root / "resources" / "cards" / "en"
             / (set_id + ".json")).read_text(encoding="utf-8")
        )
        card = next(c for c in records if c["id"] == card_id)
        assert type_name in card["types"]
    fog_id = baseline.PRINT_IDS["Fog Crystal"]
    set_id = fog_id.rsplit("-", 1)[0]
    cards = json.loads(
        (root / "resources" / "cards" / "en"
         / (set_id + ".json")).read_text(encoding="utf-8")
    )
    fog = next(c for c in cards if c["id"] == fog_id)
    assert any("Basic Psychic Pokémon" in rule for rule in fog["rules"])

    for counts in TOYS:
        actual = exact_increment(
            counts, 3, 2, v_total=1, fog_total=1
        )
        assert actual == physical_oracle(counts), counts

    base = exact_stone()
    paid = exact_extension()
    fog = exact_increment()
    target = {
        "unrestricted": Fraction(
            32815089270847133, 59827442657382400
        ),
        "energy": Fraction(
            85554048050942903, 179482327972147200
        ),
        "energy_or_extra_search": Fraction(
            466013785655437, 934803791521600
        ),
    }
    for mode in MODES:
        total = (
            success(base[mode])
            + sum(paid[mode].values(), Fraction())
            + fog[mode]
        )
        assert total == target[mode], mode
        print(
            mode, f"{100 * float(total):.9f}% total",
            f"+{100 * float(fog[mode]):.9f} points from Fog",
        )
    print("Two independent physical V/Stone/Fog toy oracles passed.")


if __name__ == "__main__":
    verify()
