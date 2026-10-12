"""SFT: exact Regidrago Guzma/V/VSTAR with paid Item searches.

Run: python -m results.regidrago_legacy_item_access.reproduce
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path

from tools.regidrago_legacy_item_access import Window, solve
from tools.regidrago_legacy_star_launch import launch
from results.aichi_regidrago_gust_deadlines.reproduce import validate_prints


def physical_oracle(w: Window, opening: int = 3, prizes: int = 2) -> Fraction:
    """Fully labeled physical openings, real Prize removals and draw labels.

    Each T1 search physically removes its chosen V/VSTAR target. Its shuffle
    makes every remaining physical card equally likely for T2 draw. This
    independent oracle enumerates that draw, with exact rational weights.
    """
    rest = (w.total - w.others - w.v - w.star - w.guzma -
            w.vip - w.quick - w.treasure - w.safe)
    cards = (["O"] * w.others + ["V"] * w.v + ["S"] * w.star +
             ["G"] * w.guzma + ["I"] * w.vip + ["Q"] * w.quick +
             ["T"] * w.treasure + ["D"] * w.safe + ["F"] * rest)
    ids = set(range(len(cards)))
    successful = Fraction(0)
    accepted = 0
    for opening_ids in combinations(range(len(cards)), opening):
        original_hand = [cards[i] for i in opening_ids]
        if "O" not in original_hand and "V" not in original_hand:
            continue
        nonhand = ids - set(opening_ids)
        for prize_ids in combinations(sorted(nonhand), prizes):
            remaining = nonhand - set(prize_ids)
            for first_draw in sorted(remaining):
                accepted += 1
                hand = original_hand + [cards[first_draw]]
                if "G" not in hand:
                    continue
                hand.remove("G")
                deck = sorted(remaining - {first_draw})

                def physical_search(target: str) -> bool:
                    for target_id in deck:
                        if cards[target_id] == target:
                            deck.remove(target_id)
                            return True
                    return False

                ready_v = "V" in hand
                if ready_v:
                    hand.remove("V")
                if not ready_v and w.first_item:
                    if "I" in hand and physical_search("V"):
                        hand.remove("I")
                        ready_v = True
                    elif ("Q" in hand and "D" in hand and
                          physical_search("V")):
                        hand.remove("Q")
                        hand.remove("D")
                        ready_v = True
                    elif ("T" in hand and "D" in hand and
                          physical_search("V")):
                        hand.remove("T")
                        hand.remove("D")
                        ready_v = True
                if not ready_v:
                    continue

                if ("S" not in hand and w.first_item and
                    "T" in hand and "D" in hand and
                    physical_search("S")):
                    hand.remove("T")
                    hand.remove("D")
                    hand.append("S")

                for second_draw in deck:
                    t2_hand = hand + [cards[second_draw]]
                    t2_deck = [i for i in deck if i != second_draw]
                    success = (
                        "S" in t2_hand or
                        (w.second_item and "T" in t2_hand and
                         "D" in t2_hand and
                         any(cards[i] == "S" for i in t2_deck))
                    )
                    if success:
                        successful += Fraction(1, len(deck))
    return successful / accepted


def verify_prints() -> None:
    root = Path(__file__).resolve().parents[2]
    resources = root / "resources" / "cards" / "en"
    manifest = json.loads(
        (root / "results" / "competitive_deck_baselines" /
         "regidrago_haruku_2026.json").read_text(encoding="utf-8"))
    quantities = {r["name"]: r["quantity"] for r in manifest["cards"]}
    assert quantities["Regidrago V"] == 4
    assert quantities["Regidrago VSTAR"] == 3
    assert quantities["Guzma"] == 2
    assert quantities["Battle VIP Pass"] == 3
    assert quantities["Quick Ball"] == 3
    assert quantities["Mysterious Treasure"] == 3
    assert sum(r["quantity"] for r in manifest["cards"]) == 60

    for source_id, name, wanted in (
        ("swsh8-225", "Battle VIP Pass", "first turn"),
        ("swsh1-179", "Quick Ball", "discard another card"),
        ("sm6-113", "Mysterious Treasure", "Psychic or Dragon"),
    ):
        set_id = source_id.rsplit("-", 1)[0]
        raw = json.loads(
            (resources / f"{set_id}.json").read_text(encoding="utf-8"))
        card = next(c for c in raw if c["id"] == source_id)
        assert card["name"] == name
        assert "Item" in card["subtypes"]
        assert wanted in " ".join(card["rules"])
        print(f"PASS: source printed Item {source_id} / {name}")
    validate_prints()


def verify() -> None:
    verify_prints()
    examples = (
        Window(total=10, others=1, v=2, star=1, guzma=1,
               vip=1, quick=1, treasure=1, safe=1),
        Window(total=10, others=2, v=1, star=2, guzma=1,
               vip=1, quick=1, treasure=1, safe=0),
        Window(total=10, others=1, v=2, star=2, guzma=1,
               vip=0, quick=1, treasure=1, safe=1),
        Window(total=11, others=2, v=2, star=1, guzma=2,
               vip=1, quick=0, treasure=1, safe=1),
    )
    count = 0
    for template in examples:
        for first, second in ((False, False), (True, False), (True, True)):
            w = replace(template, first_item=first, second_item=second)
            exact = solve(w, opening=3, prizes=2)["star_t2"]
            brute = physical_oracle(w)
            assert exact == brute, (w, exact, brute)
            count += 1
            print(f"PASS: physical toy #{count:02d}, {w.total} cards, "
                  f"Items T1={first}/T2={second}, P={exact}")

    for g in (1, 2):
        prior = launch(11, 4, 3, g)
        exact = solve(Window(guzma=g, safe=0, first_item=False,
                             second_item=False))["star_t2"]
        assert prior == exact, (prior, exact)
        print(f"PASS: no-Item regression g={g}, exact={exact}")

    print("Exact original versus legal Counter Catcher 60-card variant")
    for safe in (0, 10, 20):
        for first, second in ((False, False), (True, False), (True, True)):
            w = Window(safe=safe, first_item=first, second_item=second)
            original = solve(w)
            variant = solve(replace(w, guzma=1))
            assert original["star_t2"] > variant["star_t2"]
            print(f"D={safe:02d}, T1 Item={first}, T2 Item={second}: "
                  f"published={float(100 * original['star_t2']):.9f}%, "
                  f"variant={float(100 * variant['star_t2']):.9f}%, "
                  f"delta={float(100*(original['star_t2']-variant['star_t2'])):.9f} pp; "
                  f"prefetch={float(100*original['prefetch_t1']):.9f}%, "
                  f"second search={float(100*original['search_t2']):.9f}%")
    print("PASS: 12 independent physically labeled miniature Prize/search oracles")
    print("PASS: two independent no-Item 60-card exact reductions")
    print("LIMIT: conditional physical access only; no actual matchup win rate")


if __name__ == "__main__":
    verify()
