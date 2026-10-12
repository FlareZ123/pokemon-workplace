"""Print-grounded Aichi Regidrago swap proof and independent physical oracles."""
from __future__ import annotations

from collections import Counter
from datetime import date
from fractions import Fraction
from itertools import combinations, permutations
import json
from pathlib import Path

from tools.aichi_regidrago_gust_deadlines import Window, access
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records


SCENARIOS = {
    "open, tied throughout": (Window(), Window()),
    "open, behind second": (Window(), Window(behind=True)),
    "Item locked on second": (Window(), Window(item=False, behind=True)),
    "Supporter locked on second": (Window(), Window(supporter=False, behind=True)),
    "Item locked both": (Window(item=False), Window(item=False, behind=True)),
    "Supporter locked both": (Window(supporter=False), Window(supporter=False, behind=True)),
    "going first, behind second": (Window(supporter=False), Window(behind=True)),
    "going first, Item locked second": (
        Window(supporter=False), Window(item=False, behind=True)),
}


def physical_oracle(basics: int, guzma: int, prime: int, counter: int,
                    first: Window, second: Window,
                    total: int = 10, hand_size: int = 3, prizes: int = 2
                    ) -> tuple[Fraction, Fraction]:
    """Independently deal labeled hand, random Prizes, then ordered natural draws."""
    deck = (["B"] * basics + ["G"] * guzma + ["P"] * prime +
            ["C"] * counter + ["F"] * (total - basics - guzma - prime - counter))
    counts = [0, 0, 0]
    ids = tuple(range(total))
    for hand_ids in combinations(ids, hand_size):
        hand = [deck[i] for i in hand_ids]
        if "B" not in hand:
            continue
        remaining = tuple(i for i in ids if i not in hand_ids)
        for prize_ids in combinations(remaining, prizes):
            deck_ids = tuple(i for i in remaining if i not in prize_ids)
            for draw1, draw2 in permutations(deck_ids, 2):
                counts[0] += 1
                held1 = hand + [deck[draw1]]
                held2 = held1 + [deck[draw2]]

                def eligible(cards: list[str], turn: Window) -> bool:
                    return bool((turn.supporter and "G" in cards) or
                                (turn.item and ("P" in cards or
                                                (turn.behind and "C" in cards))))

                first_hit = eligible(held1, first)
                counts[1] += first_hit
                counts[2] += first_hit or eligible(held2, second)
    return Fraction(counts[1], counts[0]), Fraction(counts[2], counts[0])


def validate_prints() -> None:
    root = Path(__file__).resolve().parents[2]
    resources = root / "resources"
    manifest = json.loads((root / "results" / "competitive_deck_baselines" /
                           "regidrago_haruku_2026.json").read_text(encoding="utf-8"))
    assert manifest["source"]["url"] == "https://limitlesstcg.com/decks/list/26816"
    assert manifest["source"]["date"] == "2026-05-10"
    rows = manifest["cards"]
    counts = Counter({r["name"]: r["quantity"] for r in rows})
    assert sum(counts.values()) == 60
    assert counts["Guzma"] == 2 and counts["Prime Catcher"] == 1
    assert counts["VS Seeker"] == 3 and counts["Battle VIP Pass"] == 3
    assert counts["Counter Catcher"] == 0

    variant = [dict(r) for r in rows]
    guzma = next(r for r in variant if r["name"] == "Guzma")
    assert guzma["print_id"] == "sm3-115"
    guzma["quantity"] -= 1
    variant.append({"category": "Trainer", "quantity": 1,
                    "name": "Counter Catcher", "print_id": "sv4-160"})
    assert sum(r["quantity"] for r in variant) == 60
    records = load_all_card_records(resources)
    assert sum(r["quantity"] for r in variant
               if records[r["print_id"]].is_basic_pokemon) == 15
    assert Counter(r["category"] for r in variant
                   for _ in range(r["quantity"])) == {
        "Pokémon": 20, "Trainer": 30, "Energy": 10}
    for r in variant:
        assert records[r["print_id"]].name == r["name"]
    proof = adjudicate_deck(
        tuple(DeckEntry(r["print_id"], r["quantity"]) for r in variant),
        resources, as_of=date(2026, 10, 12))
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason) for p in proof.print_proofs
        if p.eligibility != "eligible"
    ]
    for print_id, kind, snippet in (
        ("sm3-115", "Supporter", "Switch 1 of your opponent's Benched"),
        ("sv5-157", "Item", "Switch in 1 of your opponent's Benched"),
        ("sv4-160", "Item", "more Prize cards remaining"),
    ):
        set_id = print_id.rsplit("-", 1)[0]
        raw = json.loads((resources / "cards" / "en" / f"{set_id}.json")
                         .read_text(encoding="utf-8"))
        card = next(c for c in raw if c["id"] == print_id)
        assert kind in card["subtypes"] and snippet in card["rules"][0]
    print("PASS: published 60-card source and legal 60-card 1-Guzma/1-Counter variant")


def verify() -> None:
    validate_prints()
    for guzma, prime, counter in ((2, 1, 0), (1, 1, 1), (0, 0, 2), (1, 0, 0)):
        for label, (first, second) in SCENARIOS.items():
            exact = access(2, guzma, prime, counter, first, second,
                           total=10, hand_size=3, prize_count=2)
            physical = physical_oracle(2, guzma, prime, counter, first, second)
            assert exact == physical, (guzma, prime, counter, label, exact, physical)
    assert access(15, 2, 1, 0, Window(behind=True), Window(behind=True)) == (
           access(15, 1, 1, 1, Window(behind=True), Window(behind=True)))
    for label, (first, second) in SCENARIOS.items():
        original = access(15, 2, 1, 0, first, second)
        variant = access(15, 1, 1, 1, first, second)
        print(f"{label}: original P1={float(original[0]*100):.6f}% / "
              f"P2={float(original[1]*100):.6f}%; "
              f"variant P1={float(variant[0]*100):.6f}% / "
              f"P2={float(variant[1]*100):.6f}%; "
              f"delta P2={float((variant[1]-original[1])*100):+.6f} pp")
    print("PASS: 32 independent fully labeled miniature Prize-zone oracles")


if __name__ == "__main__":
    verify()
