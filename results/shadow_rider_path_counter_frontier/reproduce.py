"""Prize-integrated first-turn answers to Active Iron Thorns + Path.

Run as module results.shadow_rider_path_counter_frontier.reproduce.
Rates are restricted access endpoints, not real match wins.
"""
from __future__ import annotations
import json
from datetime import date
from fractions import Fraction
from itertools import combinations
from math import comb, prod
from pathlib import Path
from results.competitive_deck_baselines.shadow_rider_reproduce import (
    POKEMON, TRAINERS, ENERGY, PRINT_IDS
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry

# Radiant, VMAX, Treasure, Cologne, Flutter, Stone, V,
# other Basic, Stadium, Field Blower, other.
CRITICAL = (0, 1, 3, 8, 9)
CUTS = ("Sky Field", "Sky Field", "Dimension Valley", "Night Stretcher")
IDS = {"Canceling Cologne": "swsh10-136", "Flutter Mane": "sv5-78"}
PATH_ID, BLOWER_ID = "swsh6-148", "sm2-125"


def counts(c: int, f: int) -> tuple[int, ...]:
    assert 0 <= c and 0 <= f and c + f <= 4
    s = max(0, 3 - c - f)
    return (1, 4, 4, c, f, 1, 3, 10, s, 1, 36 - c - f - s)


def variant(c: int, f: int) -> dict[str, int]:
    deck = {**POKEMON, **TRAINERS, **ENERGY}
    for cut in CUTS[:c + f]:
        deck[cut] -= 1
    if c:
        deck["Canceling Cologne"] = c
    if f:
        deck["Flutter Mane"] = f
    deck = {name: qty for name, qty in deck.items() if qty > 0}
    assert sum(deck.values()) == 60
    return deck


def alloc(n: int, caps: tuple[int, ...]):
    if len(caps) == 1:
        if 0 <= n <= caps[0]:
            yield (n,)
        return
    for a in range(min(n, caps[0]) + 1):
        for b in alloc(n - a, caps[1:]):
            yield (a,) + b


def feasible(op: tuple[int, ...], hand: tuple[int, ...],
             deck: tuple[int, ...] | list[int]) -> bool:
    if deck[1] < 2:
        return False
    flutter = bool(op[4])
    if not flutter and op[6] + op[7] == 0:
        return False
    stone = bool(hand[5] and hand[6])
    radiant = bool(hand[0] or hand[2] and deck[0])
    stadium = bool(hand[8] or hand[9])
    missing: list[str] = []
    if not radiant:
        missing.append("radiant")
    if not stadium:
        missing.append("stadium")
    if not flutter and not hand[3]:
        missing.append("cologne")
    if not missing:
        return True
    if len(missing) != 1 or not stone:
        return False
    lookup = {"radiant": (0,), "stadium": (8, 9), "cologne": (3,)}
    return sum(deck[i] for i in lookup[missing[0]]) > 0


def exact(caps: tuple[int, ...], opener_size: int = 7,
          prize_count: int = 6) -> Fraction:
    """Draw and Prize sets commute; irrelevant Prizes are marginalized."""
    n = sum(caps)
    basics = caps[0] + caps[4] + caps[6] + caps[7]
    opening_ways = comb(n, opener_size) - comb(n - basics, opener_size)
    denominator = (opening_ways * (n - opener_size)
                   * comb(n - opener_size - 1, prize_count))
    mass = success = 0
    for op in alloc(opener_size, caps):
        if op[0] + op[4] + op[6] + op[7] == 0:
            continue
        w0 = prod(comb(q, x) for q, x in zip(caps, op))
        remain = tuple(q - x for q, x in zip(caps, op))
        for d, multiple in enumerate(remain):
            if not multiple:
                continue
            hand = tuple(op[i] + int(i == d) for i in range(len(caps)))
            after = tuple(remain[i] - int(i == d)
                          for i in range(len(caps)))
            tracked = tuple(after[i] for i in CRITICAL)
            prize_caps = tracked + (sum(after) - sum(tracked),)
            for p in alloc(prize_count, prize_caps):
                w = w0 * multiple * prod(comb(q, x)
                                         for q, x in zip(prize_caps, p))
                mass += w
                live = list(after)
                for i, card_type in enumerate(CRITICAL):
                    live[card_type] -= p[i]
                success += w * int(feasible(op, hand, live))
    assert mass == denominator, (mass, denominator)
    return Fraction(success, denominator)


def physical_oracle() -> None:
    """Independent chronological labeled deals, no Prize marginalization."""
    caps = (1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    physical = tuple(i for i, n in enumerate(caps) for _ in range(n))
    hit = total = 0
    for start in combinations(range(len(physical)), 3):
        op = tuple(sum(physical[i] == t for i in start)
                   for t in range(len(caps)))
        if op[0] + op[4] + op[6] + op[7] == 0:
            continue
        rest = set(range(len(physical))) - set(start)
        for prizes in combinations(sorted(rest), 2):
            after = rest - set(prizes)
            for draw in sorted(after):
                hand = tuple(op[i] + int(physical[draw] == i)
                             for i in range(len(caps)))
                deck = tuple(sum(physical[j] == i
                                 for j in after if j != draw)
                             for i in range(len(caps)))
                hit += int(feasible(op, hand, deck))
                total += 1
    assert total == 41328
    assert Fraction(hit, total) == exact(caps, 3, 2)
    print("Independent 41,328-world physical oracle PASS")


def print_record(card_id: str) -> dict:
    resources = Path(__file__).resolve().parents[2] / "resources" / "cards" / "en"
    data = json.loads((resources / f"{card_id.rsplit('-', 1)[0]}.json")
                      .read_text(encoding="utf-8"))
    return next(x for x in data if x["id"] == card_id)


def check_cards() -> None:
    peak, blower, cologne, flutter = (
        print_record(i) for i in
        (PATH_ID, BLOWER_ID, IDS["Canceling Cologne"], IDS["Flutter Mane"])
    )
    assert peak["name"] == "Path to the Peak"
    assert any("Rule Box" in x and "no Abilities" in x
               for x in peak["rules"])
    assert blower["name"] == "Field Blower"
    assert any("Stadium cards in play" in x and "discard them" in x
               for x in blower["rules"])
    assert cologne["name"] == "Canceling Cologne"
    assert any("opponent's Active Pokémon has no Abilities" in x
               for x in cologne["rules"])
    assert flutter["name"] == "Flutter Mane"
    assert "Basic" in flutter["subtypes"] and not flutter.get("rules")
    assert any(x["name"] == "Midnight Fluttering"
               and "opponent's Active Pokémon has no Abilities" in x["text"]
               for x in flutter["abilities"])
    assert TRAINERS["Sky Field"] == 2
    assert TRAINERS["Dimension Valley"] == 1
    assert TRAINERS["Field Blower"] == 1
    assert TRAINERS["Forest Seal Stone"] == 1
    assert POKEMON["Shadow Rider Calyrex V"] == 3
    root = Path(__file__).resolve().parents[2]
    ids = {**PRINT_IDS, **IDS}
    for c, f in ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1),
                 (0, 2), (3, 0), (4, 0)):
        deck = variant(c, f)
        proof = adjudicate_deck(
            [DeckEntry(ids[n], q) for n, q in deck.items()],
            root / "resources", as_of=date(2026, 10, 12))
        assert proof.construction.valid, (c, f, proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (c, f)
        assert all(p.eligibility == "eligible" for p in proof.print_proofs)
        assert counts(c, f)[8] == sum(
            q for n, q in deck.items()
            if n in ("Sky Field", "Dimension Valley"))
    print("Eight complete 60-card exact-print legality checks PASS")


def main() -> None:
    check_cards()
    physical_oracle()
    expected = {
        (0, 0): Fraction(0),
        (1, 0): Fraction(44567700223329, 2257639345561600),
        (0, 1): Fraction(322511728541791, 17512056590028000),
        (2, 0): Fraction(28650171952739, 1150527743411200),
        (1, 1): Fraction(32802078670643, 1250861185002000),
        (0, 2): Fraction(672249515574867, 26812136893622080),
        (3, 0): Fraction(44567700223329, 2257639345561600),
        (4, 0): Fraction(18385984845499, 741662512281600),
    }
    for key, wanted in expected.items():
        value = exact(counts(*key))
        assert value == wanted, (key, value, wanted)
        print(f"Cologne={key[0]} Flutter={key[1]}: {float(value):.9%}")
    assert expected[(1, 1)] > expected[(2, 0)] > expected[(4, 0)]
    assert expected[(1, 0)] == expected[(3, 0)]
    print("PASS: paired lock counter access and resource symmetry")


if __name__ == "__main__":
    main()
