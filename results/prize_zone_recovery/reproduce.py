from __future__ import annotations

from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from conditioned_searchability import conditioned_searchability  # noqa: E402
from prize_zone_recovery import analyze_prize_zone_recovery  # noqa: E402


def assert_close(left: float, right: float, tolerance: float = 1e-12) -> None:
    if abs(left - right) > tolerance:
        raise AssertionError((left, right))


def labeled_validation() -> None:
    cards = ("A1", "A2", "B1", "S1", "S2", "F1", "F2", "F3", "F4", "F5")
    targets = (frozenset({"A1", "A2"}), frozenset({"B1"}))
    starters = frozenset({"S1", "S2"})
    hand_size, prize_count, draw_count = 3, 2, 1
    accepted = [frozenset(row) for row in combinations(cards, hand_size) if frozenset(row) & starters]
    totals = {key: 0.0 for key in (
        "mass", "baseline", "rotom", "ticket", "rotom_rescue", "rotom_break",
        "ticket_rescue", "ticket_break", "prize_failure", "nonprize_failure",
    )}

    for hand in accepted:
        after_hand = tuple(card for card in cards if card not in hand)
        for prize_row in combinations(after_hand, prize_count):
            prizes = frozenset(prize_row)
            after_prizes = tuple(card for card in after_hand if card not in prizes)
            for draw_row in combinations(after_prizes, draw_count):
                draws = frozenset(draw_row)
                deck = frozenset(card for card in after_prizes if card not in draws)
                mass = (
                    1 / len(accepted)
                    / comb(len(after_hand), prize_count)
                    / comb(len(after_prizes), draw_count)
                )
                totals["mass"] += mass
                baseline = all(len(deck & group) >= 1 for group in targets)
                totals["baseline"] += mass * baseline
                if not baseline:
                    if any(prizes & group for group in targets):
                        totals["prize_failure"] += mass
                    else:
                        totals["nonprize_failure"] += mass

                pool = deck | prizes
                rotom_rows = tuple(combinations(sorted(pool), prize_count))
                rotom_success = sum(
                    all(len((pool - frozenset(row)) & group) >= 1 for group in targets)
                    for row in rotom_rows
                ) / len(rotom_rows)
                totals["rotom"] += mass * rotom_success
                if baseline:
                    totals["rotom_break"] += mass * (1 - rotom_success)
                else:
                    totals["rotom_rescue"] += mass * rotom_success

                ticket_rows = tuple(combinations(sorted(deck), prize_count))
                ticket_success = sum(
                    all(len(((deck - frozenset(row)) | prizes) & group) >= 1 for group in targets)
                    for row in ticket_rows
                ) / len(ticket_rows)
                totals["ticket"] += mass * ticket_success
                if baseline:
                    totals["ticket_break"] += mass * (1 - ticket_success)
                else:
                    totals["ticket_rescue"] += mass * ticket_success

    exact = analyze_prize_zone_recovery(
        10, 2, (2, 1), opening_hand_size=3, prize_count=2, pre_search_draws=1
    )
    comparisons = (
        (totals["mass"], exact.state_mass),
        (totals["baseline"], exact.baseline_searchable),
        (totals["rotom"], exact.blind_rotom_searchable),
        (totals["ticket"], exact.blind_ticket_searchable),
        (totals["rotom_rescue"], exact.rotom_rescue_mass),
        (totals["rotom_break"], exact.rotom_break_mass),
        (totals["ticket_rescue"], exact.ticket_rescue_mass),
        (totals["ticket_break"], exact.ticket_break_mass),
        (totals["prize_failure"], exact.baseline_failure_with_target_prized),
        (totals["nonprize_failure"], exact.baseline_failure_without_target_prized),
    )
    for left, right in comparisons:
        assert_close(left, right)


def aichi_regressions() -> None:
    base = dict(
        deck_size=60,
        forced_starters=14,
        opening_hand_size=7,
        prize_count=6,
        pre_search_draws=1,
    )
    expected = {
        (1,): 0.7716248595566183,
        (2,): 0.9509406113150053,
        (2, 2): 0.9037142689348595,
        (2, 1): 0.7324139736285614,
        (2, 2, 2, 1): 0.6585095875149527,
    }

    for profile, expected_baseline in expected.items():
        result = analyze_prize_zone_recovery(target_copies=profile, **base)
        baseline = conditioned_searchability(target_copies=profile, **base)
        assert_close(result.state_mass, 1.0)
        assert_close(result.baseline_searchable, expected_baseline)
        assert_close(result.baseline_searchable, baseline)
        assert_close(result.blind_rotom_searchable, result.baseline_searchable)
        assert_close(result.blind_ticket_searchable, result.baseline_searchable)
        assert_close(result.rotom_rescue_mass, result.rotom_break_mass)
        assert_close(result.ticket_rescue_mass, result.ticket_break_mass)


def main() -> None:
    labeled_validation()
    aichi_regressions()
    print("Prize zone recovery regressions passed.")
    for profile in ((1,), (2,), (2, 2), (2, 1), (2, 2, 2, 1)):
        result = analyze_prize_zone_recovery(60, 14, profile)
        print(
            profile,
            f"baseline={100 * result.baseline_searchable:.6f}%",
            f"informed_rotom={100 * result.informed_rotom_searchable:.6f}%",
            f"informed_ticket={100 * result.informed_ticket_searchable:.6f}%",
        )


if __name__ == "__main__":
    main()
