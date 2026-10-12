"""Independent physical-label reproduction of two-turn Guzma/VS Seeker line."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations
import json
from pathlib import Path

from tools.regidrago_double_gust_access import Turn2, chain
from results.aichi_regidrago_gust_deadlines.reproduce import validate_prints


SCENARIOS = {
    "unlocked, not behind": Turn2(),
    "unlocked, behind": Turn2(behind=True),
    "Item locked, behind": Turn2(item=False, behind=True),
    "Supporter locked, behind": Turn2(supporter=False, behind=True),
    "Supporter locked, tied": Turn2(supporter=False),
    "Item locked, tied": Turn2(item=False),
}


def physical_oracle(basics: int, guzma: int, seekers: int, prime: int,
                    counter: int, turn2: Turn2, total: int = 9,
                    hand_size: int = 3, prizes: int = 2
                    ) -> tuple[Fraction, Fraction]:
    cards = (["B"] * basics + ["G"] * guzma + ["S"] * seekers +
             ["P"] * prime + ["C"] * counter +
             ["F"] * (total - basics - guzma - seekers - prime - counter))
    observations = [0, 0, 0]
    ids = set(range(total))
    for opening in combinations(range(total), hand_size):
        hand = [cards[i] for i in opening]
        if "B" not in hand:
            continue
        unused = ids - set(opening)
        for prized in combinations(sorted(unused), prizes):
            deck = unused - set(prized)
            for draw1, draw2 in permutations(sorted(deck), 2):
                observations[0] += 1
                hand1 = hand + [cards[draw1]]
                if "G" not in hand1:
                    continue
                observations[1] += 1
                hand1.remove("G")  # Played the original Supporter on T1.
                hand1.append(cards[draw2])
                source = (
                    (turn2.supporter and
                     ("G" in hand1 or (turn2.item and "S" in hand1))) or
                    (turn2.item and
                     ("P" in hand1 or (turn2.behind and "C" in hand1)))
                )
                observations[2] += bool(source)
    return (Fraction(observations[1], observations[0]),
            Fraction(observations[2], observations[0]))


def verify() -> None:
    validate_prints()
    root = Path(__file__).resolve().parents[2]
    raw = json.loads((root / "resources" / "cards" / "en" / "xy6.json")
                     .read_text(encoding="utf-8"))
    seeker = next(c for c in raw if c["id"] == "xy6-110")
    assert seeker["name"] == "VS Seeker"
    assert "Item" in seeker["subtypes"]
    assert "Supporter card from your discard pile" in seeker["rules"][0]

    for guzma, seeker_count, prime, counter in (
        (2, 2, 1, 0), (1, 2, 1, 1), (2, 1, 0, 1), (1, 1, 1, 0)
    ):
        for condition in (
            Turn2(), Turn2(behind=True), Turn2(item=False, behind=True),
            Turn2(supporter=False, behind=True)
        ):
            exact = chain(2, guzma, seeker_count, prime, counter,
                          condition, total=9, hand_size=3, prize_count=2)
            oracle = physical_oracle(2, guzma, seeker_count, prime,
                                     counter, condition)
            assert exact == oracle, (guzma, seeker_count, condition, exact, oracle)
    print("PASS: 16 independent labeled toy hands + Prizes + two ordered draws")
    first_orig = first_swap = None
    for label, condition in SCENARIOS.items():
        original = chain(15, 2, 3, 1, 0, condition)
        variant = chain(15, 1, 3, 1, 1, condition)
        if first_orig is None:
            first_orig, first_swap = original[0], variant[0]
        assert original[0] == first_orig and variant[0] == first_swap
        print(
            f"{label}: published T1 Guzma={float(original[0]*100):.6f}% "
            f"double gust={float(original[1]*100):.6f}% "
            f"(conditional={float(original[1]/original[0]*100):.6f}%); "
            f"swap T1 Guzma={float(variant[0]*100):.6f}% "
            f"double gust={float(variant[1]*100):.6f}% "
            f"(conditional={float(variant[1]/variant[0]*100):.6f}%); "
            f"delta unconditional={float((variant[1]-original[1])*100):+.6f} pp"
        )
    assert original[0] > variant[0]
    print("PASS: exact 60-card tandem gust probabilities and card-source proof")


if __name__ == "__main__":
    verify()
