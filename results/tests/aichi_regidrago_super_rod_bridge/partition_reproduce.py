"""Reproduce source-specific thirty-zone Basic Energy partition theorem."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from tools.aichi_regidrago_super_rod_partition_frontier import (
    analytic_counts, build, classify, independent_oracle, partitions, theorem,
)


def main() -> None:
    manifest=json.loads((Path("results/regidrago_aichi_top10_playable")/
                         "yoshioka_regidrago_2026.json").read_text(encoding="utf-8"))
    energies={x["name"]:x["count"] for x in manifest["groups"]["Energy"]}
    assert energies=={"Double Dragon Energy":4,"Grass Energy":4,"Fire Energy":2}
    results=build()
    assert results["distinct_type_zone_allocations"]==30
    assert results["branch_checks_with_independent_oracle"]==60
    assert results["classification"]=={"both":18,"fire_only":9,"grass_only":2,"neither":1}
    examples={
        "both":((1,3,0),(1,1,0)),
        "fire_only":((1,3,0),(2,0,0)),
        "grass_only":((4,0,0),(1,1,0)),
        "neither":((4,0,0),(2,0,0)),
    }
    for label,(g,f) in examples.items():
        assert classify(g,f)==label
        for pay in ("Grass","Fire"):
            assert theorem(g,f,pay)==independent_oracle(g,f,pay)
    for n_g in range(1,7):
        for n_f in range(1,7):
            actual=Counter(classify(g,f) for g in partitions(n_g)
                           for f in partitions(n_f))
            assert actual==Counter(analytic_counts(n_g,n_f))
    print("PASS: 30 Aichi partitions, 60 physical branch tests, 36 general count identities")
    print(results)


if __name__=="__main__":
    main()
