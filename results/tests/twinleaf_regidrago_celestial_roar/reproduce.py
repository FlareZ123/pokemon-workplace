"""Exact blind-three null model for missing Special Energy Celestial Roar attachments.

This is a source-deck *composition* diagnostic, not the distribution of
Celestial Roar attacks conditional on setup, Prize placement, deck thinning,
or bot/human policy. Pure Python standard library, Windows-compatible.
"""
from __future__ import annotations

from fractions import Fraction
from json import loads
from math import comb
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE = REPO_ROOT / "results" / "competitive_deck_baselines" / "regidrago_haruku_2026.json"


def exact_three_draw_census() -> dict[str, Fraction]:
    cards = loads(SOURCE.read_text(encoding="utf-8"))["cards"]
    total = sum(row["quantity"] for row in cards)
    special = sum(row["quantity"] for row in cards if row["name"] == "Double Dragon Energy")
    basic = sum(row["quantity"] for row in cards if row["name"] in {"Grass Energy", "Fire Energy"})
    assert (total, special, basic) == (60, 4, 6)
    draws = 3
    denominator = comb(total, draws)
    any_double_dragon = Fraction(denominator - comb(total - special, draws), denominator)
    any_energy = Fraction(denominator - comb(total - special - basic, draws), denominator)
    mean_missed_special_cards = Fraction(draws * special, total)
    # Each Double Dragon provides 2 energy units only when attached to Dragon.
    mean_missed_units = mean_missed_special_cards * 2
    return {
        "at_least_one_double_dragon": any_double_dragon,
        "at_least_one_energy": any_energy,
        "missed_special_energy_cards_mean": mean_missed_special_cards,
        "missed_double_dragon_units_mean": mean_missed_units,
    }


def main() -> None:
    result = exact_three_draw_census()
    assert result == {
        "at_least_one_double_dragon": Fraction(325, 1711),
        "at_least_one_energy": Fraction(731, 1711),
        "missed_special_energy_cards_mean": Fraction(1, 5),
        "missed_double_dragon_units_mean": Fraction(2, 5),
    }
    for key, fraction in result.items():
        print(f"{key}: {fraction} ({float(fraction):.9%})")
    print("PASS: source-60 exact blind-three Special Energy risk verified")


if __name__ == "__main__":
    main()
