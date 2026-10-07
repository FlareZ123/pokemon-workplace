from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_capacity_effect_catalog import scan_bench_capacity_effects  # noqa: E402
from bench_capacity_schedule import ReleaseBudget, evaluate_bench_schedule  # noqa: E402


def main() -> None:
    result = scan_bench_capacity_effects(ROOT / "resources")
    assert result["print_count"] == 17
    assert result["signature_count"] == 8
    assert result["unique_names"] == 7
    assert result["gameplay_variants"] == 9
    assert result["names"] == [
        "Area Zero Underdepths",
        "Collapsed Stadium",
        "Eternatus VMAX",
        "Glimmora ex",
        "Parallel City",
        "Sky Field",
        "Sudowoodo",
    ]

    by_name: dict[str, set[tuple[int, str]]] = {}
    for row in result["signatures"]:
        by_name.setdefault(row["name"], set()).add((row["capacity"], row["scope"]))
    assert by_name["Eternatus VMAX"] == {(8, "self")}
    assert by_name["Parallel City"] == {(3, "chosen_side")}
    assert by_name["Collapsed Stadium"] == {(4, "both")}
    assert by_name["Glimmora ex"] == {(3, "opponent")}
    assert by_name["Sudowoodo"] == {(4, "opponent")}
    assert by_name["Area Zero Underdepths"] == {(8, "both")}
    assert by_name["Sky Field"] == {(8, "both")}

    print(
        f"prints={result['print_count']} signatures={result['signature_count']} "
        f"names={result['unique_names']} variants={result['gameplay_variants']}"
    )
    for row in result["signatures"]:
        print(
            f"{row['name']}: capacity={row['capacity']} scope={row['scope']} "
            f"conditional={row['conditional']} active={row['active_dependent']}"
        )

    print("\nfour persistent core slots, three support activations, no release")
    for capacity in (4, 5, 8):
        outcome = evaluate_bench_schedule(
            support_activations=3,
            core_bench_slots=4,
            max_turns=1,
            release_budget=ReleaseBudget(),
            bench_capacity=capacity,
        )
        print(f"capacity={capacity}: max={outcome.max_activations} goal={outcome.goal_reached}")


if __name__ == "__main__":
    main()
