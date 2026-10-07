from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_capacity_schedule import ReleaseBudget, evaluate_bench_schedule  # noqa: E402


def validate_closed_forms() -> None:
    for core in range(0, 5):
        q = 5 - core
        for turns in range(1, 5):
            for releases in range(0, 5):
                target = 20

                item = evaluate_bench_schedule(
                    support_activations=target,
                    core_bench_slots=core,
                    max_turns=turns,
                    release_budget=ReleaseBudget(item=releases),
                )
                assert item.max_activations == q + releases

                ability = evaluate_bench_schedule(
                    support_activations=target,
                    core_bench_slots=core,
                    max_turns=turns,
                    release_budget=ReleaseBudget(ability=releases),
                )
                assert ability.max_activations == q + releases

                supporter = evaluate_bench_schedule(
                    support_activations=target,
                    core_bench_slots=core,
                    max_turns=turns,
                    release_budget=ReleaseBudget(supporter=releases),
                )
                assert supporter.max_activations == q + min(releases, turns)

                attack = evaluate_bench_schedule(
                    support_activations=target,
                    core_bench_slots=core,
                    max_turns=turns,
                    release_budget=ReleaseBudget(attack=releases),
                )
                assert attack.max_activations == q + min(releases, turns - 1)


def main() -> None:
    validate_closed_forms()

    print("Four core Bench slots, one transactional slot, three desired support activations")
    scenarios = (
        ("no release", ReleaseBudget()),
        ("2 Item releases", ReleaseBudget(item=2)),
        ("2 Ability releases", ReleaseBudget(ability=2)),
        ("2 Supporter releases", ReleaseBudget(supporter=2)),
        ("2 attack releases", ReleaseBudget(attack=2)),
    )
    for turns in (1, 2, 3):
        print(f"deadline: turn {turns}")
        for label, budget in scenarios:
            result = evaluate_bench_schedule(
                support_activations=3,
                core_bench_slots=4,
                max_turns=turns,
                release_budget=budget,
            )
            print(
                f"  {label}: max={result.max_activations} "
                f"goal={result.goal_reached} earliest={result.earliest_goal_turn}"
            )

    mixed = evaluate_bench_schedule(
        support_activations=5,
        core_bench_slots=4,
        max_turns=2,
        release_budget=ReleaseBudget(item=1, supporter=1, attack=2),
    )
    assert mixed.max_activations == 4
    print("mixed 2-turn budget:", mixed)


if __name__ == "__main__":
    main()
