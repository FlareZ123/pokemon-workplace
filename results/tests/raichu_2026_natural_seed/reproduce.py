"""SFT: natural opening evolution-base readiness for 2026 Aichi Raichu.

Exact labeled-hand combinatorics. One ordinary draw is marginally uniform
among the 53 cards outside the starting seven, with six Prizes unobserved.
No search, mulligan bonus draws, card-effect draw, or opponent interaction.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CARDS = ROOT / "resources" / "cards" / "en"
MANIFEST = ROOT / "results" / "decks" / "raichu-electrode-aichi-2026" / "manifest.json"
MANUAL = ROOT / "resources" / "manual" / "EN_advanced_manual-2025-transcription-structured.md"

POPULATION = (2, 1, 1, 9, 47)  # Voltorb, Pikachu, Ditto, other Basics, remaining
HAND_SIZE = 7
POOL_AFTER_HAND = 60 - HAND_SIZE


def choose(n: int, k: int) -> int:
    return math.comb(n, k) if 0 <= k <= n else 0


def two_evolution_bases(v: int, p: int, d: int) -> bool:
    """Two distinct source Basics for Electrode-GX and Alolan Raichu."""
    return bool((v > 0 and (p > 0 or d > 0)) or (p > 0 and d > 0))


def native_bases(v: int, p: int) -> bool:
    return v > 0 and p > 0


def source_card(card_id: str) -> dict:
    group = card_id.rsplit("-", 1)[0]
    records = json.loads((CARDS / f"{group}.json").read_text(encoding="utf-8"))
    return next(card for card in records if card["id"] == card_id)


def validate_sources() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = manifest["cards"]
    assert sum(row["quantity"] for row in rows) == 60
    q = {row["name"]: row["quantity"] for row in rows}
    assert q["Voltorb"] == 2 and q["Pikachu"] == 1 and q["Ditto ◇"] == 1
    basics = sum(
        row["quantity"]
        for row in rows
        if "Basic" in source_card(row["print_id"]).get("subtypes", ())
        and source_card(row["print_id"])["supertype"] == "Pokémon"
    )
    assert basics == 13
    assert (
        q["Voltorb"], q["Pikachu"], q["Ditto ◇"],
        basics - q["Voltorb"] - q["Pikachu"] - q["Ditto ◇"],
        60 - basics,
    ) == POPULATION

    voltorb = source_card("xy6-21")
    pikachu = source_card("swsh11-52")
    ditto = source_card("sm8-154")
    electrode = source_card("sm7-48")
    raichu = source_card("sm11-57")
    klefki = source_card("sv1-96")
    assert voltorb["name"] == "Voltorb" and "Basic" in voltorb["subtypes"]
    assert pikachu["name"] == "Pikachu" and "Basic" in pikachu["subtypes"]
    assert electrode["evolvesFrom"] == "Voltorb"
    assert raichu["evolvesFrom"] == "Pikachu"
    assert "Electro Rain" in [attack["name"] for attack in raichu["attacks"]]
    assert "Extra Energy Bomb" in [ability["name"] for ability in electrode["abilities"]]
    assert "Prism Star" in ditto["subtypes"]
    ability_text = ditto["abilities"][0]["text"]
    assert "put any Stage 1 card" in ability_text
    assert "can't use this Ability during your first turn" in ability_text
    assert "the turn this Pokémon was put into play" in ability_text
    lock_text = klefki["abilities"][0]["text"]
    assert "in the Active Spot" in lock_text
    assert "Basic Pokémon in play" in lock_text
    assert "have no Abilities" in lock_text
    assert (
        "Neither player can evolve any of their Pokémon during their first turn."
        in MANUAL.read_text(encoding="utf-8")
    )


def exact_counts() -> dict[str, int]:
    """Enumerate distinct seven-card hand compositions and one ordinary draw."""
    valid_hands = seven_seed = eight_seed = eight_native = 0
    for v, p, d, o in product(
        range(POPULATION[0] + 1),
        range(POPULATION[1] + 1),
        range(POPULATION[2] + 1),
        range(POPULATION[3] + 1),
    ):
        x = HAND_SIZE - v - p - d - o
        if not 0 <= x <= POPULATION[4] or not (v + p + d + o):
            continue
        held = (v, p, d, o, x)
        multiplicity = math.prod(
            choose(size, count) for size, count in zip(POPULATION, held)
        )
        valid_hands += multiplicity
        if two_evolution_bases(v, p, d):
            seven_seed += multiplicity
        for i, (size, count) in enumerate(zip(POPULATION, held)):
            available = size - count
            next_v = v + (i == 0)
            next_p = p + (i == 1)
            next_d = d + (i == 2)
            if two_evolution_bases(next_v, next_p, next_d):
                eight_seed += multiplicity * available
            if native_bases(next_v, next_p):
                eight_native += multiplicity * available
    return {
        "valid_hands": valid_hands,
        "seven_seed": seven_seed,
        "eight_seed": eight_seed,
        "eight_native": eight_native,
        "one_draw_denominator": valid_hands * POOL_AFTER_HAND,
    }


def main() -> None:
    validate_sources()
    observed = exact_counts()
    valid = choose(60, 7) - choose(47, 7)
    assert observed["valid_hands"] == valid

    seven_seed = choose(60, 7) - choose(58, 7) - 2 * choose(56, 6)
    eight_seed = choose(60, 8) - choose(58, 8) - 2 * choose(56, 7)
    eight_native = (
        choose(60, 8) - choose(58, 8)
        - choose(59, 8) + choose(57, 8)
    )
    assert observed["seven_seed"] == seven_seed
    assert Fraction(observed["eight_seed"], observed["one_draw_denominator"]) == (
        Fraction(eight_seed, choose(60, 8))
        / Fraction(valid, choose(60, 7))
    )
    assert Fraction(observed["eight_native"], observed["one_draw_denominator"]) == (
        Fraction(eight_native, choose(60, 8))
        / Fraction(valid, choose(60, 7))
    )

    valid_probability = Fraction(valid, choose(60, 7))
    seven_seed_probability = Fraction(observed["seven_seed"], valid)
    eight_seed_probability = Fraction(
        observed["eight_seed"], observed["one_draw_denominator"]
    )
    native_probability = Fraction(
        observed["eight_native"], observed["one_draw_denominator"]
    )
    ditto_dependent = eight_seed_probability - native_probability
    assert eight_seed_probability == Fraction(814128, 9797437)
    assert native_probability == Fraction(351120, 9797437)
    assert native_probability < eight_seed_probability
    assert seven_seed_probability < eight_seed_probability

    print(json.dumps({
        "source": "Shu Hosoda 2026 Aichi fourth place, 60 physical cards",
        "setup_bases": {
            "voltorb": 2, "pikachu": 1,
            "ditto_prism": 1, "other_basics": 9,
        },
        "opening_valid_seven_probability": float(valid_probability),
        "seven_seed_given_valid_seven": float(seven_seed_probability),
        "eight_seed_given_valid_seven": float(eight_seed_probability),
        "native_eight_seed_given_valid_seven": float(native_probability),
        "ditto_dependent_eight_seed_given_valid_seven": float(ditto_dependent),
        "ditto_fraction_of_seed": float(ditto_dependent / eight_seed_probability),
        "eight_seed_exact_fraction": str(eight_seed_probability),
        "native_seed_exact_fraction": str(native_probability),
        "earliest_normal_double_evolution_turn": 2,
        "klefki_active_suppresses_ditto_ability": True,
        "model_scope": "no search/draw effects/opponent bonus/prize knowledge, not win rate",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
