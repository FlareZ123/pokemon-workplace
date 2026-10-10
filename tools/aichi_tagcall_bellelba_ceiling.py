"""Exact information-only ceiling for a Bellelba single-target Tag Call fallback.

With Jirachi naturally in the opener and G&H plus Tag Call visible by
the natural first draw, count cases where all other G&H are Prized and
a singleton TAG TEAM Bellelba stays searchable. This measures a K1
observation opportunity, not a successful turn or game.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class TagCallFallback:
    accepted_probability: Fraction
    by_known_gnh: tuple[tuple[int, Fraction], ...]
    accepted_opening_probability: Fraction


def exact_tagcall_bellelba_fallback(
    *, deck_size: int = 60, opening: int = 7,
    subsequent_random_draws: int = 1, prizes: int = 6,
    total_basics: int = 14, gnh: int = 4,
    tagcall: int = 4, bellelba: int = 1,
) -> TagCallFallback:
    """Accepted-opening probability of a Bellelba-only first search.

    Jirachi is a unique eligible starter fixed within the opener.
    All other types are pooled except G&H, Tag Call and Bellelba.
    All G&H not visibly known must be Prized; the single Bellelba
    must remain outside the known hand and outside Prizes.
    """
    if not (deck_size > 0 and 0 < opening < deck_size
            and 1 <= total_basics <= deck_size
            and subsequent_random_draws >= 0 and prizes >= 0
            and gnh >= 1 and tagcall >= 1 and bellelba == 1):
        raise ValueError("invalid setup")
    other = deck_size - 1 - gnh - tagcall - bellelba
    sample = opening - 1 + subsequent_random_draws
    unseen = deck_size - 1 - sample
    if other < total_basics-1 or unseen < prizes:
        raise ValueError("cards do not fit")
    accepted = Fraction(
        choose(deck_size, opening) -
        choose(deck_size-total_basics, opening),
        choose(deck_size, opening),
    )
    if not accepted:
        raise ValueError("no acceptable Basic opening")

    groups = []
    for held_gnh in range(1, min(gnh, sample) + 1):
        wins = Fraction(0)
        for held_tag in range(1, min(tagcall, sample-held_gnh) + 1):
            ways = (choose(gnh, held_gnh) * choose(tagcall, held_tag)
                    * choose(other, sample-held_gnh-held_tag))
            remaining_gnh = gnh-held_gnh
            good_prizes = choose(
                unseen-remaining_gnh-bellelba, prizes-remaining_gnh
            )
            wins += (Fraction(opening, deck_size)
                     * Fraction(ways, choose(deck_size-1, sample))
                     * Fraction(good_prizes, choose(unseen, prizes)))
        groups.append((held_gnh, wins/accepted))
    return TagCallFallback(
        accepted_probability=sum((p for _, p in groups), Fraction(0)),
        by_known_gnh=tuple(groups),
        accepted_opening_probability=accepted,
    )
