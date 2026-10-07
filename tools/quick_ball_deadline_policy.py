"""Finite-horizon Quick Ball allocation with separate target deadlines."""

from __future__ import annotations

from functools import lru_cache


def deadline_success_probability(
    deck_cards: int,
    gladion_copies: int,
    *,
    attacker_deadline: int,
    gladion_deadline: int,
) -> float:
    """Return optimal probability both objectives meet their draw deadlines.

    Deadlines count future natural draws allowed before each objective must be
    complete. The current hand contains one Quick Ball and one acceptable
    discard. The deck contains one required attacker, one Tapu Lele-GX-like
    support Basic, gladion_copies rescue Supporters, and filler cards.
    """
    filler = deck_cards - gladion_copies - 2
    if gladion_copies < 1 or filler < 0:
        raise ValueError("invalid deck state")
    if min(attacker_deadline, gladion_deadline) < 0:
        raise ValueError("deadlines must be non-negative")
    horizon = max(attacker_deadline, gladion_deadline)

    @lru_cache(maxsize=None)
    def value(
        attacker: int,
        support: int,
        gladion: int,
        other: int,
        quick_ball: int,
        attacker_done: bool,
        gladion_done: bool,
        draws_elapsed: int,
    ) -> float:
        actions = [(
            attacker,
            support,
            gladion,
            other,
            quick_ball,
            attacker_done,
            gladion_done,
        )]
        if quick_ball:
            if not attacker_done and attacker:
                actions.append((
                    0, support, gladion, other,
                    0, True, gladion_done,
                ))
            if not gladion_done and support and gladion:
                actions.append((
                    attacker, 0, gladion - 1, other,
                    0, attacker_done, True,
                ))

        best = 0.0
        for state in actions:
            a, support, g, other, q, a_done, g_done = state
            if (
                (not a_done and draws_elapsed >= attacker_deadline)
                or (not g_done and draws_elapsed >= gladion_deadline)
            ):
                continue
            if a_done and g_done:
                best = 1.0
                continue
            if draws_elapsed >= horizon:
                continue

            remaining = a + support + g + other
            probability = 0.0

            if a:
                probability += (
                    a / remaining
                    * value(
                        0, support, g, other, q,
                        True, g_done, draws_elapsed + 1,
                    )
                )
            if support:
                if not g_done and g:
                    probability += (
                        support / remaining
                        * value(
                            a, 0, g - 1, other, q,
                            a_done, True, draws_elapsed + 1,
                        )
                    )
                else:
                    probability += (
                        support / remaining
                        * value(
                            a, 0, g, other, q,
                            a_done, g_done, draws_elapsed + 1,
                        )
                    )
            if g:
                probability += (
                    g / remaining
                    * value(
                        a, support, g - 1, other, q,
                        a_done, True, draws_elapsed + 1,
                    )
                )
            if other:
                probability += (
                    other / remaining
                    * value(
                        a, support, g, other - 1, q,
                        a_done, g_done, draws_elapsed + 1,
                    )
                )

            best = max(best, probability)

        return best

    return value(
        1,
        1,
        gladion_copies,
        filler,
        1,
        False,
        False,
        0,
    )
