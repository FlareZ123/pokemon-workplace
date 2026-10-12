"""Exact restricted turn-one Cologne/Stone response to Iron Thorns Initialization.

Run: python -m results.shadow_rider_cologne_thorns_counter.reproduce
Percentages concern an opening action endpoint, NEVER competitive win rates.
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

COLOGNE = "swsh10-136"
STONE = "swsh12-156"
RADIANT = "swsh12pt5-105"
THORNS = "sv6-77"
CUTS = ("Sky Field", "Sky Field", "Dimension Valley", "Night Stretcher")

# Eight physical types: Radiant; VMAX; Mysterious Treasure; Cologne;
# Forest Seal Stone; Shadow Rider V; other Basic Pokemon; remainder.
def counts_for(k: int) -> tuple[int, ...]:
    assert 0 <= k <= 4
    assert sum(POKEMON.values()) == 18
    assert sum(TRAINERS.values()) == 31
    assert sum(ENERGY.values()) == 11
    assert POKEMON["Radiant Eternatus"] == 1
    assert POKEMON["Shadow Rider Calyrex VMAX"] == 4
    assert POKEMON["Shadow Rider Calyrex V"] == 3
    assert TRAINERS["Mysterious Treasure"] == 4
    assert TRAINERS["Forest Seal Stone"] == 1
    return (1, 4, 4, k, 1, 3, 10, 37 - k)


def variant(k: int) -> dict[str, int]:
    deck = {**POKEMON, **TRAINERS, **ENERGY}
    for cut in CUTS[:k]:
        deck[cut] -= 1
    if k:
        deck["Canceling Cologne"] = k
    deck = {name: qty for name, qty in deck.items() if qty > 0}
    assert sum(deck.values()) == 60
    return deck


def allocations(total: int, caps: tuple[int, ...]):
    if len(caps) == 1:
        if 0 <= total <= caps[0]:
            yield (total,)
        return
    for first in range(min(total, caps[0]) + 1):
        for rest in allocations(total - first, caps[1:]):
            yield (first,) + rest


def classify(opening: tuple[int, ...],
             prizes: tuple[int, ...], drawn: int,
             caps: tuple[int, ...]) -> str:
    if opening[0] + opening[5] + opening[6] == 0:
        return "mulligan"
    if opening[5] + opening[6] == 0:
        return "no_non_radiant_start"
    hand = tuple(opening[i] + int(drawn == i) for i in range(8))
    deck = tuple(caps[i] - opening[i] - prizes[i] - int(drawn == i)
                 for i in range(8))
    radiant_route = ("direct" if hand[0] else
                     "treasure" if hand[2] and deck[0] else None)
    # An ordinary V from opening/first draw is available for Tool attachment.
    stone_ready = bool(hand[4] and hand[5])
    if hand[3]:
        if radiant_route:
            route = "held_cologne_" + radiant_route
        elif stone_ready and deck[0]:
            route = "held_cologne_stone_radiant"
        else:
            route = None
    elif stone_ready and deck[3] and radiant_route:
        route = "stone_cologne_" + radiant_route
    else:
        route = None
    if route is None:
        return "no_route"
    if deck[1] < 2:
        return "too_few_vmax_in_deck"
    return route


def exact(caps: tuple[int, ...], opening_size: int = 7,
          prize_count: int = 6) -> dict[str, Fraction]:
    n = sum(caps)
    basic = caps[0] + caps[5] + caps[6]
    opening_ways = comb(n, opening_size) - comb(n - basic, opening_size)
    denominator = (opening_ways * comb(n - opening_size, prize_count)
                   * (n - opening_size - prize_count))
    buckets: Counter[str] = Counter()
    checked = 0
    for opening in allocations(opening_size, caps):
        if opening[0] + opening[5] + opening[6] == 0:
            continue
        weight1 = prod(comb(c, x) for c, x in zip(caps, opening))
        remain = tuple(c - x for c, x in zip(caps, opening))
        for prizes in allocations(prize_count, remain):
            weight2 = weight1 * prod(comb(c, x)
                                     for c, x in zip(remain, prizes))
            after = tuple(c - x for c, x in zip(remain, prizes))
            for drawn, copies in enumerate(after):
                if copies == 0:
                    continue
                weight = weight2 * copies
                buckets[classify(opening, prizes, drawn, caps)] += weight
                checked += weight
    assert checked == denominator
    return {label: Fraction(weight, denominator)
            for label, weight in buckets.items()}


def physical_toy_oracle() -> None:
    """Independent labeled-card deals, rather than hypergeometric weights."""
    caps = (1, 2, 1, 1, 1, 1, 1, 2)
    identities = tuple(c for c, num in enumerate(caps) for _ in range(num))
    outcomes: Counter[str] = Counter()
    accepted = 0
    for opener in combinations(range(len(identities)), 3):
        opening = tuple(sum(identities[i] == c for i in opener)
                        for c in range(8))
        if opening[0] + opening[5] + opening[6] == 0:
            continue
        rest = set(range(len(identities))) - set(opener)
        for prize_indices in combinations(sorted(rest), 2):
            prizes = tuple(sum(identities[i] == c for i in prize_indices)
                           for c in range(8))
            for draw_index in sorted(rest - set(prize_indices)):
                outcomes[classify(opening, prizes, identities[draw_index], caps)] += 1
                accepted += 1
    assert accepted == 8925
    expected = exact(caps, 3, 2)
    assert set(expected) == set(outcomes)
    for label, probability in expected.items():
        assert probability == Fraction(outcomes[label], accepted), label
    print("Independent physical-label toy oracle: 8925 accepted worlds PASS")


def read_card(card_id: str) -> dict:
    root = Path(__file__).resolve().parents[2]
    set_id = card_id.rsplit("-", 1)[0]
    source = root / "resources" / "cards" / "en" / f"{set_id}.json"
    return next(card for card in json.loads(source.read_text(encoding="utf-8"))
                if card["id"] == card_id)


def verify_prints_and_legality() -> None:
    cologne, stone, radiant, thorns = map(
        read_card, (COLOGNE, STONE, RADIANT, THORNS)
    )
    assert cologne["name"] == "Canceling Cologne"
    assert "Item" in cologne["subtypes"]
    assert any("opponent's Active Pokémon has no Abilities" in rule
               and "end of your turn" in rule for rule in cologne["rules"])
    assert stone["name"] == "Forest Seal Stone"
    assert "Pokémon Tool" in stone["subtypes"]
    assert any("Pokémon V this card is attached to can use" in rule
               for rule in stone["rules"])
    assert any(a["name"] == "Star Alchemy" and "search your deck for a card" in a["text"]
               for a in stone["abilities"])
    assert "Radiant" in radiant["subtypes"]
    assert "Future" not in radiant["subtypes"]
    assert any(a["name"] == "Climactic Gate" and "turn ends" in a["text"]
               for a in radiant["abilities"])
    assert "Future" in thorns["subtypes"]
    assert any(a["name"] == "Initialization" and "except for Future Pokémon" in a["text"]
               for a in thorns["abilities"])
    root = Path(__file__).resolve().parents[2]
    ids = {**PRINT_IDS, "Canceling Cologne": COLOGNE}
    for k in range(5):
        deck = variant(k)
        proof = adjudicate_deck(
            [DeckEntry(ids[name], qty) for name, qty in deck.items()],
            root / "resources", as_of=date(2026, 10, 12)
        )
        assert proof.construction.valid, (k, proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (k, proof.disposition)
        assert all(p.eligibility == "eligible" for p in proof.print_proofs)
    print("All five 60-card exact-print counterfactual decks eligible PASS")


def main() -> None:
    verify_prints_and_legality()
    physical_toy_oracle()
    expected = (
        Fraction(0),
        Fraction(119260392833, 1748522406400),
        Fraction(1990248996777451, 17093555044966400),
        Fraction(9470911961112829, 59827442657382400),
        Fraction(17562578449304111, 89741163986073600),
    )
    held_expected = (0.0, 0.05057564925901034, 0.0961584196675435,
                     0.13715222430850904, 0.17393585433054575)
    for k in range(5):
        result = exact(counts_for(k))
        assert sum(result.values()) == 1
        held = sum((value for label, value in result.items()
                    if label in ("held_cologne_direct", "held_cologne_treasure")),
                   Fraction(0))
        counter = sum((value for label, value in result.items()
                       if label.startswith(("held_cologne_", "stone_cologne_"))),
                      Fraction(0))
        assert abs(float(held) - held_expected[k]) < 1e-12, (k, held)
        assert counter == expected[k], (k, counter)
        print(f"Cologne={k}: held {float(held):.9%}; with Stone {float(counter):.9%}; "
              f"increment {float(counter-held):.9%}")
    print("PASS: Exact fractions, Prize distributions, first-draw and Stone routing")


if __name__ == "__main__":
    main()
