"""Independent labeled-card test of the exact two-trigger pickup model."""
from __future__ import annotations

import itertools
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from bench_double_trigger_access import analyze


def exhaustive_small_deck():
    cards = tuple("ABOOHDCFF")
    valid = [0, 0, 0, 0]
    all_valid = 0
    for opener in itertools.combinations(range(len(cards)), 3):
        oh = [cards[i] for i in opener]
        if not any(x in ("A", "B", "O") for x in oh):
            continue
        rest = [i for i in range(len(cards)) if i not in opener]
        active = "O" if "O" in oh else ("A" if "A" in oh else "B")
        active_idx = next(i for i in opener if cards[i] == active)
        for prizes in itertools.combinations(rest, 2):
            deck = [i for i in rest if i not in prizes]
            for next_card in deck:
                hand_ids = set(opener) | {next_card}
                actual_hand_ids = hand_ids - {active_idx}
                in_deck = set(deck) - {next_card}
                hand = [cards[i] for i in hand_ids]
                actual_hand = [cards[i] for i in actual_hand_ids]
                lookups = hand.count("H") + hand.count("D")
                h_lookups = hand.count("H")
                searchable = [
                    any(cards[i] == target for i in in_deck)
                    for target in ("A", "B")
                ]
                nominal = all(
                    target in hand or (lookups > 0 and searchable[k])
                    for k, target in enumerate(("A", "B"))
                )
                role = all(
                    target in actual_hand or (lookups > 0 and searchable[k])
                    for k, target in enumerate(("A", "B"))
                )
                missing = sum(target not in actual_hand for target in ("A", "B"))
                typed = (
                    missing <= h_lookups
                    and all(
                        target in actual_hand or searchable[k]
                        for k, target in enumerate(("A", "B"))
                    )
                )
                release = "C" in hand
                for coin_head in (False, True):
                    all_valid += 1
                    valid[0] += int(release and nominal)
                    valid[1] += int(release and role)
                    valid[2] += int(release and typed)
                    valid[3] += int(release and typed and coin_head)
    result = analyze(
        deck_size=9, opening_size=3, prize_count=2, draws=1,
        other_basics=2, hand_connectors=1, direct_connectors=1,
        certain_pickups=0, coin_pickups=1, bench_slack=1,
    )
    expected = tuple(Fraction(n, all_valid) for n in valid)
    found = (result.nominal, result.role_aware, result.typed_one_use,
             result.stochastic_exact)
    assert found == expected, (found, expected)
    print("Independent labeled small-deck sequences:", all_valid,
          "exact agreement:", [str(f) for f in found])


def regressions():
    assert analyze(coin_pickups=0, certain_pickups=0,
                   bench_slack=1).stochastic_exact == 0
    assert analyze(bench_slack=0).stochastic_exact == 0
    baseline = analyze(draws=4, coin_pickups=2)
    assert (baseline.nominal >= baseline.role_aware
            >= baseline.typed_one_use >= baseline.stochastic_exact)
    certain = analyze(draws=4, certain_pickups=1, coin_pickups=0)
    assert certain.typed_one_use == certain.stochastic_exact
    free = analyze(draws=4, certain_pickups=0, coin_pickups=0, bench_slack=2)
    assert free.typed_one_use == free.stochastic_exact > 0
    for kwargs in (
        dict(draws=1, coin_pickups=2),
        dict(draws=4, coin_pickups=2),
        dict(draws=4, coin_pickups=4),
        dict(draws=4, certain_pickups=1, coin_pickups=0),
        dict(draws=4, bench_slack=2, coin_pickups=0),
    ):
        x = analyze(**kwargs)
        print("Configuration", kwargs, "valid opener",
              f"{100 * float(x.valid_start):.6f}%")
        print("  nominal / role / typed / exact:",
              *(f"{100*float(p):.6f}%" for p in
                (x.nominal, x.role_aware,
                 x.typed_one_use, x.stochastic_exact)))
        print("  source gaps (percentage points):",
              *(f"{100*float(g):.6f}" for g in
                (x.active_role_gap, x.connector_gap, x.coin_gap)))


if __name__ == "__main__":
    exhaustive_small_deck()
    regressions()
    print("PASS: independent exhaustive oracle and scenario regressions")
