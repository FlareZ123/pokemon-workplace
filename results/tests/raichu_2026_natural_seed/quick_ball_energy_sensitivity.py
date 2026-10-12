"""SFT: source-attested Energy discard-policy sensitivity for 2026 Aichi Raichu.

Prizes, first seven, and first draw are exact physical-zone class counts.
Energy-only payments are a declared preservation policy, not inferred DCI.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from itertools import product

from quick_ball_upper import search
from reproduce import MANIFEST, choose, source_card, two_evolution_bases, validate_sources

# Voltorb, Pikachu, Ditto, Quick Ball, other Basic, 12 Energy, remaining 31.
POP = (2, 1, 1, 4, 9, 12, 31)
BASIC_TYPES = (0, 1, 2, 4)
POLICIES = ("all_cards", "energy_or_quickball", "energy_only")


def sample_space():
    """Enumerate the seven, six-Prize set, and first natural draw."""
    for prefix in product(*(range(min(7, n) + 1) for n in POP[:-1])):
        last = 7 - sum(prefix)
        if not 0 <= last <= POP[-1]:
            continue
        seven = (*prefix, last)
        if not any(seven[index] for index in BASIC_TYPES):
            continue
        hand_weight = math.prod(choose(n, k) for n, k in zip(POP, seven))
        remaining = tuple(n - k for n, k in zip(POP, seven))
        for prize_prefix in product(
            *(range(min(6, n) + 1) for n in remaining[:-1])
        ):
            prize_last = 6 - sum(prize_prefix)
            if not 0 <= prize_last <= remaining[-1]:
                continue
            prizes = (*prize_prefix, prize_last)
            prize_weight = math.prod(
                choose(n, k) for n, k in zip(remaining, prizes)
            )
            for drawn in range(len(POP)):
                count = POP[drawn] - seven[drawn] - prizes[drawn]
                if count:
                    yield seven, prizes, drawn, hand_weight * prize_weight * count


def actor_state(
    seven: tuple[int, ...], prizes: tuple[int, ...],
    drawn: int, active: int,
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    hand = list(seven)
    hand[active] -= 1
    hand[drawn] += 1
    board = [0, 0, 0]
    if active < 3:
        board[active] += 1
    deck = tuple(
        n - held - prize - (index == drawn)
        for index, (n, held, prize) in enumerate(zip(POP, seven, prizes))
    )
    assert sum(hand) == 7 and sum(deck) == 46
    return tuple(hand), deck, tuple(board)


def main() -> None:
    validate_sources()
    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))["cards"]
    quantities = {row["name"]: row["quantity"] for row in rows}
    assert POP == (
        quantities["Voltorb"], quantities["Pikachu"], quantities["Ditto ◇"],
        quantities["Quick Ball"], 9, 12, 31,
    )
    energies = {
        row["name"]: row["quantity"]
        for row in rows if row["category"] == "Energy"
    }
    assert energies == {
        "Reversal Energy": 4,
        "Counter Energy": 4,
        "Unit Energy LightningPsychicMetal": 4,
    }
    assert "Basic Pokémon" in source_card("swsh1-179")["rules"][1]

    denominator = natural = 0
    success = {policy: 0 for policy in POLICIES}
    scenarios = 0
    for seven, prizes, drawn, weight in sample_space():
        scenarios += 1
        denominator += weight
        observed = list(seven)
        observed[drawn] += 1
        if two_evolution_bases(*observed[:3]):
            natural += weight
        for policy in POLICIES:
            if any(
                search(*actor_state(seven, prizes, drawn, active), policy)
                for active in BASIC_TYPES if seven[active]
            ):
                success[policy] += weight

    assert denominator == (choose(60, 7) - choose(47, 7)) * choose(53, 6) * 47
    assert scenarios == 799953
    assert Fraction(natural, denominator) == Fraction(814128, 9797437)
    assert Fraction(success["all_cards"], denominator) == Fraction(
        80313436404203, 265089546832110
    )
    assert Fraction(success["energy_or_quickball"], denominator) == Fraction(
        463976309712683, 1855626827824770
    )
    assert Fraction(success["energy_only"], denominator) == Fraction(
        4558447450312, 18934967630865
    )
    assert (
        success["all_cards"] > success["energy_or_quickball"]
        > success["energy_only"] > natural
    )

    print(json.dumps({
        "weighted_zone_classes": scenarios,
        "natural_probability": natural / denominator,
        "quick_ball_unrestricted_probability": success["all_cards"] / denominator,
        "quick_ball_energy_or_other_quickball_probability": (
            success["energy_or_quickball"] / denominator
        ),
        "quick_ball_energy_only_probability": (
            success["energy_only"] / denominator
        ),
        "strict_energy_only_fraction": str(
            Fraction(success["energy_only"], denominator)
        ),
        "scope": "Exact hand/Prize/draw and card-specific discard policy; "
                 "no other setup effects or win rate",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
