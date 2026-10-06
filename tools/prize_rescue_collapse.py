"""Exact setup-Prize probabilities for singleton rescue packages.

The model partitions a deck into:

* critical singleton cards that must be recovered if Prized;
* copies of a rescue card such as Gladion; and
* all remaining cards.

It measures a deliberately narrow failure mode: before taking ordinary Prize
cards or otherwise recovering a used rescue card, are there enough rescue
copies outside the initial Prize cards to retrieve every Prized critical card?
"""

from __future__ import annotations

from math import comb


def _validate(deck_size: int, prize_count: int, critical_singletons: int, rescue_copies: int) -> None:
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if not 0 <= critical_singletons <= deck_size:
        raise ValueError("critical_singletons must be between 0 and deck_size")
    if not 0 <= rescue_copies <= deck_size - critical_singletons:
        raise ValueError("rescue_copies must fit outside critical_singletons")


def joint_probability(
    deck_size: int,
    prize_count: int,
    critical_singletons: int,
    rescue_copies: int,
    critical_prized: int,
    rescuers_prized: int,
) -> float:
    """Return P(C=critical_prized, J=rescuers_prized) exactly."""
    _validate(deck_size, prize_count, critical_singletons, rescue_copies)
    filler = deck_size - critical_singletons - rescue_copies
    filler_prized = prize_count - critical_prized - rescuers_prized

    if not 0 <= critical_prized <= critical_singletons:
        return 0.0
    if not 0 <= rescuers_prized <= rescue_copies:
        return 0.0
    if not 0 <= filler_prized <= filler:
        return 0.0

    return (
        comb(critical_singletons, critical_prized)
        * comb(rescue_copies, rescuers_prized)
        * comb(filler, filler_prized)
        / comb(deck_size, prize_count)
    )


def any_critical_prized_probability(
    deck_size: int,
    prize_count: int,
    critical_singletons: int,
) -> float:
    """Return P(at least one modeled critical singleton is Prized)."""
    _validate(deck_size, prize_count, critical_singletons, 0)
    if critical_singletons == 0 or prize_count == 0:
        return 0.0
    return 1.0 - comb(deck_size - critical_singletons, prize_count) / comb(deck_size, prize_count)


def collapse_probability(
    deck_size: int,
    prize_count: int,
    critical_singletons: int,
    rescue_copies: int,
) -> float:
    """Return exact pre-Prize rescue-collapse probability.

    If C critical singletons and J rescue copies are Prized initially, then
    rescue_copies - J rescuers are outside the Prize cards. Each can retrieve
    one critical card before it is itself placed among the Prize cards.
    Collapse therefore occurs when C > rescue_copies - J.
    """
    _validate(deck_size, prize_count, critical_singletons, rescue_copies)

    probability = 0.0
    for critical_prized in range(min(critical_singletons, prize_count) + 1):
        max_rescuers_prized = min(rescue_copies, prize_count - critical_prized)
        for rescuers_prized in range(max_rescuers_prized + 1):
            if critical_prized <= rescue_copies - rescuers_prized:
                continue
            probability += joint_probability(
                deck_size,
                prize_count,
                critical_singletons,
                rescue_copies,
                critical_prized,
                rescuers_prized,
            )
    return probability


def conditional_collapse_probability(
    deck_size: int,
    prize_count: int,
    critical_singletons: int,
    rescue_copies: int,
) -> float:
    """Return P(collapse | at least one critical singleton is Prized)."""
    any_critical = any_critical_prized_probability(deck_size, prize_count, critical_singletons)
    if any_critical == 0.0:
        return 0.0
    return collapse_probability(
        deck_size,
        prize_count,
        critical_singletons,
        rescue_copies,
    ) / any_critical


def collapse_breakdown(
    deck_size: int,
    prize_count: int,
    critical_singletons: int,
    rescue_copies: int,
) -> list[tuple[int, int, float]]:
    """Return collapse-state masses as (critical_prized, rescuers_prized, p)."""
    _validate(deck_size, prize_count, critical_singletons, rescue_copies)
    rows: list[tuple[int, int, float]] = []
    for critical_prized in range(min(critical_singletons, prize_count) + 1):
        max_rescuers_prized = min(rescue_copies, prize_count - critical_prized)
        for rescuers_prized in range(max_rescuers_prized + 1):
            if critical_prized > rescue_copies - rescuers_prized:
                p = joint_probability(
                    deck_size,
                    prize_count,
                    critical_singletons,
                    rescue_copies,
                    critical_prized,
                    rescuers_prized,
                )
                if p:
                    rows.append((critical_prized, rescuers_prized, p))
    return rows
