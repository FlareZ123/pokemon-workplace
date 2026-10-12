"""Exact natural turn-one Celestial Roar readiness and revealed Double Dragon risk.

All numerator events are unconditional over uniformly shuffled 60 cards;
divide by 'basic_opening' to condition on a game with a valid Basic opening.
The independent labeled physical oracle explicitly deals all Prize cards.
No trainer searches, opponent draws, tactical policy or hand discards.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from json import loads
from math import comb, prod
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DECK = ROOT / "results" / "competitive_deck_baselines" / "regidrago_haruku_2026.json"
CARDS = ROOT / "resources" / "cards" / "en"


def source_counts() -> tuple[int, int, int, int, int]:
    entries = loads(DECK.read_text(encoding="utf-8"))["cards"]
    assert sum(entry["quantity"] for entry in entries) == 60
    sets: dict[str, dict[str, dict]] = {}
    basics = 0
    for entry in entries:
        printed_id = entry["print_id"]
        set_id = printed_id.rsplit("-", 1)[0]
        if set_id not in sets:
            source = loads((CARDS / f"{set_id}.json").read_text(encoding="utf-8"))
            sets[set_id] = {card["id"]: card for card in source}
        physical = sets[set_id][printed_id]
        assert physical["name"] == entry["name"]
        if entry["category"] == "Pokémon" and "Basic" in physical.get("subtypes", []):
            basics += entry["quantity"]
    counts = {entry["name"]: entry["quantity"] for entry in entries}
    reg = counts["Regidrago V"]
    special = counts["Double Dragon Energy"]
    basic_energy = counts["Grass Energy"] + counts["Fire Energy"]
    assert (basics, reg, special, basic_energy) == (15, 4, 4, 6)
    return (reg, basics - reg, special, basic_energy, 60 - basics - special - basic_energy)


def exact_groups(
    quantities: tuple[int, int, int, int, int],
    opening_size: int,
    reveal_size: int,
) -> dict[str, Fraction]:
    """Classes: Regidrago V, other Basic, Double Dragon, Basic Energy, filler."""
    total = sum(quantities)
    denom = comb(total, opening_size)
    outcomes = {key: Fraction(0) for key in ("basic_opening", "ready", "affected")}
    for opening in product(*(range(min(opening_size, n) + 1) for n in quantities)):
        if sum(opening) != opening_size:
            continue
        probability = Fraction(
            prod(comb(n, seen) for n, seen in zip(quantities, opening)), denom
        )
        if opening[0] + opening[1]:
            outcomes["basic_opening"] += probability
        if opening[0] == 0:
            continue
        # The initial seven provides an Active Regidrago, with no switch required.
        for category, remaining_count in enumerate(quantities):
            after_open = remaining_count - opening[category]
            if not after_open:
                continue
            # Prize identities have been summed out. A designated first draw
            # is exchangeable among all cards not in the opening seven.
            first_draw = probability * Fraction(after_open, total - opening_size)
            has_attachable_energy = opening[2] + opening[3] > 0 or category in (2, 3)
            if not has_attachable_energy:
                continue
            outcomes["ready"] += first_draw
            remaining = total - opening_size - 1
            double_dragon_left = quantities[2] - opening[2] - int(category == 2)
            affected_reveal = 1 - Fraction(
                comb(remaining - double_dragon_left, reveal_size),
                comb(remaining, reveal_size),
            )
            outcomes["affected"] += first_draw * affected_reveal
    return outcomes


def labeled_physical_oracle(
    quantities: tuple[int, int, int, int, int],
    opening_size: int,
    prize_count: int,
    reveal_size: int,
) -> tuple[dict[str, Fraction], int]:
    """Independently enumerate distinct physical cards and explicit Prize sets."""
    cards = [(category, physical) for category, amount in enumerate(quantities)
             for physical in range(amount)]
    worlds = 0
    events = {key: 0 for key in ("basic_opening", "ready", "affected")}
    for opener in combinations(cards, opening_size):
        opener_set = set(opener)
        remaining = [card for card in cards if card not in opener_set]
        basic = any(card[0] in (0, 1) for card in opener)
        reg = any(card[0] == 0 for card in opener)
        energy = any(card[0] in (2, 3) for card in opener)
        for prizes in combinations(remaining, prize_count):
            prize_set = set(prizes)
            post_prize = [card for card in remaining if card not in prize_set]
            for first_draw in post_prize:
                deck_after_draw = [card for card in post_prize if card != first_draw]
                for reveal in combinations(deck_after_draw, reveal_size):
                    worlds += 1
                    events["basic_opening"] += basic
                    ready = reg and (energy or first_draw[0] in (2, 3))
                    events["ready"] += ready
                    events["affected"] += ready and any(card[0] == 2 for card in reveal)
    return {key: Fraction(count, worlds) for key, count in events.items()}, worlds


def main() -> None:
    real = exact_groups(source_counts(), opening_size=7, reveal_size=3)
    assert real == {
        "basic_opening": Fraction(172135, 195054),
        "ready": Fraction(1561585, 5168931),
        "affected": Fraction(315139423777, 5654552067450),
    }
    for toy in ((2, 2, 1, 2, 3), (1, 3, 2, 1, 3)):
        grouped = exact_groups(toy, opening_size=3, reveal_size=3)
        physical, worlds = labeled_physical_oracle(
            toy, opening_size=3, prize_count=2, reveal_size=3
        )
        assert grouped == physical, (toy, grouped, physical)
        print(f"toy={toy}, physical worlds={worlds}, oracle agreement=PASS")
    print(f"accepted Basic opener: {float(real['basic_opening']):.9%}")
    print(f"natural immediate Celestial Roar ready, unconditional: {float(real['ready']):.9%}")
    print(f"natural immediate Celestial Roar ready, Basic-valid: {float(real['ready']/real['basic_opening']):.9%}")
    print(f"ready plus revealed Double Dragon, unconditional: {float(real['affected']):.9%}")
    print(f"ready plus revealed Double Dragon, Basic-valid: {float(real['affected']/real['basic_opening']):.9%}")
    print(f"reveals Double Dragon given natural ready: {float(real['affected']/real['ready']):.9%}")
    print("PASS: printed Regidrago 60 plus independent explicit-Prize physical oracle")


if __name__ == "__main__":
    main()
