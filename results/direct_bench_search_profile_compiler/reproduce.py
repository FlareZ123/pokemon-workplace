from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from direct_bench_search_profile_compiler import compile_direct_bench_search_profiles


def main() -> None:
    rows = compile_direct_bench_search_profiles(ROOT / "resources")

    assert len(rows) == 101
    assert len({row.name for row in rows}) == 76

    breakdown = Counter(
        (
            row.source_kind,
            row.output.max_units,
            row.explicit_up_to,
        )
        for row in rows
    )
    assert breakdown == Counter(
        {
            ("attack", 1, False): 40,
            ("attack", 2, False): 6,
            ("attack", 2, True): 42,
            ("attack", 3, True): 7,
            ("trainer", 1, False): 5,
            ("trainer", 2, True): 1,
        }
    )

    nest_ball = tuple(row for row in rows if row.name == "Nest Ball")
    assert tuple(row.card_id for row in nest_ball) == (
        "sm1-123",
        "sm1-158",
        "sv1-181",
        "sv1-255",
        "sv4pt5-84",
    )
    assert all(row.action_class == "Item" for row in nest_ball)
    assert all(row.output.max_units == 1 for row in nest_ball)
    assert all(row.play_condition is None for row in nest_ball)

    vip = tuple(row for row in rows if row.name == "Battle VIP Pass")
    assert len(vip) == 1
    assert vip[0].card_id == "swsh8-225"
    assert vip[0].output.max_units == 2
    assert vip[0].explicit_up_to
    assert vip[0].play_condition == "You can use this card only during your first turn."

    old_emolga = tuple(
        row
        for row in rows
        if row.name == "Emolga"
        and row.card_id in {"bw11-49", "bw11-RC23", "bw6-45"}
    )
    assert len(old_emolga) == 3
    assert all(row.source_name == "Call for Family" for row in old_emolga)
    assert all(
        row.output.max_units == 2 and not row.explicit_up_to
        for row in old_emolga
    )
    assert all(row.attack_cost == ("Colorless",) for row in old_emolga)

    compiled_names = {row.name for row in rows}
    for excluded in (
        "Buddy-Buddy Poffin",
        "Dream Ball",
        "Furisode Girl",
        "Precious Trolley",
        "Professor Oak's Setup",
        "Single Strike Style Mustard",
    ):
        assert excluded not in compiled_names

    print("direct Bench compiler regression passed")
    print(f"profiles={len(rows)} unique_names={len(compiled_names)}")
    for key, count in sorted(breakdown.items()):
        print(key, count)


if __name__ == "__main__":
    main()
