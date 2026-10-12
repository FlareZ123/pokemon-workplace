"""SFT: exact real-list Heavy Ball Prize rescue and independent toy oracle."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    ENERGY, POKEMON, TRAINERS,
)
from results.shadow_rider_radiant_launch.reproduce import (
    exact as prior_exact,
)
from tools.shadow_rider_heavy_ball_launch import (
    COUNTS, baseline_without_heavy_route, classify, exact,
    launch_probability,
)


def verify_source_cards():
    root = Path(__file__).resolve().parents[2] / "resources" / "cards" / "en"

    def card(set_name, card_id):
        rows = json.loads((root / f"{set_name}.json").read_text(encoding="utf-8"))
        return next(row for row in rows if row["id"] == card_id)

    ball = card("swsh10", "swsh10-146")
    radiant = card("swsh12pt5", "swsh12pt5-105")
    treasure = card("sm6", "sm6-113")

    text = " ".join(ball["rules"])
    assert "Look at your face-down Prize cards" in text
    assert "put this Hisuian Heavy Ball in its place" in text
    assert "put it into your hand" in text
    assert "Basic Pokémon" in text
    assert "search your deck for up to 2 Pokémon VMAX" in radiant["abilities"][0]["text"]
    assert "When you play this Pokémon from your hand onto your Bench" in radiant["abilities"][0]["text"]
    assert "Discard a card from your hand" in treasure["rules"][0]
    assert "Psychic or Dragon Pokémon" in treasure["rules"][0]


def physical_oracle() -> None:
    """Independently enumerate fully labeled toy physical card selections."""

    caps = (1, 2, 1, 1, 2, 3)
    card_types = tuple(
        category
        for category, amount in enumerate(caps)
        for _ in range(amount)
    )
    observations = Counter()
    initial_acceptances = 0
    without_draw = Counter()
    after_draw = Counter()

    for opened_indices in combinations(range(len(card_types)), 3):
        opened_types = Counter(card_types[index] for index in opened_indices)
        if opened_types[0] + opened_types[4] == 0:
            continue
        rest = [
            index for index in range(len(card_types))
            if index not in opened_indices
        ]
        opening = tuple(opened_types[index] for index in range(6))

        for prize_indices in combinations(rest, 2):
            prizes = Counter(card_types[index] for index in prize_indices)
            prize_counts = tuple(prizes[index] for index in range(6))
            without_draw[classify(opening, prize_counts, None, caps)] += 1
            initial_acceptances += 1
            for draw_index in rest:
                if draw_index in prize_indices:
                    continue
                after_draw[classify(
                    opening, prize_counts, card_types[draw_index], caps
                )] += 1
                observations["all"] += 1

    for actual, grouped, denominator in (
        (without_draw, exact(caps, opening_size=3, prize_count=2,
                             first_turn_draw=False), initial_acceptances),
        (after_draw, exact(caps, opening_size=3, prize_count=2,
                           first_turn_draw=True), observations["all"]),
    ):
        assert set(actual) == set(grouped)
        for name, probability in grouped.items():
            assert probability == Fraction(actual[name], denominator), (
                name, probability, actual[name], denominator
            )

    print(f"Toy oracle matched {initial_acceptances} no-draw physical worlds")
    print(f"Toy oracle matched {observations['all']} drawn physical worlds")


def main() -> None:
    verify_source_cards()
    assert sum(POKEMON.values()) + sum(TRAINERS.values()) + sum(ENERGY.values()) == 60
    assert COUNTS == (
        POKEMON["Radiant Eternatus"],
        POKEMON["Shadow Rider Calyrex VMAX"],
        TRAINERS["Mysterious Treasure"],
        TRAINERS["Hisuian Heavy Ball"],
        sum(POKEMON.values()) - POKEMON["Radiant Eternatus"]
        - POKEMON["Shadow Rider Calyrex VMAX"],
        60 - 1 - 4 - 4 - 1 - 13,
    )

    physical_oracle()
    before = exact(first_turn_draw=False)
    after = exact(first_turn_draw=True)
    old = prior_exact()

    assert sum(before.values()) == 1
    assert sum(after.values()) == 1
    assert baseline_without_heavy_route(after) == (
        old["direct_2"] + old["treasure_2"]
    )
    for name in ("direct_2", "treasure_2", "no_eligible_active"):
        assert after[name] == old[name]

    assert before["heavy_2"] == Fraction(
        132395819839, 12239656844800
    )
    assert after["heavy_2"] == Fraction(
        121298091771, 9791725475840
    )
    assert after["direct_2"] == Fraction(2431309737, 20230837760)
    assert after["treasure_2"] == Fraction(176258415211, 556348038400)

    assert launch_probability(before) > baseline_without_heavy_route(before)
    assert launch_probability(after) > baseline_without_heavy_route(after)
    assert launch_probability(after) > launch_probability(before)

    print("Shadow Rider Heavy Ball opening access: source-verified and exact")
    for turn, results in (("first/no draw", before), ("second/one draw", after)):
        for route in ("direct", "treasure", "heavy"):
            probability = results[f"{route}_2"]
            print(f"{turn}: {route:8} {float(probability):.12%} [{probability}]")
        print(f"{turn}: total dual-VMAX {float(launch_probability(results)):.12%}")
    print("Marginal dual-VMAX gain from adding Heavy Ball route",
          f"{float(after['heavy_2']):.12%} conditional on accepted opener")
    print("Draw increment including Heavy Ball",
          f"{float(launch_probability(after)-launch_probability(before)):.12%}")


if __name__ == "__main__":
    main()
