"""Exact Aichi Regidrago natural turn-one material access, conditional Basic opener."""
from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def exact_natural_choice(total: int, regidrago_v: int, other_basic: int,
                         dde: int, grass: int, fire: int,
                         opener: int = 7) -> dict[str, Fraction]:
    """Eight cards are observed: legal opening seven and one natural draw.

    Six initial Prizes are integrated out by exchangeability. We count
    unordered eight-card hands weighted by the number of ways the eighth
    card can be distinguished without leaving a Basic-less first seven.
    """
    if not 0 < opener < total:
        raise ValueError("Invalid opening")
    other = total - sum((regidrago_v, other_basic, dde, grass, fire))
    if min(regidrago_v, other_basic, dde, grass, fire, other) < 0:
        raise ValueError("Invalid card partition")
    counts = (regidrago_v, other_basic, dde, grass, fire, other)
    seen = opener + 1
    den = either = with_grass = with_fire = both = 0
    for prefix in product(*(range(min(count, seen) + 1) for count in counts[:-1])):
        filler = seen - sum(prefix)
        if not 0 <= filler <= other:
            continue
        rv, basics, d, g, f, _ = hand = (*prefix, filler)
        possible_eighth = seen if rv + basics >= 2 else opener if rv + basics == 1 else 0
        if not possible_eighth:
            continue
        ways = possible_eighth
        for n, k in zip(counts, hand):
            ways *= choose(n, k)
        den += ways
        if rv and d:
            with_grass += ways * bool(g)
            with_fire += ways * bool(f)
            both += ways * bool(g and f)
            either += ways * bool(g or f)
    assert either == with_grass + with_fire - both
    assert den == (total - opener) * (
        choose(total, opener) - choose(total - regidrago_v - other_basic, opener)
    )
    return {
        "valid_opening": Fraction(choose(total, opener)
                    - choose(total-regidrago_v-other_basic, opener), choose(total,opener)),
        "either": Fraction(either, den),
        "grass": Fraction(with_grass, den),
        "fire": Fraction(with_fire, den),
        "both": Fraction(both, den),
        "both_given_either": Fraction(both, either) if either else Fraction(),
    }


def build(root: Path) -> dict:
    source = json.loads((root / "results/regidrago_aichi_top10_playable/yoshioka_regidrago_2026.json").read_text(encoding="utf-8"))
    basic_names = {"Regidrago V", "Budew", "Dialga-GX", "Koraidon ex", "Kyurem",
                   "Dedenne-GX", "Squawkabilly ex", "Tapu Lele-GX", "Latias ex",
                   "Marshadow", "Wobbuffet"}
    poke = source["groups"]["Pokémon"]
    rv = next(int(c["count"]) for c in poke if c["name"] == "Regidrago V")
    basic = sum(int(c["count"]) for c in poke if c["name"] in basic_names)
    energy = {c["name"]: int(c["count"]) for c in source["groups"]["Energy"]}
    assert (rv, basic) == (4, 15)
    assert energy == {"Double Dragon Energy": 4, "Grass Energy": 4, "Fire Energy": 2}
    assert sum(int(c["count"]) for group in source["groups"].values() for c in group) == 60
    result = exact_natural_choice(60, rv, basic - rv, 4, 4, 2)
    assert result["both"] == Fraction(20692516, 1505320575)
    assert result["either"] == Fraction(470817817, 4515961725)
    assert result["both_given_either"] == Fraction(62077548, 470817817)
    return {
        "deck": source["source"],
        "groups": {"regidrago_v":rv,"other_basic":basic-rv,"dde":4,"grass":4,"fire":2,"other":35},
        "setup": "Valid seven-card Basic opening, six hidden Prizes, first natural draw",
        "source_access_only": {key:str(value) for key,value in result.items()},
    }


if __name__ == "__main__":
    print(json.dumps(build(Path(".")), indent=2))
