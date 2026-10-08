"""Independent physical-card rescue enumeration and prior-baseline checks."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_active_trigger_rescue import analyze_rescue
from bench_trigger_access import analyze_bench_trigger_access


def independent_oracle() -> None:
    # A singleton support, two ordinary Basics O, ideal connector H,
    # direct-to-Bench Item D, two fair pickup Items R and three fillers.
    cards = "AOOHDRRFFF"
    accepted = 0
    baseline_mass = Fraction(0)
    rescued_mass = Fraction(0)
    attempt_mass = Fraction(0)

    for opener in combinations(range(len(cards)), 3):
        original_hand = [cards[i] for i in opener]
        if not any(x in "AO" for x in original_hand):
            continue
        forced_a = "A" in original_hand and "O" not in original_hand
        after_opening = set(range(len(cards))) - set(opener)

        for prizes in combinations(after_opening, 2):
            after_prizes = after_opening - set(prizes)
            for drawn_card in after_prizes:
                seen = set(opener) | {drawn_card}
                visible = [cards[i] for i in seen]
                deck = after_prizes - {drawn_card}
                hand_search = visible.count("H")
                direct_search = visible.count("D")
                pickups = visible.count("R")

                a_available = (
                    ("A" in visible and not forced_a)
                    or (hand_search > 0
                        and any(cards[i] == "A" for i in deck))
                )
                backup = (
                    any(cards[i] == "O" for i in seen)
                    or (hand_search + direct_search > 0
                        and any(cards[i] == "O" for i in deck))
                )
                can_scoop = forced_a and backup and pickups > 0
                rescued = (Fraction((1 << pickups) - 1, 1 << pickups)
                           if can_scoop else Fraction(0))
                accepted += 1
                baseline_mass += int(a_available)
                attempt_mass += int(can_scoop)
                rescued_mass += int(a_available) + (
                    rescued if not a_available else 0
                )

    actual = analyze_rescue(
        deck_size=10, opening_size=3, prize_count=2,
        later_random_draws=1, other_basics=2,
        hand_connectors=1, direct_bench_items=1, coin_pickups=2,
    )
    assert accepted == 8925
    assert actual.no_active_recovery == baseline_mass / accepted
    assert actual.with_active_recovery == rescued_mass / accepted
    assert actual.rescue_attempt_possible == attempt_mass / accepted
    assert actual.no_active_recovery == Fraction(46, 119)
    assert actual.with_active_recovery == Fraction(379, 850)
    print("Independent accepted labeled worlds:", accepted)
    print("No rescue:", actual.no_active_recovery)
    print("With rescue:", actual.with_active_recovery)


def check_prior_model_and_sensitivity() -> None:
    for other in (1, 3, 5, 8):
        for direct in (0, 4):
            result = analyze_rescue(other_basics=other, direct_bench_items=direct)
            previous = analyze_bench_trigger_access(
                trigger_basics=1, other_basics=other,
                hand_connectors=4, direct_bench_connectors=direct,
                extra_random_draws=1,
            )
            assert result.no_active_recovery == previous.role_aware_access_given_valid
            assert result.valid_start == previous.valid_start_probability
            assert result.gain > 0
            print("Other Basics", other, "direct-Bench Items", direct,
                  "baseline:", f"{100*float(result.no_active_recovery):.6f}%",
                  "rescue:", f"{100*float(result.with_active_recovery):.6f}%",
                  "gain:", f"{100*float(result.gain):.6f}pp")

    no_pickups = analyze_rescue(coin_pickups=0, guaranteed_pickups=0)
    no_backups = analyze_rescue(other_basics=0)
    assert no_pickups.gain == no_backups.gain == 0
    assert (analyze_rescue(other_basics=3, direct_bench_items=4).gain
            > analyze_rescue(other_basics=3, direct_bench_items=0).gain)
    assert (analyze_rescue(other_basics=3, direct_bench_items=4,
                           guaranteed_pickups=1, coin_pickups=0).gain > 0)
    print("PASS: labeled oracle, earlier baseline, pickup and backup gates")


if __name__ == "__main__":
    independent_oracle()
    check_prior_model_and_sensitivity()
