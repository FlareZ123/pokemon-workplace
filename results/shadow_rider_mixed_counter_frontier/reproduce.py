"""Exact first-turn Iron Thorns counter diversity in Aichi Shadow Rider.

Execute: python -m results.shadow_rider_mixed_counter_frontier.reproduce
Endpoints are restricted access probabilities, not win rates.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from fractions import Fraction
from itertools import combinations
from math import comb, prod
from pathlib import Path

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    ENERGY, POKEMON, PRINT_IDS, TRAINERS,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry

FLUTTER = "sv5-78"
COLOGNE = "swsh10-136"
THORNS = "sv6-77"
RADIANT = "swsh12pt5-105"
STONE = "swsh12-156"

# Radiant, VMAX, Treasure, Cologne, Flutter, Stone, Shadow V,
# other non-Radiant Basics, other 60-card entries.
def caps(cologne: int, flutter: int) -> tuple[int, ...]:
    assert cologne >= 0 and flutter >= 0 and cologne + flutter <= 2
    assert sum(POKEMON.values()) == 18
    assert sum(TRAINERS.values()) == 31
    assert sum(ENERGY.values()) == 11
    assert POKEMON["Radiant Eternatus"] == 1
    assert POKEMON["Shadow Rider Calyrex VMAX"] == 4
    assert POKEMON["Shadow Rider Calyrex V"] == 3
    assert TRAINERS["Mysterious Treasure"] == 4
    assert TRAINERS["Forest Seal Stone"] == 1
    return (1, 4, 4, cologne, flutter, 1, 3, 10, 37 - cologne - flutter)


def deck_variant(cologne: int, flutter: int) -> dict[str, int]:
    entries = {**POKEMON, **TRAINERS, **ENERGY}
    entries["Sky Field"] -= cologne + flutter
    if cologne:
        entries["Canceling Cologne"] = cologne
    if flutter:
        entries["Flutter Mane"] = flutter
    entries = {name: count for name, count in entries.items() if count > 0}
    assert sum(entries.values()) == 60
    return entries


def allocations(size: int, counts: tuple[int, ...]):
    if len(counts) == 1:
        if 0 <= size <= counts[0]:
            yield (size,)
        return
    for count in range(min(size, counts[0]) + 1):
        for suffix in allocations(size - count, counts[1:]):
            yield (count,) + suffix


def classify(opening: tuple[int, ...], prizes: tuple[int, ...],
             drawn: int, counts: tuple[int, ...]) -> str:
    if opening[0] + opening[4] + opening[6] + opening[7] == 0:
        return "mulligan"
    hand = tuple(opening[i] + int(drawn == i) for i in range(9))
    deck = tuple(counts[i] - opening[i] - prizes[i] - int(drawn == i)
                 for i in range(9))
    if deck[1] < 2:
        return "vmax_not_in_deck"
    direct = bool(hand[0])
    treasure = bool(hand[2] and deck[0])
    tool_ready = bool(hand[5] and hand[6])
    # If Flutter is present in the opening seven, select it as Active.
    # Its non-Rule-Box Ability suppresses opposing Active Initialization.
    if opening[4]:
        if direct:
            return "flutter_direct"
        if treasure:
            return "flutter_treasure"
        if tool_ready and deck[0]:
            return "flutter_stone_radiant"
        return "flutter_missing_radiant"
    # Without Flutter initially, choose another non-Radiant opening Basic.
    if opening[6] + opening[7] == 0:
        return "no_non_radiant_active"
    if hand[3]:
        if direct:
            return "held_cologne_direct"
        if treasure:
            return "held_cologne_treasure"
        if tool_ready and deck[0]:
            return "held_cologne_stone_radiant"
    elif tool_ready and deck[3]:
        if direct:
            return "stone_cologne_direct"
        if treasure:
            return "stone_cologne_treasure"
    return "missing_counter_or_radiant"


def exact(counts: tuple[int, ...], opening_size: int = 7,
          prize_size: int = 6) -> dict[str, Fraction]:
    n = sum(counts)
    basic = counts[0] + counts[4] + counts[6] + counts[7]
    legal_openings = comb(n, opening_size) - comb(n - basic, opening_size)
    ways = legal_openings * comb(n - opening_size, prize_size) * (
        n - opening_size - prize_size
    )
    bucket: Counter[str] = Counter()
    witnessed = 0
    for opening in allocations(opening_size, counts):
        if opening[0] + opening[4] + opening[6] + opening[7] == 0:
            continue
        w1 = prod(comb(nc, oc) for nc, oc in zip(counts, opening))
        after_opening = tuple(nc - oc for nc, oc in zip(counts, opening))
        for prizes in allocations(prize_size, after_opening):
            w2 = w1 * prod(comb(nc, pc)
                           for nc, pc in zip(after_opening, prizes))
            after_prizes = tuple(nc - pc for nc, pc in zip(after_opening, prizes))
            for drawn, count in enumerate(after_prizes):
                if not count:
                    continue
                weight = w2 * count
                bucket[classify(opening, prizes, drawn, counts)] += weight
                witnessed += weight
    assert witnessed == ways
    return {name: Fraction(count, ways) for name, count in bucket.items()}


def successful(result: dict[str, Fraction]) -> Fraction:
    return sum((value for name, value in result.items()
                if name.startswith(("flutter_", "held_cologne_", "stone_cologne_"))
                and name != "flutter_missing_radiant"), Fraction(0))


def physical_toy_oracle() -> None:
    """Independent enumeration of distinct labeled physical cards."""
    counts = (1, 2, 1, 1, 1, 1, 1, 1, 2)
    cards = tuple(i for i, n in enumerate(counts) for _ in range(n))
    outcomes: Counter[str] = Counter()
    total = 0
    for opening_cards in combinations(range(len(cards)), 3):
        opening = tuple(sum(cards[i] == k for i in opening_cards)
                        for k in range(9))
        if opening[0] + opening[4] + opening[6] + opening[7] == 0:
            continue
        remaining = set(range(len(cards))) - set(opening_cards)
        for prize_cards in combinations(sorted(remaining), 2):
            prizes = tuple(sum(cards[i] == k for i in prize_cards)
                           for k in range(9))
            for draw_card in sorted(remaining - set(prize_cards)):
                label = classify(opening, prizes, cards[draw_card], counts)
                outcomes[label] += 1
                total += 1
    assert total == 21840
    projected = exact(counts, opening_size=3, prize_size=2)
    assert set(projected) == set(outcomes)
    for label, prob in projected.items():
        assert prob == Fraction(outcomes[label], total), label
    print("Nine-category independent 21,840 physical-world oracle PASS")


def read_card(cid: str) -> dict:
    root = Path(__file__).resolve().parents[2]
    source = root / "resources" / "cards" / "en" / f"{cid.rsplit('-', 1)[0]}.json"
    return next(card for card in json.loads(source.read_text(encoding="utf-8"))
                if card["id"] == cid)


def verify_card_text_and_legality() -> None:
    flutter, thorns, radiant, cologne, stone = (
        read_card(cid) for cid in (FLUTTER, THORNS, RADIANT, COLOGNE, STONE)
    )
    assert flutter["name"] == "Flutter Mane"
    assert "Basic" in flutter["subtypes"]
    assert "ex" not in flutter["subtypes"]
    assert not any(" Rule:" in rule for rule in flutter.get("rules") or [])
    assert any(a["name"] == "Midnight Fluttering"
               and "opponent's Active Pokémon has no Abilities" in a["text"]
               for a in flutter["abilities"])
    assert "Future" in thorns["subtypes"]
    assert any(a["name"] == "Initialization"
               and "except for Future Pokémon" in a["text"]
               for a in thorns["abilities"])
    assert "Radiant" in radiant["subtypes"]
    assert any(a["name"] == "Climactic Gate" for a in radiant["abilities"])
    assert any("opponent's Active Pokémon has no Abilities" in rule
               for rule in cologne["rules"])
    assert any(a["name"] == "Star Alchemy" for a in stone["abilities"])
    root = Path(__file__).resolve().parents[2]
    ids = {**PRINT_IDS, "Flutter Mane": FLUTTER, "Canceling Cologne": COLOGNE}
    for cologne_count, flutter_count in ((0, 0), (1, 0), (0, 1),
                                         (2, 0), (1, 1), (0, 2)):
        deck = deck_variant(cologne_count, flutter_count)
        proof = adjudicate_deck(
            [DeckEntry(ids[name], amount) for name, amount in deck.items()],
            root / "resources", as_of=date(2026, 10, 12)
        )
        assert proof.construction.valid, proof.construction.issues
        assert proof.disposition == "eligible_snapshot", proof.disposition
        assert all(p.eligibility == "eligible" for p in proof.print_proofs)
    print("Six exact-print 60-card conservative Expanded legality checks PASS")


def main() -> None:
    verify_card_text_and_legality()
    physical_toy_oracle()
    expected = {
        (0, 0): Fraction(0),
        (1, 0): Fraction(119260392833, 1748522406400),
        (0, 1): Fraction(94951987049, 1612973804000),
        (2, 0): Fraction(1990248996777451, 17093555044966400),
        (1, 1): Fraction(209827525698827, 1751205659002800),
        (0, 2): Fraction(713487559221, 6482624974280),
    }
    for case, goal in expected.items():
        distributions = exact(caps(*case))
        assert sum(distributions.values()) == 1
        value = successful(distributions)
        assert value == goal, (case, value, goal)
        print(f"Cologne={case[0]} Flutter={case[1]}: {float(value):.9%}")
    assert expected[(1, 1)] > expected[(2, 0)] > expected[(0, 2)]
    print("PASS: Mixed two-slot counter access outranks either homogeneous pair")


if __name__ == "__main__":
    main()
