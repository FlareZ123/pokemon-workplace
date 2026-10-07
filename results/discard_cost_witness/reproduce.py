"""Reproduce exact discard-cost selection aliasing and execution."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import (
    DiscardCandidate,
    apply_discard_selection,
    enumerate_discard_selections,
)
from multicopy_zone_state import ZoneCountState


def main() -> None:
    state = ZoneCountState.from_mapping(
        {
            ("secret_box", "hand"): 1,
            ("fire_energy", "hand"): 1,
            ("dce", "hand"): 1,
            ("boss", "hand"): 1,
            ("stadium", "hand"): 1,
        }
    )
    candidates = (
        DiscardCandidate("fire_energy"),
        DiscardCandidate("dce"),
        DiscardCandidate("boss"),
        DiscardCandidate("stadium"),
    )

    selections = enumerate_discard_selections(
        state,
        candidates,
        3,
    )
    assert len(selections) == 4
    assert all(selection.cost == 3 for selection in selections)

    outcomes = set()
    for selection in selections:
        transition = apply_discard_selection(
            state,
            candidates,
            selection,
        )
        remaining = tuple(
            card_class
            for card_class in ("fire_energy", "dce", "boss", "stadium")
            if transition.after.count(card_class, "hand") == 1
        )
        assert len(remaining) == 1
        outcomes.add(remaining[0])

        for card_class in (
            "secret_box",
            "fire_energy",
            "dce",
            "boss",
            "stadium",
        ):
            assert transition.before.total(card_class) == transition.after.total(card_class)

    assert outcomes == {
        "fire_energy",
        "dce",
        "boss",
        "stadium",
    }

    protected_candidates = (
        DiscardCandidate("fire_energy"),
        DiscardCandidate("dce"),
        DiscardCandidate("boss", max_copies=0),
        DiscardCandidate("stadium"),
    )
    protected = enumerate_discard_selections(
        state,
        protected_candidates,
        3,
    )
    assert len(protected) == 1
    protected_after = apply_discard_selection(
        state,
        protected_candidates,
        protected[0],
    ).after
    assert protected_after.count("boss", "hand") == 1

    stale_state = state.move("stadium", "hand", "discard")
    stale_selection = next(
        selection
        for selection in selections
        if selection.counts == (1, 1, 1, 0)
    )
    stale_rejected = False
    try:
        apply_discard_selection(
            stale_state,
            candidates,
            stale_selection,
        )
    except ValueError:
        stale_rejected = True
    assert stale_rejected

    print(
        json.dumps(
            {
                "scalar_discard_cost": 3,
                "coarse_discardable_capacity": 4,
                "exact_selections": len(selections),
                "distinct_remaining_hand_cards": sorted(outcomes),
                "protected_boss_selections": len(protected),
                "protected_boss_remains_in_hand": True,
                "stale_selection_rejected": stale_rejected,
                "card_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
