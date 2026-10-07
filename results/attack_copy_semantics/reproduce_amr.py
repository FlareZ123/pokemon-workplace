from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_amr import build, top_card_hit_probability, top_n_hit_probability


def profile_for(result: dict, attack_name: str) -> list[dict]:
    return [row for row in result["profiles"] if row["attack_name"] == attack_name]


def main() -> None:
    result = build(ROOT / "resources")
    counts = result["counts"]

    assert counts["copy_signatures"] == 30
    assert counts["signatures_with_any_extra_gate"] == 14
    assert counts["signatures_without_listed_extra_gate"] == 16
    assert counts["gate_flags"] == {
        "adversarial_choice": 1,
        "coin_flip_gate": 4,
        "copied_energy_gate": 2,
        "empty_hand_gate": 1,
        "opponent_hand_observation": 1,
        "opponent_top_10_sample": 1,
        "optional_copy": 2,
        "post_copy_continuation": 1,
        "pre_copy_discard": 2,
        "previous_turn_attack_gate": 2,
        "prize_count_gate": 1,
        "random_top_card_sample": 1,
    }

    assert top_n_hit_probability(50, 1, 10) == Fraction(1, 5)
    assert top_n_hit_probability(50, 2, 10) == Fraction(89, 245)
    assert top_n_hit_probability(50, 4, 10) == Fraction(13891, 23030)
    assert top_n_hit_probability(8, 3, 10) == Fraction(1, 1)
    assert top_n_hit_probability(50, 0, 10) == Fraction(0, 1)
    assert top_card_hit_probability(50, 4) == Fraction(2, 25)

    assert "copied_energy_gate" in profile_for(result, "Copy Anything")[0]["active_gate_flags"]
    assert "copied_energy_gate" in profile_for(result, "Imittack")[0]["active_gate_flags"]
    assert "post_copy_continuation" in profile_for(result, "Haughty Order")[0]["active_gate_flags"]
    assert "adversarial_choice" in profile_for(result, "Mimed Games")[0]["active_gate_flags"]
    assert "coin_flip_gate" in profile_for(result, "Assist")[0]["active_gate_flags"]

    print("attack-copy AMR regressions passed")
    print(counts)


if __name__ == "__main__":
    main()
