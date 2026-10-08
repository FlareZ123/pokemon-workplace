"""Opponent-aware six-Prize target eligibility for Boss versus Serena gust.

Boss's Orders may select any opposing Benched Pokemon. Serena's gust mode may
select a Benched Pokemon V. For this abstract model a target has a one-hit
Prize reward (1/2/3) and a Pokemon-V-family eligibility flag. One-Prize V
targets are excluded from the enumerated source-state taxonomy, while two- and
three-Prize targets may be V or non-V.

Each gust token represents an otherwise executable Supporter action; spending
one attacks the target on the current turn. Only one is consumed per turn.
Serena's alternate discard-and-draw mode is not modeled here.
"""
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations_with_replacement
from typing import Iterator


@dataclass(frozen=True, order=True)
class Target:
    prizes: int
    is_pokemon_v: bool = False


@lru_cache(None)
def minimum_attacks(
    active: Target,
    bench: tuple[Target, ...],
    bosses: int,
    serenas: int,
    prizes_needed: int = 6,
) -> int:
    if prizes_needed <= 0:
        return 0
    if not bench:
        return 1

    actions = [(active, bench, bosses, serenas)]
    for i, target in enumerate(bench):
        replacement_bench = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
        if bosses:
            actions.append((target, replacement_bench, bosses - 1, serenas))
        if serenas and target.is_pokemon_v:
            actions.append((target, replacement_bench, bosses, serenas - 1))

    scores = []
    for prize_target, survivors, b, s in actions:
        if prize_target.prizes >= prizes_needed or not survivors:
            scores.append(1)
        else:
            scores.append(
                1 + max(
                    minimum_attacks(
                        promoted, survivors[:j] + survivors[j + 1:],
                        b, s, prizes_needed - prize_target.prizes
                    )
                    for j, promoted in enumerate(survivors)
                )
            )
    return min(scores)


def forced_first_gust(
    active: Target,
    bench: tuple[Target, ...],
    bosses: int,
    serenas: int,
    source: str,
    target: Target,
    prizes_needed: int = 6,
) -> int | None:
    """Exact cost of targeting the supplied Benched type first using source."""
    if source not in ("boss", "serena"):
        raise ValueError("source must be boss or serena")
    if source == "boss" and not bosses:
        return None
    if source == "serena" and (not serenas or not target.is_pokemon_v):
        return None
    scores = []
    for i, eligible in enumerate(bench):
        if eligible != target:
            continue
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
        b = bosses - (source == "boss")
        s = serenas - (source == "serena")
        if eligible.prizes >= prizes_needed or not survivors:
            scores.append(1)
        else:
            scores.append(
                1 + max(
                    minimum_attacks(
                        promoted, survivors[:j] + survivors[j + 1:],
                        b, s, prizes_needed - eligible.prizes
                    )
                    for j, promoted in enumerate(survivors)
                )
            )
    return min(scores) if scores else None


def enumerate_boards() -> Iterator[tuple[Target, tuple[Target, ...]]]:
    """Two-to-five-Pokemon opposing boards with 1/2/3 prize and V eligibility."""
    kinds = (
        Target(1, False),
        Target(2, False),
        Target(2, True),
        Target(3, False),
        Target(3, True),
    )
    for count in range(2, 6):
        for values in combinations_with_replacement(kinds, count):
            if sum(target.prizes for target in values) < 6:
                continue
            for active in sorted(set(values)):
                bench = list(values)
                bench.remove(active)
                yield active, tuple(sorted(bench))
