"""SFT: precise Mysterious Treasure payment opportunity and physical toy oracle."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    ENERGY, POKEMON, TRAINERS,
)
from results.shadow_rider_radiant_launch.reproduce import exact as prior_exact
from tools.shadow_rider_heavy_ball_launch import (
    COUNTS, baseline_without_heavy_route, classify, exact
)
from tools.shadow_rider_treasure_cost_sensitivity import (
    acceptable_discard_probability,
    treasure_two_vmax_hand_buckets,
)


def physical_toy_oracle() -> None:
    """Count labeled toy openings, Prize subsets and draws independently."""

    caps = (1, 2, 1, 1, 2, 3)
    cards = tuple(
        (category, copy)
        for category, amount in enumerate(caps)
        for copy in range(amount)
    )
    n = len(cards)
    events = Counter()
    den = 0
    for opening in combinations(range(n), 3):
        by_open = Counter(cards[index][0] for index in opening)
        if by_open[0] + by_open[4] == 0:
            continue
        remaining = [index for index in range(n) if index not in opening]
        for prizes in combinations(remaining, 2):
            by_prize = Counter(cards[index][0] for index in prizes)
            for drawn in remaining:
                if drawn in prizes:
                    continue
                den += 1
                if classify(
                    tuple(by_open[i] for i in range(6)),
                    tuple(by_prize[i] for i in range(6)),
                    cards[drawn][0], caps,
                ) != "treasure_2":
                    continue
                hand = tuple(opening) + (drawn,)
                treasures_held = sum(cards[index][0] == 2 for index in hand)
                filler_copies = frozenset(
                    cards[index][1]
                    for index in hand if cards[index][0] == 5
                )
                for safe in range(caps[5] + 1):
                    eligible = any(copy < safe for copy in filler_copies)
                    events[(safe, False)] += int(eligible)
                    events[(safe, True)] += int(eligible or treasures_held >= 2)

    grouped = treasure_two_vmax_hand_buckets(
        caps, opening_size=3, prize_count=2, first_turn_draw=True,
    )
    assert sum(grouped.values()) == exact(
        caps, opening_size=3, prize_count=2
    )["treasure_2"]
    for safe in range(caps[5] + 1):
        for spare in (False, True):
            predicted = acceptable_discard_probability(
                grouped, safe_filler_copies=safe,
                total_filler_copies=caps[5],
                allow_spare_treasure=spare,
            )
            observed = Fraction(events[(safe, spare)], den)
            assert predicted == observed, (safe, spare, predicted, observed)

    print(f"Independent labeled toy oracle matched {den} physical draw worlds")
    print("Exact valid-payment probabilities matched for all 4 safe-copy counts")
    print("Both payment policies (only safe filler / safe filler or spare Treasure) verified")


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    cards = json.loads(
        (root / "resources" / "cards" / "en" / "sm6.json").read_text(encoding="utf-8")
    )
    treasure = next(row for row in cards if row["id"] == "sm6-113")
    assert "Discard a card from your hand. If you do" in treasure["rules"][0]
    assert COUNTS == (1, 4, 4, 1, 13, 37)
    assert sum(POKEMON.values()) + sum(TRAINERS.values()) + sum(ENERGY.values()) == 60
    assert TRAINERS["Mysterious Treasure"] == 4
    assert TRAINERS["Hisuian Heavy Ball"] == 1
    assert ENERGY["Psychic Energy"] == 11

    physical_toy_oracle()
    buckets = treasure_two_vmax_hand_buckets()
    old = prior_exact()
    extended = exact()
    assert sum(buckets.values()) == extended["treasure_2"] == old["treasure_2"]
    assert len(buckets) == 23

    # Hypothetical safe-discard counts are chosen from the 37-card broad
    # filler pool, without privileging future Prize-card knowledge.
    expected = {
        0: (Fraction(0), Fraction(2112156999, 37401548800)),
        4: (Fraction(283499660117, 2225392153600),
            Fraction(91234199429, 556348038400)),
        11: (Fraction(402091494907, 1618467020800),
             Fraction(117457006901, 445078430720)),
        37: (Fraction(20138131229, 63582632960),
             Fraction(719333303, 2270808320)),
    }
    previous_with_spares = Fraction(-1)
    for safe_count in range(38):
        strict = acceptable_discard_probability(
            buckets, safe_filler_copies=safe_count,
        )
        spare = acceptable_discard_probability(
            buckets, safe_filler_copies=safe_count,
            allow_spare_treasure=True,
        )
        assert 0 <= strict <= spare <= extended["treasure_2"]
        assert spare >= previous_with_spares
        previous_with_spares = spare
        if safe_count in expected:
            assert (strict, spare) == expected[safe_count]

    # The 11 Basic Psychic Energy in the list are a *hypothetical* cost
    # family. It might be strategically costly to discard one.
    energy_only = acceptable_discard_probability(
        buckets, safe_filler_copies=11,
    )
    energy_or_spare = acceptable_discard_probability(
        buckets, safe_filler_copies=11, allow_spare_treasure=True,
    )
    print("Exact actual-deck Mysterious Treasure payment sensitivity")
    print(f"Unrestricted Treasure dual-VMAX route: {float(extended['treasure_2']):.12%}")
    print(f"Only Psychic Energy accepted as discard: {float(energy_only):.12%}")
    print(f"Psychic Energy or spare Treasure: {float(energy_or_spare):.12%}")
    for k, (strict, spare) in expected.items():
        print(f"safe filler copies={k:2} strict={float(strict):.12%}"
              f" spare-allowed={float(spare):.12%}")
    print("Real-list prior exact two-route analysis and labeled physical oracle agree")


if __name__ == "__main__":
    main()
