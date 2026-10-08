"""SFT: exact K0/K1 feasibility bounds for Sky Field-as-Ultra Ball payment."""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from teleport_discard_access_bound import (
    UnknownPool,
    at_least_one_of_each,
    enumerate_small_k0,
    example_results,
    k0_payload_probability,
    k1_payload_probability,
)


def pct(value: Fraction) -> float:
    return 100.0 * float(value)


def main() -> None:
    tiny = UnknownPool(10, 2, 3, 2, 2, 2)
    exhaustive = enumerate_small_k0(tiny)
    analytic = k0_payload_probability(tiny)
    assert exhaustive == analytic
    print(f"PASS: 10-card exhaustive enumeration equals {analytic}")

    no_prize = UnknownPool(9, 0, 5, 2, 2, 2)
    assert enumerate_small_k0(no_prize) == k0_payload_probability(no_prize)
    assert at_least_one_of_each(6, 2, (1, 1, 1)) == 0
    print("PASS: no-Prize exhaustive enumeration and impossible hand-size gate")

    r = example_results()
    spec = r["unknown_pool"]
    aware = r["k0_payment_aware"]
    optimistic = r["k0_access_only"]
    assert spec == UnknownPool(46, 6, 5, 4, 2, 16)
    assert aware == Fraction(7280, 174537)
    assert optimistic == Fraction(213800, 4014351)
    assert optimistic > aware
    assert k0_payload_probability(UnknownPool(46, 6, 5, 4, 2, 0)) == 0
    print(f"PASS: 46-card K0 payment-aware {aware} = {pct(aware):.6f}%")
    print(f"PASS: access-only comparator {optimistic} = {pct(optimistic):.6f}%")
    print(f"PASS: access-only overstatement {pct(optimistic-aware):.6f} pp")

    previous = Fraction(-1)
    for d, probability in r["vary_discardable_pool"].items():
        assert previous <= probability <= optimistic
        previous = probability
        print(f"  approved_discard={d:2d}: {pct(probability):.6f}%")
    assert r["vary_discardable_pool"][0] == 0
    assert r["vary_discardable_pool"][16] == aware
    print("PASS: additional approved payments weakly improve access")

    full = r["k1_all_live"]
    one_sky = r["k1_one_sky_prized"]
    assert full == Fraction(5588, 82251)
    assert one_sky == Fraction(322, 9139)
    assert full > one_sky > 0
    assert k1_payload_probability(
        40, 5, unprized_ultra_ball=4,
        unprized_sky_field=0, unprized_approved_discard=16,
    ) == 0
    assert k1_payload_probability(
        40, 5, unprized_ultra_ball=4,
        unprized_sky_field=2, unprized_approved_discard=16,
        target_prized=True,
    ) == 0
    print("PASS: target or both Sky copies Prized closes the exact channel")
    print(f"PASS: all designated outs unprized K1 = {pct(full):.6f}%")
    print(f"PASS: one Sky Prized K1 = {pct(one_sky):.6f}%")
    print(json.dumps({
        "scenario": asdict(spec),
        "k0_fraction": str(aware),
        "k0_percent": round(pct(aware), 6),
        "access_only_percent": round(pct(optimistic), 6),
        "k1_all_live_percent": round(pct(full), 6),
        "k1_one_sky_prized_percent": round(pct(one_sky), 6),
        "claim_scope": "conditional on established Gothitelle, exhausted ordinary Stadium quota, required Basic already in hand, full Collapsed Bench, and this exact Ultra Ball payload path",
    }, indent=2))
    print("teleport_discard_access_bound regression: PASS")


if __name__ == "__main__":
    main()
