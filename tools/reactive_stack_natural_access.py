"""Exact unconditioned natural-card accessibility of a hypothetical Scrafty shell."""
from __future__ import annotations
from fractions import Fraction
from math import comb
from pathlib import Path
import json
from build_expanded_legality_baseline import classify_effective_legality
from reactive_counter_stack_frontier import source_validate

COUNTS = (4, 3, 4, 4, 1, 44)

def choose(n: int, r: int) -> int:
    return comb(n, r) if 0 <= r <= n else 0

def access_probability(n: int, counters: int) -> Fraction:
    """Uniform subset of 60; 4 Scraggy, 3 Mega, 4 Spiritomb, 4 Spiky, 1 Deluxe, 44 other."""
    if not 0 <= n <= 60 or counters < 0:
        raise ValueError("invalid draw size or threshold")
    wins = 0
    for a in range(1, 5):
        for b in range(1, 4):
            for c in range(5):
                for d in range(5):
                    other = n - a - b - c - d - 1
                    if 0 <= other <= 44 and 17 + c + 2*d >= counters:
                        wins += choose(4,a)*choose(3,b)*choose(4,c)*choose(4,d)*choose(44,other)
    return Fraction(wins,choose(60,n))

def independent_oracle(n: int, counters: int) -> Fraction:
    """Inclusion-exclusion for lower (17) and maximum (29) fixed packages."""
    if counters == 17:
        k=n-1
        x=choose(59,k)-choose(55,k)-choose(56,k)+choose(52,k)
    elif counters == 29:
        k=n-9
        x=choose(51,k)-choose(47,k)-choose(48,k)+choose(44,k)
    else:
        raise ValueError("oracle supports 17 or 29")
    return Fraction(x,choose(60,n))

def verify_sources(resources: Path) -> None:
    source_validate(resources)
    cards=json.loads((resources/"cards"/"en"/"me2pt5.json").read_text(encoding="utf-8"))
    card=next(c for c in cards if c["id"]=="me2pt5-134")
    assert card["name"]=="Scraggy" and "Basic" in card["subtypes"]
    assert classify_effective_legality(card)[0]=="Legal"

def study() -> dict:
    return {"inventory":{"Scraggy":4,"Mega Scrafty ex":3,"Spiritomb":4,
                          "Spiky Energy":4,"Deluxe Bomb":1,"inert_other":44},
            "natural_only_probability":[
                {"n":n,"p170":format(float(access_probability(n,17)),".12g"),
                 "p220":format(float(access_probability(n,22)),".12g"),
                 "p290":format(float(access_probability(n,29)),".12g")}
                for n in (11,14,18,24,30)]}
