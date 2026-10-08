"""Finite-source Item/Supporter gust minimax with target-effect immunity.

Each target is a public typed object. Source immunity is fixed across the
position; card access, tool removal, locks, and hit point/damage dynamics are
deliberately excluded. The opponent chooses each replacement Active.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations_with_replacement
from typing import Iterator


@dataclass(frozen=True)
class TargetType:
    prizes: int
    item_gust: bool
    supporter_gust: bool
    concrete_anchor: str


TARGET_TYPES: dict[str, TargetType] = {
    "B1": TargetType(1, False, False, "Axew Unnerve, sm11-154"),
    "B2": TargetType(2, False, False, "Cetitan ex Snow Camouflage, sv10-65"),
    "I3": TargetType(3, False, True, "Greninja V-UNION Ninja Body, swshp-SWSH155"),
    "S2": TargetType(2, True, False, "Arceus VSTAR + Leafy Camo Poncho"),
    "S3": TargetType(3, True, False, "Crobat VMAX + Leafy Camo Poncho"),
    "U1": TargetType(1, True, True, "ordinary one-Prize Basic"),
    "U2": TargetType(2, True, True, "ordinary Pokemon ex"),
    "U3": TargetType(3, True, True, "ordinary TAG TEAM Pokemon-GX"),
}


def boards() -> Iterator[tuple[str, tuple[str, ...]]]:
    """Distinct Active/type-multiset boards (2..6 targets, total >=6 Prizes)."""
    kinds = tuple(sorted(TARGET_TYPES))
    for size in range(2, 7):
        for values in combinations_with_replacement(kinds, size):
            if sum(TARGET_TYPES[value].prizes for value in values) < 6:
                continue
            for active in sorted(set(values)):
                bench = list(values)
                bench.remove(active)
                yield active, tuple(bench)


def actions(
    active: str, bench: tuple[str, ...], items: int, supporters: int,
) -> tuple[tuple[str, tuple[str, ...], int, int], ...]:
    """Attack current Active or spend one typed gust and attack a legal Bench."""
    out = [(active, bench, items, supporters)]
    for index, target in enumerate(bench):
        rest = tuple(sorted((active,) + bench[:index] + bench[index + 1 :]))
        profile = TARGET_TYPES[target]
        if items > 0 and profile.item_gust:
            out.append((target, rest, items - 1, supporters))
        if supporters > 0 and profile.supporter_gust:
            out.append((target, rest, items, supporters - 1))
    return tuple(out)


@lru_cache(maxsize=None)
def minimum_attack_turns(
    active: str,
    bench: tuple[str, ...],
    items: int,
    supporters: int,
    prizes_needed: int = 6,
) -> int:
    """Exact minimax: attacker chooses gust, defender chooses promotion."""
    if prizes_needed <= 0:
        return 0
    if not bench:
        return 1

    best = len(bench) + 1
    for knocked_out, survivors, item_left, supporter_left in actions(
        active, bench, items, supporters,
    ):
        reward = TARGET_TYPES[knocked_out].prizes
        if reward >= prizes_needed or not survivors:
            return 1
        worst_replacement = max(
            minimum_attack_turns(
                promoted,
                survivors[:index] + survivors[index + 1 :],
                item_left,
                supporter_left,
                prizes_needed - reward,
            )
            for index, promoted in enumerate(survivors)
        )
        best = min(best, 1 + worst_replacement)
    return best
