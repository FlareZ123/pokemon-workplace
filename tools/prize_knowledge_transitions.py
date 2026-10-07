"""Small information-state calculations for Prize-zone mutations."""

from __future__ import annotations

from math import comb, log2


def unknown_position_swap_support(face_down_prize_count: int) -> int:
    """Possible resulting physical Prize sets after swapping a known incoming card.

    Assumptions:
    * the player knows the exact identities comprising the current face-down
      Prize set;
    * the identity-to-position mapping is unknown;
    * one chosen face-down Prize position is swapped with a known incoming
      card;
    * all current Prize identities are treated as physically distinct.

    The outgoing identity can be any one of the face-down Prize cards.
    """
    if face_down_prize_count <= 0:
        raise ValueError("face_down_prize_count must be positive")
    return face_down_prize_count


def uniform_support_entropy_bits(support_size: int) -> float:
    """Shannon entropy in bits for a uniform finite support."""
    if support_size <= 0:
        raise ValueError("support_size must be positive")
    return log2(support_size)


def redealt_prize_support(pool_size: int, prize_count: int) -> int:
    """Number of possible physical Prize sets after a fully randomized redeal."""
    if pool_size <= 0:
        raise ValueError("pool_size must be positive")
    if not 0 <= prize_count <= pool_size:
        raise ValueError("prize_count must be between 0 and pool_size")
    return comb(pool_size, prize_count)


def exact_knowledge_preserved(
    *,
    outgoing_identity_known: bool,
    incoming_identity_known: bool,
    resulting_set_reinspected: bool = False,
) -> bool:
    """Whether an exact Prize-set composition stays exact after one replacement.

    This intentionally describes composition knowledge, not physical position
    knowledge. Re-inspecting the complete resulting set restores exactness.
    """
    return resulting_set_reinspected or (
        outgoing_identity_known and incoming_identity_known
    )
