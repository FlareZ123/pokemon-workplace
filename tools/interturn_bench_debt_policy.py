"""Exact finite-horizon model for Bench debt colliding with Supporter bandwidth.

The model isolates a common Expanded pattern: a one-shot support Pokémon occupies
what becomes the last Bench slot. A later AZ can remove that spent support, but AZ
itself consumes a Supporter play. If the same future turn also requires another
Supporter and a new Bench entrant, ordinary one-Supporter bandwidth cannot execute
the line. A two-Supporter quota restores it.

This is a deliberately small semantic island. It composes the repository's generic
TurnActionBudget with the bounded planner, then layers exact hypergeometric setup
probabilities over the mechanically validated continuation states.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bounded_state_planner import shortest_bounded_plan
from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class FutureTurnState:
    bench_occupancy: int
    bench_capacity: int
    spent_support_present: bool
    required_supporter_done: bool
    required_bench_entry_done: bool
    budget: TurnActionBudget


def _az_cleanup(state: FutureTurnState):
    if not state.spent_support_present:
        return ()
    next_budget = state.budget.consume(TurnAction.SUPPORTER)
    if next_budget is None:
        return ()
    return ((
        "AZ removes spent support",
        FutureTurnState(
            bench_occupancy=state.bench_occupancy - 1,
            bench_capacity=state.bench_capacity,
            spent_support_present=False,
            required_supporter_done=state.required_supporter_done,
            required_bench_entry_done=state.required_bench_entry_done,
            budget=next_budget,
        ),
    ),)


def _required_supporter(state: FutureTurnState):
    if state.required_supporter_done:
        return ()
    next_budget = state.budget.consume(TurnAction.SUPPORTER)
    if next_budget is None:
        return ()
    return ((
        "play required Supporter",
        FutureTurnState(
            bench_occupancy=state.bench_occupancy,
            bench_capacity=state.bench_capacity,
            spent_support_present=state.spent_support_present,
            required_supporter_done=True,
            required_bench_entry_done=state.required_bench_entry_done,
            budget=next_budget,
        ),
    ),)


def _required_bench_entry(state: FutureTurnState):
    if state.required_bench_entry_done or state.bench_occupancy >= state.bench_capacity:
        return ()
    return ((
        "Bench required Pokémon",
        FutureTurnState(
            bench_occupancy=state.bench_occupancy + 1,
            bench_capacity=state.bench_capacity,
            spent_support_present=state.spent_support_present,
            required_supporter_done=state.required_supporter_done,
            required_bench_entry_done=True,
            budget=state.budget,
        ),
    ),)


def continuation_plan(*, spent_support_present: bool, supporter_limit: int, require_supporter: bool):
    occupancy = 5 if spent_support_present else 4
    initial = FutureTurnState(
        bench_occupancy=occupancy,
        bench_capacity=5,
        spent_support_present=spent_support_present,
        required_supporter_done=not require_supporter,
        required_bench_entry_done=False,
        budget=TurnActionBudget(supporter_play_limit=supporter_limit),
    )
    goal = lambda s: s.required_supporter_done and s.required_bench_entry_done
    witness = shortest_bounded_plan(
        initial,
        (_az_cleanup, _required_supporter, _required_bench_entry),
        goal,
        max_depth=4,
    )
    return None if witness is None else witness.labels


def hit_probability(deck_cards: int, outs: int, draws: int) -> Fraction:
    if not (0 <= outs <= deck_cards):
        raise ValueError("outs must be between zero and deck size")
    if not (0 <= draws <= deck_cards):
        raise ValueError("draws must be between zero and deck size")
    if outs == 0 or draws == 0:
        return Fraction(0, 1)
    if deck_cards - outs < draws:
        return Fraction(1, 1)
    return Fraction(1, 1) - Fraction(
        math.comb(deck_cards - outs, draws),
        math.comb(deck_cards, draws),
    )


def break_even_collision_probability(base_success: Fraction, support_success: Fraction) -> Fraction:
    if support_success <= 0:
        raise ValueError("support_success must be positive")
    if base_success > support_success:
        raise ValueError("support line must weakly improve immediate success")
    return Fraction(1, 1) - base_success / support_success


def pct(value: Fraction) -> float:
    return 100.0 * value.numerator / value.denominator


def scenario(deck_cards: int, outs: int, base_draws: int, support_draws: int):
    base = hit_probability(deck_cards, outs, base_draws)
    support = hit_probability(deck_cards, outs, support_draws)
    threshold = break_even_collision_probability(base, support)
    return {
        "deck_cards": deck_cards,
        "outs": outs,
        "base_draws": base_draws,
        "support_draws": support_draws,
        "base_success_fraction": f"{base.numerator}/{base.denominator}",
        "base_success_percent": pct(base),
        "support_success_fraction": f"{support.numerator}/{support.denominator}",
        "support_success_percent": pct(support),
        "immediate_gain_pp": pct(support - base),
        "break_even_collision_fraction": f"{threshold.numerator}/{threshold.denominator}",
        "break_even_collision_percent": pct(threshold),
    }


def build_result():
    mechanical = {
        "no_spent_support_limit_1": continuation_plan(
            spent_support_present=False,
            supporter_limit=1,
            require_supporter=True,
        ),
        "spent_support_entry_only_limit_1": continuation_plan(
            spent_support_present=True,
            supporter_limit=1,
            require_supporter=False,
        ),
        "spent_support_plus_required_supporter_limit_1": continuation_plan(
            spent_support_present=True,
            supporter_limit=1,
            require_supporter=True,
        ),
        "spent_support_plus_required_supporter_limit_2": continuation_plan(
            spent_support_present=True,
            supporter_limit=2,
            require_supporter=True,
        ),
    }
    assert mechanical["no_spent_support_limit_1"] is not None
    assert mechanical["spent_support_entry_only_limit_1"] == (
        "AZ removes spent support",
        "Bench required Pokémon",
    )
    assert mechanical["spent_support_plus_required_supporter_limit_1"] is None
    assert mechanical["spent_support_plus_required_supporter_limit_2"] is not None

    thresholds = [
        scenario(40, 4, 2, 5),
        scenario(40, 4, 4, 5),
        scenario(40, 4, 5, 6),
    ]
    return {
        "card_text_anchors": {
            "spent_support_example": "Crobat V swsh3-104: Dark Asset triggers when played from hand to Bench and the Pokémon remains in play afterward.",
            "cleanup_example": "AZ xy4-91: put 1 Pokémon into your hand; AZ is a Supporter.",
            "item_cleanup_counterexample": "Scoop Up Net swsh2-165 cannot target Pokémon V or Pokémon-GX, so it cannot clear Crobat V or Dedenne-GX.",
            "two_supporter_quota_example": "Magnezone bw8-46: Dual Brains allows 2 Supporter cards during your turn.",
        },
        "mechanical_continuation": mechanical,
        "probability_model": {
            "interpretation": "Immediate setup succeeds if at least one of O outs appears in D random draws from an N-card deck. A future collision branch requires both AZ cleanup and another Supporter before a required Bench entry. All other future branches are assumed solvable.",
            "ordinary_quota_support_joint_success": "support_success * (1 - collision_probability)",
            "no_support_joint_success": "base_success",
            "two_supporter_quota_support_joint_success": "support_success",
            "break_even_formula": "collision_probability = 1 - base_success / support_success",
            "threshold_examples": thresholds,
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
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp_file:
                json.dump(payload, tmp_file, indent=2, ensure_ascii=False)
                tmp_file.write("\n")
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/interturn_bench_debt_policy/model.json"))
    args = parser.parse_args()
    result = build_result()
    atomic_write_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
