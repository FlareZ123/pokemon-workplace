"""Physically valid rare-Prize counterexamples to sampled global portfolios.

Each fixture specifies a 7-card opening, 6 Prizes, and the first-turn draw
as real named cards in the Aichi 60. Build a complete 60-position permutation,
then verify identical raw-state construction for both ACE SPEC choices.

The endpoint is the existing compressed Aichi first-turn core, not a
full-game matchup outcome.
"""

from collections import defaultdict, deque
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from aichi_vileplume_secret_box import (
    BASE_DECK,
    SECRET_BOX_DECK,
    BOX_ALL_OUTPUTS,
    _raw_state,
    _state_succeeds,
)


FIXTURES = {
    "requires_supporter": {
        "opening": (
            "Oddish", "Grand Tree", "Guzma", "Cassius",
            "Karen", "Faba", "Lusamine",
        ),
        "prizes": (
            "Tag Call", "Tag Call", "Tag Call", "Tag Call",
            "Pidgeotto", "Gloom",
        ),
        "draw": "Plumeria",
        "required": 4,
    },
    "requires_tool_and_stadium": {
        "opening": (
            "Oddish", "Grand Tree", "Jet Energy", "Guzma",
            "Cassius", "Karen", "Faba",
        ),
        "prizes": (
            "Guzma & Hala", "Guzma & Hala", "Guzma & Hala",
            "Guzma & Hala", "Pidgeotto", "Gloom",
        ),
        "draw": "Lusamine",
        "required": 10,
    },
    "requires_item": {
        "opening": (
            "Oddish", "Grand Tree", "Bunnelby",
            "Technical Machine: Evolution", "Technical Machine: Evolution",
            "Guzma", "Cassius",
        ),
        "prizes": (
            "Stealthy Hood", "Stealthy Hood", "Stealthy Hood",
            "Counter Gain", "Artazon", "Artazon",
        ),
        "draw": "Karen",
        "required": 1,
    },
}


def physical_order(fixture: dict[str, object]) -> list[int]:
    """Construct one complete legal permutation from named physical cards."""
    occurrences: dict[str, deque[int]] = defaultdict(deque)
    for index, name in enumerate(BASE_DECK):
        occurrences[name].append(index)

    def take(name: str) -> int:
        if not occurrences[name]:
            raise ValueError(f"Card not available in the published deck: {name}")
        return occurrences[name].popleft()

    opening = fixture["opening"]
    prizes = fixture["prizes"]
    draw = fixture["draw"]
    assert isinstance(opening, tuple) and len(opening) == 7
    assert isinstance(prizes, tuple) and len(prizes) == 6
    assert isinstance(draw, str)
    prefix = [take(name) for name in (*opening, *prizes, draw)]
    remainder = [
        index for pool in occurrences.values() for index in pool
    ]
    order = prefix + remainder
    assert len(order) == len(set(order)) == 60
    assert tuple(BASE_DECK[i] for i in order[:7]) == opening
    assert tuple(BASE_DECK[i] for i in order[7:13]) == prizes
    return order


def main() -> None:
    aggregate_required = 0
    for label, fixture in FIXTURES.items():
        order = physical_order(fixture)
        base = _raw_state(BASE_DECK, order)
        secret = _raw_state(SECRET_BOX_DECK, order)
        assert base is not None and secret is not None
        assert not _state_succeeds(base), label

        works = tuple(
            _state_succeeds_with_mask(secret, mask)
            for mask in range(16)
        )
        assert works[BOX_ALL_OUTPUTS], label
        assert not works[0], label
        required = fixture["required"]
        assert isinstance(required, int)
        assert all(
            not works[mask] for mask in range(16)
            if mask & required != required
        ), (label, works)
        aggregate_required |= required
        winning_masks = [
            mask for mask, success in enumerate(works) if success
        ]
        print(label)
        print("  physical opening =", fixture["opening"])
        print("  prize identities =", fixture["prizes"])
        print("  first turn draw =", fixture["draw"])
        print("  winning output masks =", winning_masks)
        print("  universally necessary bits for this witness =", required)

    assert aggregate_required == BOX_ALL_OUTPUTS
    print("Across the three valid starting states, every output category")
    print("is necessary for a universally complete category portfolio.")
    print("Full all-four category requirement witness suite passed.")


if __name__ == "__main__":
    main()
