"""Reproduce legal turn-ending source inventory by semantic action channel."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from turn_end_source_catalog import audit_turn_end_sources, channel_counts


def main() -> None:
    rows = audit_turn_end_sources(ROOT / "resources")
    counts = channel_counts(rows)
    expected = {
        "ability_use": 46,
        "item_effect": 7,
        "legacy_evolution": 92,
        "opponent_turn_attachment_reaction": 2,
        "stadium_activation": 5,
        "supporter_effect": 12,
    }
    assert counts == expected, (counts, expected)
    assert len(rows) == sum(expected.values()) == 164
    witness = {(row.print_id, row.channel) for row in rows}
    for key in (
        ("me55c-106m", "legacy_evolution"),
        ("xy2-13", "legacy_evolution"),
        ("me3-77", "stadium_activation"),
        ("sm11-205", "stadium_activation"),
        ("sm7-145", "supporter_effect"),
        ("swsh9-133", "supporter_effect"),
        ("sv5-143", "item_effect"),
        ("swsh7-142", "item_effect"),
        ("sv1-125", "ability_use"),
        ("sm11-167", "opponent_turn_attachment_reaction"),
        ("sv6pt5-17", "opponent_turn_attachment_reaction"),
    ):
        assert key in witness, key
    assert ("me1-3", "legacy_evolution") not in witness
    assert len({r.name for r in rows if r.channel == "legacy_evolution"}) == 41
    print("turn_end_source_catalog regression: PASS")
    for kind, count in counts.items():
        print(kind, count)
    print("Total legal source print rows:", len(rows))


if __name__ == "__main__":
    main()
