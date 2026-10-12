"""Exact 60-card Basic-valid Wobbuffet opening and natural free-pivot oracle."""

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
manifest = json.loads((ROOT / "results" / "regidrago_aichi_top10_playable" /
                       "yoshioka_regidrago_2026.json").read_text(encoding="utf-8"))
printed = {
    card["id"]: card
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json"))
    for card in json.loads(path.read_text(encoding="utf-8"))
}
entries = manifest["groups"]["Pokémon"]
basics = sum(entry["count"] for entry in entries
             if "Basic" in printed[entry["print_id"]].get("subtypes", []))
assert basics == 15, basics
assert {entry["name"]: entry["count"] for entry in entries}["Wobbuffet"] == 1
assert {entry["name"]: entry["count"] for entry in entries}["Regidrago V"] == 4
assert {entry["name"]: entry["count"] for entry in entries}["Latias ex"] == 1
assert len(printed["xy4-36"]["retreatCost"]) == 2
assert printed["sv8-76"]["types"] == ["Psychic"]
assert "Your Basic Pokémon in play have no Retreat Cost." == printed["sv8-76"]["abilities"][0]["text"]


def c(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def exact_opening(n: int, basic: int, hand: int, rare: int,
                  backup: int, free_pivot: int) -> dict[str, Fraction]:
    """Uniform valid initial hand; one required Basic singleton.

    The Basic count includes the rare singleton, backup and free-pivot classes.
    """
    assert 1 + backup + free_pivot <= basic <= n
    total = c(n, hand)
    valid_count = total - c(n - basic, hand)
    w = c(n - 1, hand - 1)
    assert rare == 1
    remaining = n - 1
    extra = hand - 1
    with_backup = w - c(remaining - backup, extra)
    with_pivot = w - c(remaining - free_pivot, extra)
    with_both = (w - c(remaining - backup, extra)
                 - c(remaining - free_pivot, extra)
                 + c(remaining - backup - free_pivot, extra))
    return {
        "valid_opener": Fraction(valid_count, total),
        "wobb_active_possible": Fraction(w, valid_count),
        "wobb_and_regidrago_v": Fraction(with_backup, valid_count),
        "wobb_and_latias": Fraction(with_pivot, valid_count),
        "wobb_regidrago_v_latias": Fraction(with_both, valid_count),
    }


values = exact_opening(60, basics, 7, 1, 4, 1)
for key, fraction in values.items():
    print(f"{key:27s} {fraction} = {100 * float(fraction):.9f}%")

assert values["wobb_active_possible"] > values["wobb_and_regidrago_v"]
assert values["wobb_and_regidrago_v"] > values["wobb_regidrago_v_latias"]
assert values["wobb_and_latias"] > values["wobb_regidrago_v_latias"]
assert values["wobb_and_regidrago_v"] > 0


def exhaustive_small(n: int, basics: int, hand: int,
                     backups: int, pivot: int) -> dict[str, Fraction]:
    """Independent labeled physical-hand oracle for small toy pools."""
    cards = ["W"] + ["R"] * backups + ["L"] * pivot
    cards.extend(["B"] * (basics - len(cards)))
    cards.extend(["X"] * (n - len(cards)))
    labels = Counter()
    for positions in combinations(range(n), hand):
        observed = [cards[i] for i in positions]
        if not any(card != "X" for card in observed):
            continue
        labels["valid"] += 1
        if "W" not in observed:
            continue
        labels["wobb_active_possible"] += 1
        if "R" in observed:
            labels["wobb_and_regidrago_v"] += 1
        if "L" in observed:
            labels["wobb_and_latias"] += 1
        if "R" in observed and "L" in observed:
            labels["wobb_regidrago_v_latias"] += 1
    return {name: Fraction(labels[name], labels["valid"])
            for name in ("wobb_active_possible", "wobb_and_regidrago_v",
                         "wobb_and_latias", "wobb_regidrago_v_latias")}


checks = 0
for n in range(6, 11):
    for hand in range(2, min(n, 4) + 1):
        for backups in (1, 2):
            for pivot in (1, 2):
                for basic in range(1 + backups + pivot, min(n, 1 + backups + pivot + 2) + 1):
                    got = exact_opening(n, basic, hand, 1, backups, pivot)
                    oracle = exhaustive_small(n, basic, hand, backups, pivot)
                    for key in oracle:
                        assert got[key] == oracle[key], (n, basic, hand, key)
                    checks += 1

assert checks >= 100, checks
print("PASS:", checks, "labeled toy physical enumeration cases agree exactly.")
