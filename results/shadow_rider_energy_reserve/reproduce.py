"""Exact champion Shadow Rider Psychic Energy retention after Treasure payment."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    ENERGY,
    POKEMON,
    TRAINERS,
)
from tools.shadow_rider_energy_reserve import (
    energy_tail,
    retained_energy_frontier,
    retained_energy_treasure_route,
)
from tools.shadow_rider_heavy_ball_launch import (
    COUNTS,
    exact,
)
from tools.shadow_rider_treasure_cost_sensitivity import (
    acceptable_discard_probability,
    treasure_two_vmax_hand_buckets,
)


def card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(row for row in rows if row["id"] == card_id)


def physical_toy_oracle() -> int:
    """Independently enumerate labeled openers, Prize cards and draws.

    The 11-card physical toy has two designated Psychic filler cards and a
    third non-Energy filler. Treasure has two physical copies so that the
    alternative extra-Treasure payment is testable as a different mechanism.
    """

    caps = (1, 2, 2, 1, 2, 3)
    cards = tuple(
        (category, copy)
        for category, copies in enumerate(caps)
        for copy in range(copies)
    )
    assert len(cards) == 11
    denominator = 0
    events: Counter[tuple[int, bool]] = Counter()
    for opening in combinations(range(len(cards)), 3):
        opened = Counter(cards[i][0] for i in opening)
        if opened[0] + opened[4] == 0:
            continue
        remaining = tuple(
            i for i in range(len(cards)) if i not in opening
        )
        for prized in combinations(remaining, 2):
            prized_set = set(prized)
            for drawn in remaining:
                if drawn in prized_set:
                    continue
                denominator += 1
                visible = opening + (drawn,)
                hand = Counter(cards[i][0] for i in visible)
                searchable = Counter(
                    cards[i][0] for i in remaining
                    if i not in prized_set and i != drawn
                )
                # Same named Treasure_2 physical condition as the exact
                # six-group classifier: an eligible other Basic starts
                # Active, Radiant is still in the deck, and both VMAX
                # copies remain searchable there. A held Heavy Ball does
                # not supersede Treasure when Radiant is still in deck.
                eligible = (
                    opened[4] >= 1
                    and hand[0] == 0
                    and hand[2] >= 1
                    and searchable[0] == 1
                    and searchable[1] == 2
                )
                if not eligible:
                    continue

                psychic_held = sum(
                    cards[i][0] == 5 and cards[i][1] < 2
                    for i in visible
                )
                for remaining_psychic in range(3):
                    strict = psychic_held >= remaining_psychic + 1
                    spare = (
                        strict or (
                            hand[2] >= 2
                            and psychic_held >= remaining_psychic
                        )
                    )
                    events[(remaining_psychic, False)] += int(strict)
                    events[(remaining_psychic, True)] += int(spare)

    grouped = treasure_two_vmax_hand_buckets(
        caps, opening_size=3, prize_count=2
    )
    assert sum(grouped.values()) == Fraction(33, 763)
    assert denominator == 18312

    for required in range(3):
        for allow_spare in (False, True):
            computed = retained_energy_treasure_route(
                retain_after_payment=required,
                allow_spare_treasure_payment=allow_spare,
                psychic_energy=2,
                total_filler=3,
                buckets=grouped,
            )
            observed = Fraction(events[(required, allow_spare)], denominator)
            assert computed == observed, (
                required, allow_spare, computed, observed
            )
    return denominator


def main() -> None:
    treasure = card("sm6-113")
    shadow = card("swsh6-75")
    radiant = card("swsh12pt5-105")
    assert treasure["name"] == "Mysterious Treasure"
    assert "Discard a card from your hand" in treasure["rules"][0]
    assert shadow["name"] == "Shadow Rider Calyrex VMAX"
    assert any(
        ability["name"] == "Underworld Door"
        and "Psychic Energy card from your hand" in ability["text"]
        for ability in shadow["abilities"]
    )
    assert radiant["name"] == "Radiant Eternatus"

    assert COUNTS == (1, 4, 4, 1, 13, 37)
    assert ENERGY["Psychic Energy"] == 11
    assert TRAINERS["Mysterious Treasure"] == 4
    assert POKEMON["Shadow Rider Calyrex VMAX"] == 4
    assert sum(POKEMON.values()) + sum(TRAINERS.values()) + sum(ENERGY.values()) == 60

    assert energy_tail(
        3, total_filler=37, psychic_energy=11, at_least=0
    ) == 1
    assert energy_tail(
        3, total_filler=37, psychic_energy=11, at_least=4
    ) == 0
    assert energy_tail(
        3, total_filler=37, psychic_energy=11, at_least=2
    ) == Fraction(
        1, 1
    ) - Fraction(
        (26 * 25 * 24) + (3 * 11 * 26 * 25),
        37 * 36 * 35,
    )

    toy_worlds = physical_toy_oracle()
    frontier = retained_energy_frontier(3)

    expected = {
        0: (
            Fraction(402091494907, 1618467020800),
            Fraction(117457006901, 445078430720),
        ),
        1: (
            Fraction(230770753, 1904078848),
            Fraction(9404186203, 64738680832),
        ),
        2: (
            Fraction(2160627843, 64738680832),
            Fraction(1079894919, 23120957440),
        ),
        3: (
            Fraction(197102433, 40461675520),
            Fraction(2630261163, 323693404160),
        ),
    }
    for count, strict, spare in frontier:
        assert (strict, spare) == expected[count]
        assert 0 <= strict <= spare
    for previous, following in zip(frontier, frontier[1:]):
        assert following[1] <= previous[1]
        assert following[2] <= previous[2]

    base_buckets = treasure_two_vmax_hand_buckets()
    assert sum(base_buckets.values()) == exact()["treasure_2"]
    assert expected[0][0] == acceptable_discard_probability(
        base_buckets, safe_filler_copies=11,
    )
    assert expected[0][1] == acceptable_discard_probability(
        base_buckets, safe_filler_copies=11,
        allow_spare_treasure=True,
    )

    summary = {
        "champion_source_prints": (
            treasure["id"], radiant["id"], shadow["id"]
        ),
        "independent_labeled_toy_worlds": toy_worlds,
        "named_Treasure_route_no_retention_restriction": (
            f"{float(sum(base_buckets.values())):.12%}"
        ),
        "retained_psychic_frontier": [
            {
                "held_after_payment": m,
                "energy_only": f"{float(strict):.12%}",
                "energy_or_spare_treasure": f"{float(spare):.12%}",
            }
            for m, strict, spare in frontier
        ],
        "one_energy_retention_loss_percentage_points": (
            f"{float(expected[0][0] - expected[1][0]) * 100:.12f}"
        ),
        "extra_spare_treasure_retention_gain_points": (
            f"{float(expected[1][1] - expected[1][0]) * 100:.12f}"
        ),
        "scope": (
            "physical start/Prize/draw access and retained hand Energy; "
            "no match wins or opponent modeling"
        ),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
