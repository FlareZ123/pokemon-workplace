"""Reproduce Alolan Raichu / Electrode-GX Prize-state Energy ALS."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_electro_rain_als import maximum_electro_rain_after_bomb, prize_state_matrix


def names(result):
    assert result is not None
    counts = {}
    for card in result.attached_cards:
        counts[card.name] = counts.get(card.name, 0) + 1
    return counts


def main() -> None:
    tied = maximum_electro_rain_after_bomb(3, 3)
    assert tied is not None
    assert not tied.state.condition_active_before
    assert tied.state.condition_active_after
    assert tied.state.condition_activated_by_self_ko
    assert tied.state.opponent_prizes_after == 1
    assert tied.lightning_units == 14
    assert tied.maximum_damage == 420
    assert names(tied) == {"Reversal Energy": 4, "Counter Energy": 1}

    one_ahead = maximum_electro_rain_after_bomb(2, 3)
    assert one_ahead is not None
    assert one_ahead.state.condition_activated_by_self_ko
    assert one_ahead.maximum_damage == 420

    two_ahead = maximum_electro_rain_after_bomb(1, 3)
    assert two_ahead is not None
    assert not two_ahead.state.condition_active_after
    assert two_ahead.lightning_units == 3
    assert two_ahead.maximum_damage == 90
    assert names(two_ahead)["Unit Energy LightningPsychicMetal"] == 3

    assert maximum_electro_rain_after_bomb(6, 2) is None
    assert maximum_electro_rain_after_bomb(1, 1) is None

    matrix = prize_state_matrix()
    terminal = [state for state in matrix if state.terminal_loss]
    nonterminal = [state for state in matrix if not state.terminal_loss]
    active_after = [state for state in nonterminal if state.condition_active_after]
    activated = [state for state in nonterminal if state.condition_activated_by_self_ko]
    inactive_after = [state for state in nonterminal if not state.condition_active_after]
    assert len(matrix) == 36
    assert len(terminal) == 12
    assert len(nonterminal) == 24
    assert len(active_after) == 14
    assert len(activated) == 8
    assert len(inactive_after) == 10

    switch_pairs = [
        (state.own_prizes_before, state.opponent_prizes_before)
        for state in activated
    ]
    assert switch_pairs == [
        (2, 3), (3, 3), (3, 4), (4, 4),
        (4, 5), (5, 5), (5, 6), (6, 6),
    ]

    rows = []
    for opponent in range(1, 7):
        row = []
        for own in range(1, 7):
            result = maximum_electro_rain_after_bomb(own, opponent)
            row.append("terminal" if result is None else result.maximum_damage)
        rows.append({"opponent_prizes_before": opponent, "own_prizes_1_to_6": row})

    print(json.dumps({
        "tied_3_3_max_damage": tied.maximum_damage,
        "one_prize_ahead_2_3_max_damage": one_ahead.maximum_damage,
        "two_prizes_ahead_1_3_max_damage": two_ahead.maximum_damage,
        "terminal_prize_pairs": len(terminal),
        "nonterminal_active_pairs": len(active_after),
        "self_ko_activation_pairs": switch_pairs,
        "nonterminal_inactive_pairs": len(inactive_after),
        "damage_matrix": rows,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
