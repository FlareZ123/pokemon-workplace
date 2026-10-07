"""Closed-form partial Prize-information value for two singleton alternatives."""

from __future__ import annotations


def two_singleton_value_after_k_inspections(
    unknown_cards: int,
    prize_count: int,
    inspected_prize_cards: int,
) -> float:
    """Expected availability after inspecting k distinct Prize identities.

    Assumptions:
    * two equally valuable singleton-dependent lines A and B;
    * each line works exactly when its singleton is not in the Prize set;
    * before committing, the player learns the identities of k distinct
      physical Prize cards chosen without replacement;
    * if one singleton is observed in the Prizes, the player chooses the other
      line; if neither is observed, either line is symmetric.

    The result simplifies to:
      (U - P) * (U + k - 1) / (U * (U - 1))
    where U is unknown_cards and P is prize_count.
    """
    if unknown_cards < 2:
        raise ValueError("unknown_cards must be at least 2")
    if not 0 <= prize_count <= unknown_cards:
        raise ValueError("prize_count must be between 0 and unknown_cards")
    if not 0 <= inspected_prize_cards <= prize_count:
        raise ValueError("inspected_prize_cards must be between 0 and prize_count")

    u = unknown_cards
    p = prize_count
    k = inspected_prize_cards
    return (u - p) * (u + k - 1) / (u * (u - 1))


def marginal_value_per_additional_inspected_prize(
    unknown_cards: int,
    prize_count: int,
) -> float:
    """Constant per-card increment for the symmetric two-singleton case."""
    if unknown_cards < 2:
        raise ValueError("unknown_cards must be at least 2")
    if not 0 <= prize_count <= unknown_cards:
        raise ValueError("prize_count must be between 0 and unknown_cards")
    return (unknown_cards - prize_count) / (unknown_cards * (unknown_cards - 1))
