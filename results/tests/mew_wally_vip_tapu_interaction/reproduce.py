"""Exact first-turn Mew/Genesect Wally-attack objective versus two card swaps.

Experiments are complete 60-card paper Expanded snapshot constructions.
The two options share the same lost one Special Red Card copy.
They must not be interpreted as a full-game deck quality ranking.
"""
from __future__ import annotations

import sys
from datetime import date
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.competitive_deck_baselines.mew_genesect_reproduce import (
    POKEMON, TRAINERS, ENERGY, PRINT_IDS,
)
from results.tests.mew_wally_first_attack.paid_ball_routes import (
    exact as no_lele_exact, oracle as no_lele_oracle,
)
from results.tests.mew_wally_tapu_variant.reproduce import (
    exact as lele_exact, physical_oracle as lele_oracle,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry

# Two independent slot decisions on the *same* source Aichi fifth-place 60:
# Extra VIP4 and/or first Tapu Lele-GX, both displacing Special Red Card.
# No Lele groups: Mew, Genesect, VMAX, Wally, DCE, VIP, Quick, Ultra, filler
# With Lele: identical first eight categories, Tapu, filler.
CASES = {
    "published": (4, 4, 3, 1, 4, 3, 4, 4, 33),
    "vip4_remove_red": (4, 4, 3, 1, 4, 4, 4, 4, 32),
    "lele_remove_red": (4, 4, 3, 1, 4, 3, 4, 4, 1, 32),
    "vip4_lele_remove_two_red": (4, 4, 3, 1, 4, 4, 4, 4, 1, 31),
}
EXPECTED = {
    "published": Fraction(167155400140607, 11575496365633200),
    "vip4_remove_red": Fraction(128968148547649, 8681622274224900),
    "lele_remove_red": Fraction(636040115150563, 8681622274224900),
    "vip4_lele_remove_two_red": Fraction(1025739340259, 13439043768150),
}


def model(pool: tuple[int, ...], hand: int, prizes: int) -> Fraction:
    if len(pool) == 9:
        return sum(no_lele_exact(pool, hand, prizes), Fraction(0))
    return sum(lele_exact(pool, hand, prizes).values(), Fraction(0))


def physical(pool: tuple[int, ...], hand: int, prizes: int) -> Fraction:
    if len(pool) == 9:
        return sum(no_lele_oracle(pool, hand, prizes), Fraction(0))
    return sum(lele_oracle(pool, hand, prizes).values(), Fraction(0))


def verify_printed_variants() -> None:
    for name in CASES:
        poke = dict(POKEMON)
        trainers = dict(TRAINERS)
        energy = dict(ENERGY)
        prints = dict(PRINT_IDS)
        add_vip = "vip4" in name
        add_lele = "lele" in name
        if add_vip:
            trainers["Battle VIP Pass"] += 1
            trainers["Special Red Card"] -= 1
        if add_lele:
            poke["Tapu Lele-GX"] = 1
            prints["Tapu Lele-GX"] = "sm2-60"
            trainers["Special Red Card"] -= 1
        counts = {**poke, **trainers, **energy}
        assert sum(counts.values()) == 60, name
        assert counts["Special Red Card"] == 2 - int(add_vip) - int(add_lele)
        assert counts["Battle VIP Pass"] == 3 + int(add_vip)
        assert counts.get("Tapu Lele-GX", 0) == int(add_lele)
        cards = [DeckEntry(prints[c], count) for c, count in counts.items() if count]
        proof = adjudicate_deck(
            cards, ROOT / "resources", as_of=date(2026, 10, 12)
        )
        assert proof.construction.valid, (name, proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (name, proof.disposition)
        print(f"{name}: exact-print Expanded snapshot verified")


def main():
    verify_printed_variants()
    toy = (
        ("published", (1, 1, 1, 1, 1, 1, 1, 1, 4)),
        ("vip4_remove_red", (1, 1, 1, 1, 1, 2, 1, 1, 3)),
        ("lele_remove_red", (1, 1, 1, 1, 1, 1, 1, 1, 1, 3)),
        ("vip4_lele_remove_two_red", (1, 1, 1, 1, 1, 2, 1, 1, 1, 2)),
    )
    for name, pop in toy:
        result = model(pop, 4, 2)
        expected = physical(pop, 4, 2)
        assert result == expected, (name, result, expected)
        print(f"{name}: independent physically labeled oracle PASSED")
    outcomes = {}
    for name, pop in CASES.items():
        assert sum(pop) == 60
        actual = model(pop, 7, 6)
        assert actual == EXPECTED[name], (name, actual)
        outcomes[name] = actual
        basics = 12 if "lele" in name else 11
        valid = 1 - Fraction(comb(60 - basics, 7), comb(60, 7))
        print(f"{name}: {float(actual):.12%} unconditional, "
              f"{float(actual / valid):.12%} valid-seven conditional")
    orig = outcomes["published"]
    vip = outcomes["vip4_remove_red"]
    lele = outcomes["lele_remove_red"]
    both = outcomes["vip4_lele_remove_two_red"]
    marginal_vip = vip - orig
    marginal_vip_with_lele = both - lele
    interaction = marginal_vip_with_lele - marginal_vip
    assert interaction == Fraction(30647866952743, 11575496365633200)
    assert interaction > 0
    print(f"VIP4 lift without Lele: {float(marginal_vip):.12%}")
    print(f"VIP4 lift with Lele: {float(marginal_vip_with_lele):.12%}")
    print(f"positive source interaction: {float(interaction):.12%}")


if __name__ == "__main__":
    main()
