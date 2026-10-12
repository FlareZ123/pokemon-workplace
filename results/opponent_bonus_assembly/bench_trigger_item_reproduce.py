"""Independent labeled opening, Prize, bonus oracle for trigger-role dual search."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_bench_trigger_items import TwoBenchTriggerItems


def physical_oracle(model: TwoBenchTriggerItems, bonus: int, *,
                    require_bench_triggers: bool, ignore_payment: bool,
                    ignore_prizes: bool) -> Fraction:
    physical = (
        ["other"] * model.other_basics + ["a", "b"]
        + ["source"] * model.item_sources
        + ["safe"] * model.safe_fodder
        + ["filler"] * model.capacities[-1]
    )
    good = total = 0
    for opening in combinations(range(model.deck_size), model.opening_size):
        starter = [physical[i] for i in opening]
        if not any(c in {"other", "a", "b"} for c in starter):
            continue
        outside = set(range(model.deck_size)) - set(opening)
        for prizes in combinations(sorted(outside), model.prizes):
            remaining = outside - set(prizes)
            for bonus_indices in combinations(sorted(remaining), bonus):
                hand = [physical[i] for i in (*opening, *bonus_indices)]
                missing = int("a" not in hand) + int("b" not in hand)
                has_start = ("other" in starter if require_bench_triggers
                             else True)
                feasible = (
                    has_start
                    and hand.count("source") >= missing
                    and (ignore_payment or hand.count("safe") >=
                         missing * model.payment_per_item)
                    and (ignore_prizes or all(
                        physical[i] not in {"a", "b"}
                        for i in prizes
                    ))
                )
                good += feasible
                total += 1
    return Fraction(good, total)


def test_card_text() -> None:
    root = Path(__file__).resolve().parents[2]
    for path, identifier, ability in (
        ("swsh12pt5", "swsh12pt5-105", "Climactic Gate"),
        ("swsh9", "swsh9-40", "Luminous Sign"),
    ):
        cards = json.loads((root / "resources" / "cards" / "en" /
                            f"{path}.json").read_text(encoding="utf-8"))
        match = next(card for card in cards if card["id"] == identifier)
        assert match["legalities"]["expanded"] == "Legal"
        assert "Basic" in match["subtypes"]
        assert any(
            a["name"] == ability
            and "from your hand onto your Bench during your turn" in a["text"]
            for a in match["abilities"]
        )


def test_small() -> None:
    models = (
        TwoBenchTriggerItems(9, 3, 1, 1, 2, 2, 1),
        TwoBenchTriggerItems(10, 3, 2, 2, 2, 1, 1),
    )
    for model in models:
        for bonus in (0, 1, 2):
            for require in (False, True):
                for payment in (False, True):
                    for prizes in (False, True):
                        exact = model.probability(
                            bonus, require_bench_triggers=require,
                            ignore_payment=payment, ignore_prizes=prizes,
                        )
                        enumeration = physical_oracle(
                            model, bonus, require_bench_triggers=require,
                            ignore_payment=payment, ignore_prizes=prizes,
                        )
                        assert exact == enumeration, (
                            model, bonus, require, payment, prizes,
                            exact, enumeration,
                        )


def benchmark() -> None:
    print("other Basics | bonus | naive | role+payment+prize | role penalty (pp)")
    for starters in (0, 1, 3, 5, 11, 19):
        model = TwoBenchTriggerItems(other_basics=starters)
        for bonus in (0, 4, 8):
            data = model.ablation(bonus)
            assert data["physical"] <= data["naive"]
            assert data["physical"] <= data["role_and_payment"]
            assert data["physical"] <= data["role_and_prizes"]
            assert data["role_and_payment"] <= data["role_only"]
            assert data["role_and_prizes"] <= data["role_only"]
            penalty = 100 * float(data["naive"] - data["physical"])
            print(f"{starters:12d} | {bonus:5d} | "
                  f"{float(data['naive']):.8%} | "
                  f"{float(data['physical']):.8%} | {penalty:.8f}")
        assert model.probability(0) <= model.probability(4) <= model.probability(8)
    assert TwoBenchTriggerItems(other_basics=0).probability(8) == 0


if __name__ == "__main__":
    test_card_text()
    test_small()
    benchmark()
    print("PASS: exact active-role + payments + Prizes from labeled oracles")
