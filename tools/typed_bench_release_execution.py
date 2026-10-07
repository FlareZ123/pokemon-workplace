"""Compose persistent Bench occupancy with typed release-action costs.

This extends the conservative bench-release catalog with a small execution model.
A release edge is represented by its action class rather than as a generic free
transition. The model asks whether a full Bench containing one spent support
Pokémon can be cleared early enough to both play a required Supporter and Bench a
required Pokémon on the same turn.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bounded_state_planner import shortest_bounded_plan
from interturn_bench_debt_policy import break_even_collision_probability, hit_probability, pct
from turn_action_budget import TurnAction, TurnActionBudget

ReleaseClass = Literal["supporter", "item", "attack", "ability"]


@dataclass(frozen=True)
class ReleaseProfile:
    name: str
    action_class: ReleaseClass
    stochastic_success: Fraction = Fraction(1, 1)
    requires_item_access: bool = False
    requires_ability_ready: bool = False


@dataclass(frozen=True)
class ReleaseState:
    bench_occupancy: int
    bench_capacity: int
    spent_support_present: bool
    release_used: bool
    required_supporter_done: bool
    required_bench_entry_done: bool
    items_allowed: bool
    ability_ready: bool
    budget: TurnActionBudget


def release_action(profile: ReleaseProfile):
    def action(state: ReleaseState):
        if state.release_used or not state.spent_support_present or state.budget.turn_ended:
            return ()
        if profile.requires_item_access and not state.items_allowed:
            return ()
        if profile.requires_ability_ready and not state.ability_ready:
            return ()

        budget = state.budget
        if profile.action_class == "supporter":
            budget = budget.consume(TurnAction.SUPPORTER)
            if budget is None:
                return ()
        elif profile.action_class == "attack":
            budget = budget.consume(TurnAction.ATTACK)
            if budget is None:
                return ()
        elif profile.action_class not in {"item", "ability"}:
            raise ValueError(f"unsupported release class: {profile.action_class}")

        return ((
            f"{profile.name} releases spent support",
            ReleaseState(
                bench_occupancy=state.bench_occupancy - 1,
                bench_capacity=state.bench_capacity,
                spent_support_present=False,
                release_used=True,
                required_supporter_done=state.required_supporter_done,
                required_bench_entry_done=state.required_bench_entry_done,
                items_allowed=state.items_allowed,
                ability_ready=state.ability_ready,
                budget=budget,
            ),
        ),)

    return action


def required_supporter_action(state: ReleaseState):
    if state.required_supporter_done:
        return ()
    budget = state.budget.consume(TurnAction.SUPPORTER)
    if budget is None:
        return ()
    return ((
        "play required Supporter",
        ReleaseState(
            bench_occupancy=state.bench_occupancy,
            bench_capacity=state.bench_capacity,
            spent_support_present=state.spent_support_present,
            release_used=state.release_used,
            required_supporter_done=True,
            required_bench_entry_done=state.required_bench_entry_done,
            items_allowed=state.items_allowed,
            ability_ready=state.ability_ready,
            budget=budget,
        ),
    ),)


def required_bench_entry_action(state: ReleaseState):
    if state.required_bench_entry_done or state.budget.turn_ended:
        return ()
    if state.bench_occupancy >= state.bench_capacity:
        return ()
    return ((
        "Bench required Pokémon",
        ReleaseState(
            bench_occupancy=state.bench_occupancy + 1,
            bench_capacity=state.bench_capacity,
            spent_support_present=state.spent_support_present,
            release_used=state.release_used,
            required_supporter_done=state.required_supporter_done,
            required_bench_entry_done=True,
            items_allowed=state.items_allowed,
            ability_ready=state.ability_ready,
            budget=state.budget,
        ),
    ),)


def collision_plan(
    profile: ReleaseProfile,
    *,
    supporter_limit: int = 1,
    items_allowed: bool = True,
    ability_ready: bool = True,
):
    initial = ReleaseState(
        bench_occupancy=5,
        bench_capacity=5,
        spent_support_present=True,
        release_used=False,
        required_supporter_done=False,
        required_bench_entry_done=False,
        items_allowed=items_allowed,
        ability_ready=ability_ready,
        budget=TurnActionBudget(supporter_play_limit=supporter_limit),
    )
    witness = shortest_bounded_plan(
        initial,
        (release_action(profile), required_supporter_action, required_bench_entry_action),
        lambda s: s.required_supporter_done and s.required_bench_entry_done,
        max_depth=4,
    )
    return None if witness is None else witness.labels


def repeated_coin_release_success(attempts: int) -> Fraction:
    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    return Fraction(1, 1) - Fraction(1, 2**attempts)


def collision_break_even_with_release(
    base_success: Fraction,
    support_success: Fraction,
    release_success: Fraction,
):
    if not (Fraction(0, 1) <= release_success <= Fraction(1, 1)):
        raise ValueError("release_success must be between zero and one")
    base_threshold = break_even_collision_probability(base_success, support_success)
    failure = Fraction(1, 1) - release_success
    if failure == 0:
        return None
    return base_threshold / failure


def build_result():
    profiles = {
        "supporter": ReleaseProfile("AZ/Penny-like Supporter", "supporter"),
        "deterministic_item": ReleaseProfile(
            "Scoop Up Cyclone",
            "item",
            requires_item_access=True,
        ),
        "coin_item": ReleaseProfile(
            "Super Scoop Up (heads branch)",
            "item",
            stochastic_success=Fraction(1, 2),
            requires_item_access=True,
        ),
        "attack": ReleaseProfile("Pelipper Courier", "attack"),
        "ability": ReleaseProfile(
            "Corviknight Flying Taxi",
            "ability",
            requires_ability_ready=True,
        ),
    }

    mechanical = {
        "supporter_limit_1": collision_plan(profiles["supporter"], supporter_limit=1),
        "supporter_limit_2": collision_plan(profiles["supporter"], supporter_limit=2),
        "deterministic_item": collision_plan(profiles["deterministic_item"]),
        "deterministic_item_under_item_lock": collision_plan(
            profiles["deterministic_item"], items_allowed=False
        ),
        "coin_item_heads_branch": collision_plan(profiles["coin_item"]),
        "attack_release": collision_plan(profiles["attack"]),
        "ability_release_ready": collision_plan(profiles["ability"], ability_ready=True),
        "ability_release_not_ready": collision_plan(profiles["ability"], ability_ready=False),
    }

    assert mechanical["supporter_limit_1"] is None
    assert mechanical["supporter_limit_2"] is not None
    assert mechanical["deterministic_item"] is not None
    assert mechanical["deterministic_item_under_item_lock"] is None
    assert mechanical["coin_item_heads_branch"] is not None
    assert mechanical["attack_release"] is None
    assert mechanical["ability_release_ready"] is not None
    assert mechanical["ability_release_not_ready"] is None

    base = hit_probability(40, 4, 4)
    support = hit_probability(40, 4, 5)
    coin_rows = []
    for attempts in range(0, 5):
        release_success = repeated_coin_release_success(attempts)
        threshold = collision_break_even_with_release(base, support, release_success)
        coin_rows.append(
            {
                "attempts": attempts,
                "release_success_fraction": f"{release_success.numerator}/{release_success.denominator}",
                "release_success_percent": pct(release_success),
                "break_even_collision_fraction": None if threshold is None else f"{threshold.numerator}/{threshold.denominator}",
                "break_even_collision_percent": None if threshold is None else pct(threshold),
                "support_wins_for_all_collision_probabilities": threshold is None or threshold >= 1,
            }
        )

    return {
        "card_text_anchors": {
            "supporter_release": "Penny sv1-183: put 1 of your Basic Pokémon and all attached cards into your hand; Penny is a Supporter.",
            "deterministic_item_release": "Scoop Up Cyclone bw10-95: put 1 of your Pokémon and all attached cards into your hand; it is an ACE SPEC Item.",
            "stochastic_item_release": "Super Scoop Up bw1-103: flip a coin; on heads, put 1 of your Pokémon and all attached cards into your hand.",
            "attack_release": "Pelipper sm1-38 / Courier: put 1 of your Benched Pokémon and all cards attached to it into your hand.",
            "ability_release": "Corviknight swsh3-156 / Flying Taxi: when played from hand to evolve, it may put another of your Pokémon and all attached cards into your hand.",
        },
        "mechanical_same_turn_collision": mechanical,
        "coin_release_probability": {
            "toy_setup_base_success_percent": pct(base),
            "toy_setup_support_success_percent": pct(support),
            "ordinary_no_release_break_even_collision_percent": pct(
                break_even_collision_probability(base, support)
            ),
            "super_scoop_up_attempts": coin_rows,
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
    parser.add_argument("--output", type=Path, default=Path("results/typed_bench_release_execution/model.json"))
    args = parser.parse_args()
    result = build_result()
    atomic_write_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
