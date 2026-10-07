"""Deadline-sensitive Bench release execution across turn boundaries."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from bounded_state_planner import shortest_bounded_plan
from turn_action_budget import TurnAction, TurnActionBudget

ReleaseClass = Literal["supporter", "item", "attack", "ability"]

@dataclass(frozen=True)
class ReleaseProfile:
    name: str
    action_class: ReleaseClass
    satisfies_current_attack_objective: bool = False

@dataclass(frozen=True)
class DeadlineState:
    own_turn: int
    bench_occupancy: int
    bench_capacity: int
    spent_support_present: bool
    release_used: bool
    current_attack_done: bool
    next_supporter_done: bool
    required_bench_entry_done: bool
    budget: TurnActionBudget


def _replace(state: DeadlineState, **changes) -> DeadlineState:
    values = state.__dict__ | changes
    return DeadlineState(**values)


def release_action(profile: ReleaseProfile):
    def action(state: DeadlineState):
        if state.release_used or not state.spent_support_present or state.budget.turn_ended:
            return ()
        budget = state.budget
        current_attack_done = state.current_attack_done
        if profile.action_class == "supporter":
            budget = budget.consume(TurnAction.SUPPORTER)
            if budget is None:
                return ()
        elif profile.action_class == "attack":
            budget = budget.consume(TurnAction.ATTACK)
            if budget is None:
                return ()
            current_attack_done = current_attack_done or profile.satisfies_current_attack_objective
        elif profile.action_class not in {"item", "ability"}:
            raise ValueError(profile.action_class)
        return ((
            f"{profile.name} releases spent support",
            _replace(
                state,
                bench_occupancy=state.bench_occupancy - 1,
                spent_support_present=False,
                release_used=True,
                current_attack_done=current_attack_done,
                budget=budget,
            ),
        ),)
    return action


def current_attack_action(state: DeadlineState):
    if state.own_turn != 0 or state.current_attack_done:
        return ()
    budget = state.budget.consume(TurnAction.ATTACK)
    if budget is None:
        return ()
    return (("use distinct required attack", _replace(state, current_attack_done=True, budget=budget)),)


def next_supporter_action(state: DeadlineState):
    if state.own_turn != 1 or state.next_supporter_done:
        return ()
    budget = state.budget.consume(TurnAction.SUPPORTER)
    if budget is None:
        return ()
    return (("play next-turn required Supporter", _replace(state, next_supporter_done=True, budget=budget)),)


def bench_entry_action(available_turn: int, deadline: int):
    def action(state: DeadlineState):
        if state.required_bench_entry_done or state.budget.turn_ended:
            return ()
        if state.own_turn < available_turn or state.own_turn > deadline or state.bench_occupancy >= state.bench_capacity:
            return ()
        return ((
            "Bench required Pokémon",
            _replace(
                state,
                bench_occupancy=state.bench_occupancy + 1,
                required_bench_entry_done=True,
            ),
        ),)
    return action


def _fresh_budget_from(state: DeadlineState) -> TurnActionBudget:
    return TurnActionBudget(
        supporter_play_limit=state.budget.supporter_play_limit,
        stadium_play_limit=state.budget.stadium_play_limit,
        manual_energy_attachment_limit=state.budget.manual_energy_attachment_limit,
        retreat_limit=state.budget.retreat_limit,
    )


def advance_to_next_own_turn(state: DeadlineState):
    if state.own_turn != 0:
        return ()
    if not state.budget.turn_ended:
        return ()
    return ((
        "advance to next own turn",
        _replace(state, own_turn=1, budget=_fresh_budget_from(state)),
    ),)


def voluntary_end(state: DeadlineState):
    if state.own_turn != 0 or state.budget.turn_ended:
        return ()
    budget = state.budget.consume(TurnAction.END_TURN)
    if budget is None:
        return ()
    return (("end current turn", _replace(state, budget=budget)),)


def plan(
    profile: ReleaseProfile,
    *,
    bench_available_turn: int,
    bench_deadline: int,
    require_current_attack: bool,
    require_next_supporter: bool,
):
    initial = DeadlineState(
        own_turn=0,
        bench_occupancy=5,
        bench_capacity=5,
        spent_support_present=True,
        release_used=False,
        current_attack_done=not require_current_attack,
        next_supporter_done=not require_next_supporter,
        required_bench_entry_done=False,
        budget=TurnActionBudget(),
    )
    witness = shortest_bounded_plan(
        initial,
        (
            release_action(profile),
            current_attack_action,
            next_supporter_action,
            bench_entry_action(bench_available_turn, bench_deadline),
            voluntary_end,
            advance_to_next_own_turn,
        ),
        lambda s: (
            s.required_bench_entry_done
            and s.current_attack_done
            and s.next_supporter_done
            and s.own_turn <= bench_deadline
        ),
        max_depth=7,
    )
    return None if witness is None else witness.labels


def build_result():
    item = ReleaseProfile("deterministic Item", "item")
    supporter = ReleaseProfile("Supporter pickup", "supporter")
    attack = ReleaseProfile("release attack", "attack")
    attack_aligned = ReleaseProfile("release attack", "attack", satisfies_current_attack_objective=True)

    scenarios = {
        "same_turn_entry_item": plan(item, bench_available_turn=0, bench_deadline=0, require_current_attack=False, require_next_supporter=False),
        "same_turn_entry_supporter": plan(supporter, bench_available_turn=0, bench_deadline=0, require_current_attack=False, require_next_supporter=False),
        "same_turn_entry_attack": plan(attack, bench_available_turn=0, bench_deadline=0, require_current_attack=False, require_next_supporter=False),
        "next_turn_entry_attack_plus_next_supporter": plan(attack, bench_available_turn=1, bench_deadline=1, require_current_attack=False, require_next_supporter=True),
        "next_turn_entry_supporter_plus_next_supporter": plan(supporter, bench_available_turn=1, bench_deadline=1, require_current_attack=False, require_next_supporter=True),
        "next_turn_entry_attack_plus_distinct_current_attack": plan(attack, bench_available_turn=1, bench_deadline=1, require_current_attack=True, require_next_supporter=False),
        "next_turn_entry_aligned_attack_objective": plan(attack_aligned, bench_available_turn=1, bench_deadline=1, require_current_attack=True, require_next_supporter=False),
        "next_turn_entry_item_plus_distinct_current_attack": plan(item, bench_available_turn=1, bench_deadline=1, require_current_attack=True, require_next_supporter=False),
    }

    assert scenarios["same_turn_entry_item"] is not None
    assert scenarios["same_turn_entry_supporter"] is not None
    assert scenarios["same_turn_entry_attack"] is None
    assert scenarios["next_turn_entry_attack_plus_next_supporter"] is not None
    assert scenarios["next_turn_entry_supporter_plus_next_supporter"] is not None
    assert scenarios["next_turn_entry_attack_plus_distinct_current_attack"] is None
    assert scenarios["next_turn_entry_aligned_attack_objective"] is not None
    assert scenarios["next_turn_entry_item_plus_distinct_current_attack"] is not None

    return {
        "deadline_semantics": {
            "0": "required Bench entrant must be placed during the current turn",
            "1": "required Bench entrant becomes available on the player's next own turn and must be placed that turn",
        },
        "scenarios": scenarios,
        "findings": {
            "attack_release": "misses a same-turn Bench deadline but can preload Bench capacity for the next own turn",
            "supporter_release": "its quota cost does not carry across the turn boundary; a next-turn required Supporter gets a fresh quota",
            "attack_contention": "an attack release conflicts with a distinct current-turn attack objective unless the release attack itself satisfies that objective",
            "item_release": "a pre-attack Item release can preserve the current attack window while preloading future Bench capacity",
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
    parser.add_argument("--output", type=Path, default=Path("results/bench_release_deadline_geometry/model.json"))
    args = parser.parse_args()
    result = build_result()
    atomic_write_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
