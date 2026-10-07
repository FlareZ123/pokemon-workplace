"""Exact state-conditioned access value of Bench-capacity restoration outs."""
from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path


def hit_probability(deck_cards: int, outs: int, draws: int) -> Fraction:
    if not (0 <= outs <= deck_cards):
        raise ValueError("outs outside deck")
    if not (0 <= draws <= deck_cards):
        raise ValueError("draws outside deck")
    if outs == 0 or draws == 0:
        return Fraction(0, 1)
    return Fraction(1, 1) - Fraction(math.comb(deck_cards - outs, draws), math.comb(deck_cards, draws))


def joint_two_class_probability(deck_cards: int, class_a: int, class_b: int, draws: int) -> Fraction:
    if min(class_a, class_b) < 0 or class_a + class_b > deck_cards:
        raise ValueError("invalid disjoint class sizes")
    den = math.comb(deck_cards, draws)
    def choose_remaining(removed: int) -> int:
        remaining = deck_cards - removed
        return math.comb(remaining, draws) if remaining >= draws else 0
    return Fraction(
        den
        - choose_remaining(class_a)
        - choose_remaining(class_b)
        + choose_remaining(class_a + class_b),
        den,
    )


def pct(value: Fraction) -> float:
    return 100.0 * value.numerator / value.denominator


def state_row(deck_cards: int, draws: int, direct: int, removers: int, entrants: int, slack: int):
    if slack not in {0, 1}:
        raise ValueError("this semantic island models slack 0 or 1")
    live_removers = removers if slack >= 1 else 0
    live_unlockers = direct + live_removers
    unlock = hit_probability(deck_cards, live_unlockers, draws)
    joint = joint_two_class_probability(deck_cards, live_unlockers, entrants, draws)
    return {
        "slack": slack,
        "direct_restorers": direct,
        "removers_in_deck": removers,
        "live_remover_outs": live_removers,
        "live_unlockers": live_unlockers,
        "unlock_probability_fraction": f"{unlock.numerator}/{unlock.denominator}",
        "unlock_probability_percent": pct(unlock),
        "joint_unlock_plus_entrant_fraction": f"{joint.numerator}/{joint.denominator}",
        "joint_unlock_plus_entrant_percent": pct(joint),
    }


def build_result():
    n, k, direct, removers, entrants = 40, 5, 2, 2, 4
    zero = state_row(n, k, direct, removers, entrants, 0)
    one = state_row(n, k, direct, removers, entrants, 1)

    zero_add_direct = state_row(n, k, direct + 1, removers, entrants, 0)
    zero_add_remover = state_row(n, k, direct, removers + 1, entrants, 0)
    one_add_direct = state_row(n, k, direct + 1, removers, entrants, 1)
    one_add_remover = state_row(n, k, direct, removers + 1, entrants, 1)

    def frac(row, key):
        a, b = row[key].split("/")
        return Fraction(int(a), int(b))

    zero_base = frac(zero, "unlock_probability_fraction")
    one_base = frac(one, "unlock_probability_fraction")
    zd = frac(zero_add_direct, "unlock_probability_fraction") - zero_base
    zr = frac(zero_add_remover, "unlock_probability_fraction") - zero_base
    od = frac(one_add_direct, "unlock_probability_fraction") - one_base
    or_ = frac(one_add_remover, "unlock_probability_fraction") - one_base

    assert zr == 0
    assert zd > 0
    assert od == or_ > 0
    assert one_base > zero_base

    return {
        "example": {
            "deck_cards": n,
            "random_cards_seen": k,
            "direct_restorers": direct,
            "bench_triggered_removers": removers,
            "required_entrant_outs": entrants,
        },
        "states": {"zero_slack": zero, "one_slack": one},
        "single_copy_marginals": {
            "zero_slack_add_direct_pp": pct(zd),
            "zero_slack_add_remover_pp": pct(zr),
            "one_slack_add_direct_pp": pct(od),
            "one_slack_add_remover_pp": pct(or_),
        },
        "findings": {
            "state_conditioned_outs": "Bench-triggered Stadium removers contribute zero live unlock outs at zero slack and become ordinary live outs once one Bench slot exists.",
            "joint_line_access": "The same state dependence carries into joint access to both an unlocker and a required entrant.",
            "copy_marginal_reversal": "Adding a remover copy has zero immediate unlock marginal at zero slack but matches a direct-restorer copy's simple draw-access marginal at one slack under symmetric access assumptions.",
        },
    }


def atomic_write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        temp = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
                temp = Path(handle.name)
            os.replace(temp, path)
        finally:
            if temp is not None and temp.exists():
                temp.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/bench_restoration_out_marginals/model.json"))
    args = parser.parse_args()
    result = build_result()
    atomic_write_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
