"""Exact Prize conditioning for state-dependent Bench-restoration outs."""
from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path

from prize_belief_kernel import PrizeBelief


def hit_probability(deck_cards: int, outs: int, draws: int) -> Fraction:
    if outs == 0 or draws == 0:
        return Fraction(0, 1)
    return Fraction(1, 1) - Fraction(math.comb(deck_cards-outs, draws), math.comb(deck_cards, draws))


def exact_prize_states(pool_size: int, prize_count: int, direct: int, removers: int):
    filler = pool_size - direct - removers
    den = math.comb(pool_size, prize_count)
    rows = []
    for direct_prized in range(direct + 1):
        for remover_prized in range(removers + 1):
            filler_prized = prize_count - direct_prized - remover_prized
            if not 0 <= filler_prized <= filler:
                continue
            ways = (
                math.comb(direct, direct_prized)
                * math.comb(removers, remover_prized)
                * math.comb(filler, filler_prized)
            )
            if ways:
                rows.append((direct_prized, remover_prized, Fraction(ways, den)))
    return rows


def expected_access(pool_size: int, prize_count: int, direct: int, removers: int, draws: int, slack: int):
    deck_cards = pool_size - prize_count
    expected = Fraction(0, 1)
    live_distribution: dict[int, Fraction] = {}
    for dp, rp, mass in exact_prize_states(pool_size, prize_count, direct, removers):
        live = direct - dp + ((removers-rp) if slack else 0)
        live_distribution[live] = live_distribution.get(live, Fraction(0, 1)) + mass
        expected += mass * hit_probability(deck_cards, live, draws)
    return expected, live_distribution


def belief_validation(pool_size: int, prize_count: int, direct: int, removers: int, draws: int, slack: int):
    belief = PrizeBelief.from_hypergeometric(
        {"direct": direct, "remover": removers},
        pool_size=pool_size,
        prize_count=prize_count,
    )
    expected = 0.0
    deck_cards = pool_size - prize_count
    for state, mass in belief.state_dicts():
        live = direct - state["direct"] + ((removers-state["remover"]) if slack else 0)
        expected += mass * float(hit_probability(deck_cards, live, draws))
    return expected, belief.probability_mass()


def pct(value: Fraction) -> float:
    return 100.0 * value.numerator / value.denominator


def exact_k1(deck_cards: int, draws: int, direct: int, removers: int, direct_prized: int, remover_prized: int, slack: int):
    live = direct-direct_prized + ((removers-remover_prized) if slack else 0)
    value = hit_probability(deck_cards, live, draws)
    return {"live_unlockers": live, "fraction": f"{value.numerator}/{value.denominator}", "percent": pct(value)}


def build_result():
    pool, prizes, direct, removers, draws = 46, 6, 2, 2, 5
    zero, zero_dist = expected_access(pool, prizes, direct, removers, draws, 0)
    one, one_dist = expected_access(pool, prizes, direct, removers, draws, 1)
    zero_float, mass0 = belief_validation(pool, prizes, direct, removers, draws, 0)
    one_float, mass1 = belief_validation(pool, prizes, direct, removers, draws, 1)
    assert abs(float(zero)-zero_float) < 1e-12
    assert abs(float(one)-one_float) < 1e-12
    assert abs(mass0-1.0) < 1e-12 and abs(mass1-1.0) < 1e-12

    k1 = {
        "no_relevant_prizes_zero_slack": exact_k1(40, draws, direct, removers, 0, 0, 0),
        "one_direct_prized_zero_slack": exact_k1(40, draws, direct, removers, 1, 0, 0),
        "one_remover_prized_zero_slack": exact_k1(40, draws, direct, removers, 0, 1, 0),
        "one_direct_prized_one_slack": exact_k1(40, draws, direct, removers, 1, 0, 1),
        "one_remover_prized_one_slack": exact_k1(40, draws, direct, removers, 0, 1, 1),
    }
    assert k1["one_direct_prized_zero_slack"]["percent"] == 12.5
    assert k1["one_remover_prized_zero_slack"]["fraction"] == "37/156"
    assert k1["one_direct_prized_one_slack"] == k1["one_remover_prized_one_slack"]

    def dist_rows(dist):
        return [
            {"live_unlockers": live, "mass_fraction": f"{mass.numerator}/{mass.denominator}", "mass_percent": pct(mass)}
            for live, mass in sorted(dist.items())
        ]

    return {
        "example": {"unknown_pool": pool, "prize_count": prizes, "post_prize_deck": 40, "draws": draws, "direct_restorers": direct, "removers": removers},
        "k0": {
            "zero_slack_expected_fraction": f"{zero.numerator}/{zero.denominator}",
            "zero_slack_expected_percent": pct(zero),
            "one_slack_expected_fraction": f"{one.numerator}/{one.denominator}",
            "one_slack_expected_percent": pct(one),
            "zero_slack_live_out_distribution": dist_rows(zero_dist),
            "one_slack_live_out_distribution": dist_rows(one_dist),
        },
        "k1_examples": k1,
        "findings": {
            "zero_slack_prize_asymmetry": "Prizing a direct restorer reduces current unlock access, while Prizing a remover does not change zero-slack access because remover copies are already mechanically dead.",
            "one_slack_symmetry": "With one Bench slack and symmetric access, a direct restorer and remover become equivalent live outs, so one copy of either being Prized has the same access effect.",
            "belief_state": "K0 is a distribution over live-out counts; K1 collapses to the realized state-specific count and can materially change the estimated unlock probability.",
        },
    }


def atomic_write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path=path.with_suffix(path.suffix+".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name=="nt":
            import msvcrt
            msvcrt.locking(lock_file.fileno(),msvcrt.LK_LOCK,1)
        else:
            import fcntl
            fcntl.flock(lock_file.fileno(),fcntl.LOCK_EX)
        temp=None
        try:
            with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=path.parent,delete=False) as h:
                json.dump(payload,h,indent=2,ensure_ascii=False)
                h.write("\n")
                h.flush()
                os.fsync(h.fileno())
                temp=Path(h.name)
            os.replace(temp,path)
        finally:
            if temp is not None and temp.exists():
                temp.unlink()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("results/bench_restore_prize_conditioning/model.json"))
    args=parser.parse_args()
    r=build_result()
    atomic_write_json(args.output,r)
    print(json.dumps(r,indent=2))


if __name__=="__main__":
    main()
