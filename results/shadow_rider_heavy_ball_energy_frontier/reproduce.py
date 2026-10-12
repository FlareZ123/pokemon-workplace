"""SFT: exact Heavy Ball versus Psychic Energy deck swap and physical oracle."""

from __future__ import annotations

from collections import Counter
from datetime import date
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    ENERGY, POKEMON, PRINT_IDS, TRAINERS,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry
from tools.shadow_rider_ball_energy_frontier import (
    energy_reserve_probability, energy_swap_frontier,
    launch_filler_hand_buckets, source_counts,
)
from tools.shadow_rider_heavy_ball_launch import classify, exact, launch_probability


def physical_toy_oracle() -> None:
    """Enumerate explicitly designated Energy cards among physical filler."""

    for heavy in range(3):
        caps = (1, 2, 1, heavy, 2, 4 - heavy)
        energy_count = 2 - heavy
        cards = tuple(
            (card_kind, copy)
            for card_kind, count in enumerate(caps)
            for copy in range(count)
        )
        accepted = 0
        launches = 0
        retained_energy = 0

        for opening in combinations(range(len(cards)), 3):
            by_open = Counter(cards[index][0] for index in opening)
            if not (by_open[0] + by_open[4]):
                continue
            rest = [index for index in range(len(cards)) if index not in opening]
            opened = tuple(by_open[i] for i in range(6))
            for prizes in combinations(rest, 2):
                by_prize = Counter(cards[index][0] for index in prizes)
                pr = tuple(by_prize[i] for i in range(6))
                for draw in rest:
                    if draw in prizes:
                        continue
                    accepted += 1
                    if not classify(opened, pr, cards[draw][0], caps).endswith("_2"):
                        continue
                    launches += 1
                    if any(
                        cards[index][0] == 5 and cards[index][1] < energy_count
                        for index in (*opening, draw)
                    ):
                        retained_energy += 1

        buckets = launch_filler_hand_buckets(
            caps, opening_size=3, prize_count=2
        )
        assert accepted == 8925
        assert sum(buckets.values(), Fraction(0)) == Fraction(launches, accepted)
        assert energy_reserve_probability(
            buckets, caps[5], energy_count
        ) == Fraction(retained_energy, accepted)
        assert launch_probability(
            exact(caps, opening_size=3, prize_count=2)
        ) == Fraction(launches, accepted)

    print("Independent physical 8,925-world toy oracle matches H0, H1, H2")
    print("Joint launch and physically held designated Energy agrees exactly")


def legal_variants() -> None:
    """Print-verified 60-card variants change only Heavy Ball and Psychic Energy."""

    root = Path(__file__).resolve().parents[2] / "resources"
    source = {**POKEMON, **TRAINERS, **ENERGY}
    assert source["Hisuian Heavy Ball"] == 1
    assert source["Psychic Energy"] == 11
    for heavy in range(5):
        current = dict(source)
        current["Hisuian Heavy Ball"] = heavy
        current["Psychic Energy"] = 12 - heavy
        entries = tuple(
            DeckEntry(PRINT_IDS[name], quantity)
            for name, quantity in current.items()
            if quantity
        )
        assert sum(row.quantity for row in entries) == 60
        assert current["Hisuian Heavy Ball"] <= 4
        proof = adjudicate_deck(entries, root, as_of=date(2026, 10, 12))
        assert proof.disposition == "eligible_snapshot", (
            heavy, proof.disposition
        )


def main() -> None:
    legal_variants()
    physical_toy_oracle()

    rows = energy_swap_frontier()
    assert len(rows) == 5
    assert rows[1][0:2] == (1, 11)
    assert rows[1][2] == launch_probability(exact())
    expected = (
        (
            Fraction(486238865957, 1112696076800),
            Fraction(4340526515197, 12239656844800),
        ),
        (
            Fraction(22001000560963, 48958627379200),
            Fraction(3116851058407, 8901568614400),
        ),
        (
            Fraction(402470087603, 874261203200),
            Fraction(597704056401, 1748522406400),
        ),
        (
            Fraction(18410563046033, 39166901903360),
            Fraction(9219689847567, 27976358502400),
        ),
        (
            Fraction(5857955864221, 12239656844800),
            Fraction(3832619242037, 12239656844800),
        ),
    )

    previous_launch = Fraction(-1)
    previous_energy = Fraction(2)
    for index, (heavy, energy, launch, joint) in enumerate(rows):
        assert (launch, joint) == expected[index]
        assert heavy == index and energy == 12 - index
        assert 0 < joint < launch < 1
        assert launch > previous_launch
        assert joint < previous_energy
        previous_launch, previous_energy = launch, joint
        print(f"H={heavy} Psychic={energy:2} dual-VMAX={float(launch):.12%}"
              f" dual-VMAX+heldEnergy={float(joint):.12%}")

    assert rows[2][2] > rows[1][2]
    assert rows[2][3] < rows[1][3]
    print("Five 60-card variants have conservative Expanded snapshot legality")
    print("H1->H2 improves two-VMAX launch but worsens the Energy-hand joint event")


if __name__ == "__main__":
    main()
