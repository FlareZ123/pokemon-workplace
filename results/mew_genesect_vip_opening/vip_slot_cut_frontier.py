"""First-turn Mew/Genesect fourth-VIP deck-slot cut sensitivity.

Compare source-access under five exact-print paper Expanded 60-card variants.
The goal is Basic board assembly, so lost tactical effects or Mew VMAX
evolution access are outside this model's objective and must be evaluated.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from results.competitive_deck_baselines.mew_genesect_reproduce import (
    ENERGY, POKEMON, PRINT_IDS, TRAINERS,
)
from results.mew_genesect_vip_opening.combined_mail_ball_frontier import (
    exact, exact_counts, physical_toy_oracle,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry


# Each tuple is (name, +VIP delta, Trainer cut, count of Mail, Quick, Ultra).
VARIANTS = (
    ("published 3-VIP", 0, None, 3, 4, 4),
    ("4-VIP / minus Red", 1, "Special Red Card", 3, 4, 4),
    ("4-VIP / minus Mail", 1, "Trainers' Mail", 2, 4, 4),
    ("4-VIP / minus Quick", 1, "Quick Ball", 3, 3, 4),
    ("4-VIP / minus Ultra", 1, "Ultra Ball", 3, 4, 3),
    ("4-VIP / minus Karen", 1, "Karen", 3, 4, 4),
)


def deck_entries(variant: tuple) -> list[DeckEntry]:
    _, extra_vip, removed, *_ = variant
    copy_counts = {**POKEMON, **TRAINERS, **ENERGY}
    if extra_vip:
        copy_counts["Battle VIP Pass"] += 1
        assert removed is not None
        copy_counts[removed] -= 1
    assert sum(copy_counts.values()) == 60
    assert all(1 <= n <= 4 for n in copy_counts.values())
    return [DeckEntry(PRINT_IDS[name], n) for name, n in copy_counts.items()]


def access(variant: tuple, *, d: int, goal: int):
    _, extra_vip, _, mail, quick, ultra = variant
    vip = 3 + extra_vip
    target_basics = (4, 4, 3)
    fixed = sum(target_basics) + vip + mail + quick + ultra + d
    cards = (*target_basics, vip, mail, quick, ultra, d, 60 - fixed)
    assert all(x >= 0 for x in cards)
    return exact_counts(
        cards, goal, hand_size=7, prize_size=6, look_size=4
    )


def verify_prints() -> None:
    resources = Path(__file__).resolve().parents[2] / "resources"
    for row in VARIANTS:
        proof = adjudicate_deck(
            deck_entries(row), resources, as_of=date(2026, 10, 12)
        )
        assert proof.construction.valid, (row[0], proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (
            row[0], proof.disposition
        )
        print(f"{row[0]}: 60 exact-print cards, eligible paper Expanded")


def self_test() -> None:
    # This is a joint paid Ball -> shuffled Mail -> VIP model; test alternate
    # source copy counts against independent physical toy-card labeling.
    for toy in (
        (1, 2, 1, 2, 1, 1, 1, 1, 0),
        (1, 2, 1, 2, 0, 1, 1, 1, 1),
        (1, 2, 1, 2, 1, 0, 1, 1, 1),
        (1, 2, 1, 2, 1, 1, 0, 1, 1),
    ):
        assert sum(toy) == 10
        for goal in (1, 2):
            grouped = exact_counts(
                toy, goal, hand_size=3, prize_size=2, look_size=2
            )
            oracle, worlds = physical_toy_oracle(toy, goal)
            assert grouped == oracle and worlds == 10500
            print(f"Toy={toy} goal={goal}: physical oracle PASS")

    for goal in (2, 3):
        for d in (6, 12):
            values = {
                row[0]: access(row, d=d, goal=goal) for row in VARIANTS
            }
            assert values["published 3-VIP"] == exact(3, d, goal)
            assert values["4-VIP / minus Red"] == exact(4, d, goal)
            assert values["4-VIP / minus Karen"] == values[
                "4-VIP / minus Red"
            ]
            for row in VARIANTS[2:]:
                assert values[row[0]] <= values["4-VIP / minus Red"]
            for name, probability in values.items():
                print(
                    f"Mew + {goal} Genesect, D={d}, {name}: "
                    f"{float(probability):.9%}"
                )
    verify_prints()


if __name__ == "__main__":
    self_test()
