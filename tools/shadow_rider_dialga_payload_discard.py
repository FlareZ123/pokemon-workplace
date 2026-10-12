"""Exact incremental Radiant-launch access from discarding singleton Dialga-GX.

For Regidrago counterplay, Dialga-GX in discard can supply Timeless-GX after
Mimikyu copies Apex Dragon. This computes *conditional opening feasibility*
when using the held Dialga as the Mysterious Treasure cost. It does not score
the later counter-line or claim universal discard desirability.

The 13 interchangeable 'other Basic' cards in the validated Shadow Rider
six-category opening kernel contain exactly one Dialga-GX. Conditional on
category counts, its physical position is uniform among those 13 copies.
"""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations
from math import comb, prod
from pathlib import Path

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    POKEMON,
    PRINT_IDS,
)
from tools.shadow_rider_treasure_discard_sensitivity import (
    COUNTS,
    allocations,
    exact as payment_exact,
    success_flags,
)


def eligible_dialga_positions(
    opening_basics: int,
    first_draw_is_basic: bool,
) -> int:
    """Number of singleton-Dialga placements keeping it available in hand.

    If two or more non-Radiant Basics appear in the opening, any one can be
    Dialga while another starts Active. If only one appears and it is Dialga,
    that Dialga must start Active and cannot be discarded from hand.

    If a further Basic is the first draw, it may instead be Dialga; the
    initially established eligible Active already exists.
    """
    return (
        (opening_basics if opening_basics >= 2 else 0)
        + int(first_draw_is_basic and opening_basics >= 1)
    )


def exact_increment(
    caps: tuple[int, ...] = COUNTS,
    *,
    opening_size: int = 7,
    prize_count: int = 6,
) -> Fraction:
    """Additional success over the >=2 Psychic Energy or spare-Treasure guard."""
    deck_size = sum(caps)
    basic_slots = caps[3]
    if basic_slots == 0:
        raise ValueError("Dialga requires an other-Basic category")
    valid_opening_ways = (
        comb(deck_size, opening_size)
        - comb(deck_size - caps[0] - caps[3], opening_size)
    )
    denominator = (
        valid_opening_ways
        * comb(deck_size - opening_size, prize_count)
        * (deck_size - opening_size - prize_count)
    )
    numerator_scaled = 0

    for opening in allocations(opening_size, caps):
        if opening[0] + opening[3] == 0:
            continue
        opening_weight = prod(
            comb(cap, count) for cap, count in zip(caps, opening)
        )
        after_opening = tuple(c - n for c, n in zip(caps, opening))
        for prizes in allocations(prize_count, after_opening):
            prize_weight = opening_weight * prod(
                comb(cap, count)
                for cap, count in zip(after_opening, prizes)
            )
            after_prizes = tuple(
                c - n for c, n in zip(after_opening, prizes)
            )
            for draw, available in enumerate(after_prizes):
                if available == 0:
                    continue
                flags = success_flags(opening, prizes, draw, caps)
                if flags is None:
                    continue
                if (
                    not flags["treasure_free"]
                    or flags["treasure_energy2_spare"]
                ):
                    continue
                possible_positions = eligible_dialga_positions(
                    opening[3], draw == 3
                )
                assert 0 <= possible_positions <= basic_slots
                numerator_scaled += prize_weight * available * possible_positions

    # Every possible position of the sole Dialga among the B physical
    # copies is equally likely conditional on grouped B-category counts.
    return Fraction(numerator_scaled, basic_slots * denominator)


def labeled_oracle(caps: tuple[int, ...]) -> tuple[Fraction, int]:
    """Independent physical singleton-position test for a toy deck.

    Each physical copy receives a stable index, and the first other-Basic
    physical copy is assigned Dialga identity. All physical deals are
    enumerated directly without the exchangeability formula.
    """
    physical = tuple(
        category for category, quantity in enumerate(caps)
        for _copy in range(quantity)
    )
    dialga_id = physical.index(3)
    accepted = 0
    successful = 0
    for opened in combinations(range(len(physical)), 3):
        opening = tuple(
            sum(physical[index] == category for index in opened)
            for category in range(len(caps))
        )
        remaining = tuple(
            index for index in range(len(physical)) if index not in opened
        )
        for prized in combinations(remaining, 2):
            prizes = tuple(
                sum(physical[index] == category for index in prized)
                for category in range(len(caps))
            )
            for drawn in remaining:
                if drawn in prized:
                    continue
                flags = success_flags(
                    opening, prizes, physical[drawn], caps
                )
                if flags is None:
                    continue
                accepted += 1
                if (
                    flags["treasure_free"]
                    and not flags["treasure_energy2_spare"]
                    and (
                        (dialga_id in opened and opening[3] >= 2)
                        or (dialga_id == drawn and opening[3] >= 1)
                    )
                ):
                    successful += 1
    return Fraction(successful, accepted), accepted


def run() -> dict[str, Fraction]:
    assert POKEMON["Dialga-GX"] == 1
    assert PRINT_IDS["Dialga-GX"] == "sm5-100"
    root = Path(__file__).resolve().parents[1]
    cards = json.loads(
        (root / "resources" / "cards" / "en" / "sm5.json").read_text(
            encoding="utf-8"
        )
    )
    dialga = next(card for card in cards if card["id"] == "sm5-100")
    assert "Basic" in dialga["subtypes"]
    assert "Dragon" in dialga["types"]
    assert any(
        attack["name"] == "Timeless-GX"
        for attack in dialga["attacks"]
    )

    # Vary Basic count in the independent labeled oracle, including
    # the degenerate one-Basic category where Dialga can only start Active.
    for toy, expected_worlds in [
        ((1, 2, 2, 1, 2, 2), 6720),
        ((1, 2, 2, 2, 2, 2), 18312),
        ((1, 2, 2, 3, 2, 2), 41328),
    ]:
        labeled, worlds = labeled_oracle(toy)
        assert worlds == expected_worlds
        grouped = exact_increment(
            toy, opening_size=3, prize_count=2
        )
        assert labeled == grouped, (toy, labeled, grouped)

    increment = exact_increment()
    assert increment == Fraction(84865653, 4090794400)
    baseline = payment_exact()
    strict = baseline["treasure_energy2_spare"]
    direct = baseline["direct"]
    extended = strict + increment
    assert extended == Fraction(50480630621, 278174019200)
    total = extended + direct
    assert total == Fraction(335644558019, 1112696076800)
    return {
        "baseline_direct": direct,
        "baseline_strict_treasure": strict,
        "dialga_payload_increment": increment,
        "extended_treasure": extended,
        "extended_total": total,
    }


if __name__ == "__main__":
    results = run()
    for key, value in results.items():
        print(f"{key}: {float(value):.9%} [{value}]")
    print("Dialga discard identity and physical oracle passed")
