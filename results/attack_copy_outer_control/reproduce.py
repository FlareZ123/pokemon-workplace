from __future__ import annotations

from collections import Counter
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_catalog import build as build_catalog
from attack_copy_outer_control import (
    classify_outer_control,
    evaluate_outer_control,
)


def main() -> None:
    catalog = build_catalog(ROOT / "resources")
    controlled = []
    for signature in catalog["signatures"]:
        control = classify_outer_control(signature["text"])
        if control is not None:
            controlled.append((signature, control))

    assert len(catalog["signatures"]) == 30
    assert len(controlled) == 6
    assert sum(len(row["print_ids"]) for row, _control in controlled) == 7

    by_kind = Counter(control.kind for _row, control in controlled)
    assert by_kind == Counter(
        {
            "coin_heads": 4,
            "opponent_prizes_exact": 1,
            "actor_hand_empty": 1,
        }
    )

    by_name = {row["attack_name"]: control for row, control in controlled}
    assert set(by_name) == {
        "Assist",
        "Mini-Metronome",
        "Nightcap",
        "Pendulum Influence",
        "Skill Thief",
        "Try to Imitate",
    }

    nightcap = by_name["Nightcap"]
    assert nightcap.stage == "declaration"
    assert nightcap.exact_value == 2
    assert (
        evaluate_outer_control(nightcap, opponent_prizes_remaining=2)
        == "proceed"
    )
    assert (
        evaluate_outer_control(nightcap, opponent_prizes_remaining=3)
        == "declaration_illegal"
    )

    skill_thief = by_name["Skill Thief"]
    assert skill_thief.stage == "body"
    assert evaluate_outer_control(skill_thief, actor_hand_size=0) == "proceed"
    assert (
        evaluate_outer_control(skill_thief, actor_hand_size=1)
        == "resolve_without_copy"
    )

    for name in (
        "Assist",
        "Mini-Metronome",
        "Pendulum Influence",
        "Try to Imitate",
    ):
        control = by_name[name]
        assert control.stage == "body"
        assert evaluate_outer_control(control, coin_heads=True) == "proceed"
        assert (
            evaluate_outer_control(control, coin_heads=False)
            == "resolve_without_copy"
        )
        assert evaluate_outer_control(control) == "random_outcome_required"

    print(
        {
            "copy_signatures": len(catalog["signatures"]),
            "controlled_signatures": len(controlled),
            "controlled_print_rows": sum(
                len(row["print_ids"]) for row, _control in controlled
            ),
            "kinds": dict(sorted(by_kind.items())),
        }
    )


if __name__ == "__main__":
    main()
