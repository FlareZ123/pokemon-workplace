"""Aichi Regidrago: matched-hand Crispin stock invariance under Energy choice."""
from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path

from tools.aichi_regidrago_crispin_energy_supply import both_types_in_deck
from tools.aichi_regidrago_t1_natural_choice import choose


def after_payment(hand: tuple[str, ...], deck: tuple[str, ...],
                  prizes: tuple[str, ...], basic: str) -> dict:
    if basic not in ("Grass", "Fire") or "DDE" not in hand or basic not in hand:
        raise ValueError("Energy must already be in hand")
    remaining = list(hand)
    remaining.remove("DDE")
    remaining.remove(basic)
    return {"hand": tuple(remaining), "deck": deck, "prizes": prizes,
            "discard": ("DDE", basic),
            "crispin_two_type_stock": "Grass" in deck and "Fire" in deck}


def exact_paired_stock(*, total: int, regidrago: int, other_basic: int,
                       dde: int, grass: int, fire: int,
                       opening: int, prizes: int) -> dict:
    """Exact two-type stock given natural first-eight R+DDE+Grass+Fire."""
    exposed = opening + 1
    if total - exposed < prizes:
        raise ValueError("Not enough cards")
    other = total - sum((regidrago,other_basic,dde,grass,fire))
    if min(other, regidrago,other_basic,dde,grass,fire) < 0:
        raise ValueError("Invalid deck")
    counts = (regidrago,other_basic,dde,grass,fire,other)
    denominator = 0
    total_success = Fraction()
    classes = 0
    for prefix in product(*(range(min(c,exposed)+1) for c in counts[:-1])):
        last = exposed-sum(prefix)
        if not 0<=last<=other:
            continue
        rv, basic, d, g, f, _ = held = (*prefix,last)
        if not (rv and d and g and f):
            continue
        ways = exposed if rv+basic>=2 else opening
        for count,owned in zip(counts,held):
            ways*=choose(count,owned)
        probability = both_types_in_deck(total-exposed, grass-g, fire-f, prizes)
        denominator += ways
        total_success += ways*probability
        classes += 1
    if not denominator:
        raise ValueError("No qualifying hand")
    p = total_success/denominator
    return {"hand_classes":classes,"after_grass":p,"after_fire":p,
            "causal_difference":Fraction(0)}


def build(root: Path) -> dict:
    source=json.loads((root/"results/regidrago_aichi_top10_playable/yoshioka_regidrago_2026.json").read_text(encoding="utf-8"))
    energy={x["name"]:x["count"] for x in source["groups"]["Energy"]}
    assert energy=={"Double Dragon Energy":4,"Grass Energy":4,"Fire Energy":2}
    hand=("Regidrago V","DDE","Grass","Fire","Trainer")
    deck=("Grass","Grass","Grass","Fire","Trainer")
    prizes=("Trainer",)
    a=after_payment(hand,deck,prizes,"Grass")
    b=after_payment(hand,deck,prizes,"Fire")
    assert a["deck"]==b["deck"] and a["prizes"]==b["prizes"]
    assert a["crispin_two_type_stock"]==b["crispin_two_type_stock"]
    result=exact_paired_stock(total=60,regidrago=4,other_basic=11,
                              dde=4,grass=4,fire=2,opening=7,prizes=6)
    assert result["hand_classes"]==102
    assert result["after_grass"]==Fraction(33898500113,40014152815)
    assert result["after_fire"]==result["after_grass"]
    return {"source":source["source"],
            "sample":"accepted first-seven and natural first draw holding Regidrago V, DDE, Grass, Fire",
            "outcomes":{k:str(v) for k,v in result.items()},
            "interpretation":"A hand-matched Energy choice does not change the deck; the remaining hand and discard do change"}


if __name__=="__main__":
    print(json.dumps(build(Path(".")),indent=2))
