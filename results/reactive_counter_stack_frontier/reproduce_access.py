"""Exhaustive exact combinatorial audit, independently derived endpoint formulas."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from reactive_stack_natural_access import (
    access_probability, independent_oracle, verify_sources, study,
)

def run() -> dict:
    verify_sources(ROOT/"resources")
    last=(0,0,0)
    for n in range(61):
        values=tuple(access_probability(n,t) for t in (17,22,29))
        assert values[0]==independent_oracle(n,17), n
        assert values[2]==independent_oracle(n,29), n
        assert 0<=values[2]<=values[1]<=values[0]<=1
        assert all(a<=b for a,b in zip(last,values))
        last=values
    assert last==(1,1,1)
    return study()

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
