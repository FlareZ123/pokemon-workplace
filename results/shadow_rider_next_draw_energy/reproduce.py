"""Independent source-deck and physical-toy tests of next-turn Psychic draw."""

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
from tools.shadow_rider_energy_reserve import retained_energy_treasure_route
from tools.shadow_rider_next_draw_energy import (
    next_draw_psychic_readiness,
    treasure_hand_prize_buckets,
)
from tools.shadow_rider_treasure_cost_sensitivity import (
    treasure_two_vmax_hand_buckets,
)


def card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(r for r in rows if r["id"] == card_id)


def physical_toy() -> int:
    """Enumerate the exact next draw from each source-legal toy launch."""

    caps = (1, 2, 2, 1, 2, 3)
    cards = tuple(
        (category, copy)
        for category, amount in enumerate(caps)
        for copy in range(amount)
    )
    accepted_deals = 0
    hits: Counter[tuple[int, bool]] = Counter()
    for opening in combinations(range(len(cards)), 3):
        opened = Counter(cards[i][0] for i in opening)
        if not (opened[0] + opened[4]):
            continue
        unseen = tuple(i for i in range(len(cards)) if i not in opening)
        for prized in combinations(unseen, 2):
            prize_set = set(prized)
            for first_draw in unseen:
                if first_draw in prize_set:
                    continue
                accepted_deals += 1
                visible = opening + (first_draw,)
                hand = Counter(cards[i][0] for i in visible)
                deck = tuple(
                    i for i in unseen
                    if i not in prize_set and i != first_draw
                )
                # Radiant still in deck; two VMAX still in deck; an
                # eligible other Basic was selected Active from opener.
                eligible = (
                    opened[4] >= 1
                    and hand[0] == 0
                    and hand[2] >= 1
                    and sum(cards[i][0] == 0 for i in deck) == 1
                    and sum(cards[i][0] == 1 for i in deck) == 2
                )
                if not eligible:
                    continue

                # A successful Treasure and Climactic Gate remove one
                # Dragon Radiant and exactly two VMAX from the deck.
                next_deck = tuple(
                    i for i in deck if cards[i][0] not in (0, 1)
                )
                assert len(next_deck) == 2
                initial_psychic = sum(
                    cards[i][0] == 5 and cards[i][1] < 2
                    for i in visible
                )
                for next_draw in next_deck:
                    next_is_psychic = int(
                        cards[next_draw][0] == 5
                        and cards[next_draw][1] < 2
                    )
                    for minimum in range(3):
                        for spare in (False, True):
                            pay_spare = spare and hand[2] >= 2
                            if not pay_spare and initial_psychic == 0:
                                continue
                            kept = (
                                initial_psychic
                                if pay_spare
                                else initial_psychic - 1
                            )
                            hits[(minimum, spare)] += int(
                                kept + next_is_psychic >= minimum
                            )
    assert accepted_deals == 18312
    denominator = accepted_deals * 2
    assert denominator == 36624

    buckets = treasure_hand_prize_buckets(
        caps, opening_size=3, prize_count=2
    )
    assert sum(buckets.values()) == Fraction(33, 763)
    for minimum in range(3):
        for spare in (False, True):
            calculated = next_draw_psychic_readiness(
                at_least_after_draw=minimum,
                allow_spare_treasure_payment=spare,
                caps=caps,
                opening_size=3,
                prize_count=2,
                psychic_energy=2,
                buckets=buckets,
            )
            literal = Fraction(
                hits[(minimum, spare)], denominator
            )
            assert calculated == literal, (
                minimum, spare, calculated, literal
            )
    return denominator


def main() -> None:
    treasure = card("sm6-113")
    radiant = card("swsh12pt5-105")
    shadow = card("swsh6-75")
    assert treasure["name"] == "Mysterious Treasure"
    assert radiant["name"] == "Radiant Eternatus"
    assert shadow["name"] == "Shadow Rider Calyrex VMAX"
    assert any(
        ability["name"] == "Climactic Gate"
        and "up to 2 Pokémon VMAX" in ability["text"]
        and "your turn ends" in ability["text"]
        for ability in radiant["abilities"]
    )
    assert any(
        ability["name"] == "Underworld Door"
        and "Psychic Energy card from your hand" in ability["text"]
        for ability in shadow["abilities"]
    )
    assert POKEMON["Shadow Rider Calyrex VMAX"] == 4
    assert TRAINERS["Mysterious Treasure"] == 4
    assert ENERGY["Psychic Energy"] == 11
    assert sum(POKEMON.values()) + sum(TRAINERS.values()) + sum(ENERGY.values()) == 60

    labeled = physical_toy()
    three_axis_buckets = treasure_hand_prize_buckets()
    original = treasure_two_vmax_hand_buckets()
    collapse = Counter()
    for (hand_filler, _prize_filler, hand_treasures), prob in (
        three_axis_buckets.items()
    ):
        collapse[(hand_filler, hand_treasures)] += prob
    assert dict(collapse) == original
    assert len(three_axis_buckets) == 154

    expected = {
        0: (
            Fraction(402091494907, 1618467020800),
            Fraction(117457006901, 445078430720),
        ),
        1: (
            Fraction(560181484951, 3803397498880),
            Fraction(380121800561, 2237292646400),
        ),
        2: (
            Fraction(377157153921, 7606794997760),
            Fraction(5075381043, 77620357120),
        ),
        3: (
            Fraction(4539154029, 475424687360),
            Fraction(2383775913, 161846702080),
        ),
    }
    results = []
    for minimum, (strict_expected, spare_expected) in expected.items():
        strict = next_draw_psychic_readiness(
            at_least_after_draw=minimum,
            buckets=three_axis_buckets,
        )
        spare = next_draw_psychic_readiness(
            at_least_after_draw=minimum,
            allow_spare_treasure_payment=True,
            buckets=three_axis_buckets,
        )
        assert (strict, spare) == (strict_expected, spare_expected)
        assert 0 <= strict <= spare <= sum(three_axis_buckets.values())
        assert strict >= retained_energy_treasure_route(
            retain_after_payment=minimum
        )
        assert spare >= retained_energy_treasure_route(
            retain_after_payment=minimum,
            allow_spare_treasure_payment=True,
        )
        results.append({
            "minimum_psychic_after_next_draw": minimum,
            "pay_energy_only": f"{float(strict):.12%}",
            "pay_energy_or_spare_treasure": f"{float(spare):.12%}",
        })

    assert expected[0][0] == retained_energy_treasure_route(
        retain_after_payment=0
    )
    assert expected[0][1] == retained_energy_treasure_route(
        retain_after_payment=0,
        allow_spare_treasure_payment=True,
    )
    print(json.dumps({
        "source_prints": (
            treasure["id"], radiant["id"], shadow["id"]
        ),
        "first_turn_post_launch_deck_count": 43,
        "independent_physical_toy_next_draw_worlds": labeled,
        "exact_next_natural_draw_readiness": results,
        "scope": "named source-deck line, no opponent or match outcomes",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
