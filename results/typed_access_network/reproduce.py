"""Reproduce typed Gladion access-network regression cases."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from typed_access_network import make_state, shortest_gladion_line  # noqa: E402


def line_labels(result: tuple[list[str], object] | None) -> list[str] | None:
    if result is None:
        return None
    return result[0]


def main() -> None:
    quick_ball = make_state(
        {
            "Quick Ball": "hand",
            "Fodder": "hand",
            "Tapu Lele-GX": "deck",
            "Gladion": "deck",
        }
    )
    nest_ball = make_state(
        {
            "Nest Ball": "hand",
            "Tapu Lele-GX": "deck",
            "Gladion": "deck",
        }
    )
    compressor_seeker = make_state(
        {
            "Battle Compressor": "hand",
            "VS Seeker": "hand",
            "Gladion": "deck",
        }
    )
    skyla = make_state(
        {
            "Skyla": "hand",
            "Gladion": "deck",
        }
    )
    jigglypuff_lead = make_state(
        {
            "Jigglypuff": "active",
            "Gladion": "deck",
        },
        lead_ready=True,
    )

    expected_quick = [
        "Quick Ball -> Tapu Lele-GX to hand",
        "Play Tapu Lele-GX from hand onto Bench",
        "Play Gladion",
    ]
    expected_compressor = [
        "Battle Compressor -> Gladion to discard",
        "VS Seeker -> Gladion to hand",
        "Play Gladion",
    ]
    expected_skyla_future = [
        "Play Skyla -> Gladion to hand",
        "Advance to next Supporter window",
        "Play Gladion",
    ]
    expected_lead_future = [
        "Use Jigglypuff Lead -> Gladion to hand; attack ends turn",
        "Play Gladion",
    ]

    assert line_labels(shortest_gladion_line(quick_ball)) == expected_quick
    assert shortest_gladion_line(nest_ball) is None
    assert line_labels(shortest_gladion_line(compressor_seeker)) == expected_compressor
    assert shortest_gladion_line(skyla) is None
    assert line_labels(
        shortest_gladion_line(skyla, max_future_windows=1)
    ) == expected_skyla_future
    assert shortest_gladion_line(jigglypuff_lead) is None
    assert line_labels(
        shortest_gladion_line(jigglypuff_lead, max_future_windows=1)
    ) == expected_lead_future

    quick_ability_lock = make_state(
        {
            "Quick Ball": "hand",
            "Fodder": "hand",
            "Tapu Lele-GX": "deck",
            "Gladion": "deck",
        },
        abilities_allowed=False,
    )
    quick_full_bench = make_state(
        {
            "Quick Ball": "hand",
            "Fodder": "hand",
            "Tapu Lele-GX": "deck",
            "Gladion": "deck",
        },
        bench_count=5,
    )
    compressor_item_lock = make_state(
        {
            "Battle Compressor": "hand",
            "VS Seeker": "hand",
            "Gladion": "deck",
        },
        items_allowed=False,
    )
    lead_attack_lock = make_state(
        {
            "Jigglypuff": "active",
            "Gladion": "deck",
        },
        lead_ready=True,
        attacks_allowed=False,
    )

    assert shortest_gladion_line(quick_ability_lock) is None
    assert shortest_gladion_line(quick_full_bench) is None
    assert shortest_gladion_line(compressor_item_lock) is None
    assert shortest_gladion_line(lead_attack_lock, max_future_windows=1) is None

    cases = [
        ("Quick Ball -> Tapu Lele-GX", shortest_gladion_line(quick_ball)),
        ("Nest Ball -> Tapu Lele-GX", shortest_gladion_line(nest_ball)),
        ("Battle Compressor -> VS Seeker", shortest_gladion_line(compressor_seeker)),
        ("Skyla, current window", shortest_gladion_line(skyla)),
        ("Skyla, one future window", shortest_gladion_line(skyla, max_future_windows=1)),
        ("Jigglypuff Lead, current window", shortest_gladion_line(jigglypuff_lead)),
        ("Jigglypuff Lead, one future window", shortest_gladion_line(jigglypuff_lead, max_future_windows=1)),
        ("Quick Ball under Ability lock", shortest_gladion_line(quick_ability_lock)),
        ("Quick Ball with full Bench", shortest_gladion_line(quick_full_bench)),
        ("Compressor/Seeker under Item lock", shortest_gladion_line(compressor_item_lock)),
        ("Jigglypuff Lead while attacks are disabled", shortest_gladion_line(lead_attack_lock, max_future_windows=1)),
    ]

    for name, result in cases:
        labels = line_labels(result)
        if labels is None:
            print(f"{name}: no Gladion play in allowed window(s)")
        else:
            print(f"{name}: {' -> '.join(labels)}")


if __name__ == "__main__":
    main()
