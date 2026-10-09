"""Sensitivity scan of joint Beheeyem staging/Nest reserve over Basic counts."""

from __future__ import annotations

from collections import Counter
import json

from reproduce import joint_access


def main() -> None:
    rows = []
    winner_counts: Counter[int] = Counter()
    for elgyem in (2, 3, 4):
        for partner in (1, 2, 3, 4):
            candidates = []
            for vip in range(5):
                nest = 4 - vip
                first_turn, joint = joint_access(
                    vip,
                    nest,
                    elgyem_copies=elgyem,
                    partner_copies=partner,
                )
                candidates.append((vip, first_turn, joint))

            best = max(candidates, key=lambda row: row[2])
            stage_best = max(candidates, key=lambda row: row[1])
            assert stage_best[0] == 4
            assert candidates[-1][2] == 0
            assert best[0] in {1, 2}

            winner_counts[best[0]] += 1
            rows.append({
                "elgyem": elgyem,
                "partner_basic": partner,
                "best_vip": best[0],
                "best_nest": 4 - best[0],
                "best_joint_percent": round(float(best[2]) * 100, 6),
                "one_vip_three_nest_percent": round(float(candidates[1][2]) * 100, 6),
                "two_vip_two_nest_percent": round(float(candidates[2][2]) * 100, 6),
            })

    expected_winners = (
        (2, 2, 2, 1),
        (2, 2, 1, 1),
        (2, 1, 1, 1),
    )
    for index, elgyem in enumerate((2, 3, 4)):
        assert tuple(
            row["best_vip"] for row in rows if row["elgyem"] == elgyem
        ) == expected_winners[index]

    assert winner_counts == {1: 6, 2: 6}
    assert rows[-1]["best_joint_percent"] == 3.181558
    assert rows[0]["best_joint_percent"] == 0.995117
    print(json.dumps(
        {
            "fixed_search_item_slots": 4,
            "decks_scanned": len(rows),
            "winner_counts_by_vip_copy_count": dict(sorted(winner_counts.items())),
            "rows": rows,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
