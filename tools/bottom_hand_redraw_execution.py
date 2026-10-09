"""Physical-zone kernel for six literal bottom-hand redraw families.

Call after source legality, timing gates, and optional activation are resolved.
Deck tuples are ordered top first. Caller supplies randomized bottom orders.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerZones:
    deck: tuple[str, ...]
    hand: tuple[str, ...]
    prizes_remaining: int


@dataclass(frozen=True)
class RedrawResult:
    player: PlayerZones
    opponent: PlayerZones
    moved: tuple[int, int]
    drawn: tuple[int, int]


def _return(player: PlayerZones, order: tuple[str, ...]) -> PlayerZones:
    if Counter(order) != Counter(player.hand):
        raise ValueError("bottom order must be a permutation of old hand")
    if len(set(player.deck + player.hand)) != len(player.deck + player.hand):
        raise ValueError("physical identifiers must be distinct")
    return PlayerZones(player.deck + order, (), player.prizes_remaining)


def _draw(player: PlayerZones, n: int) -> tuple[PlayerZones, int]:
    taken = min(n, len(player.deck))
    return (PlayerZones(player.deck[taken:], player.hand + player.deck[:taken],
                        player.prizes_remaining), taken)


def execute_bottom_hand_redraw(
    effect: str, player: PlayerZones, opponent: PlayerZones,
    *, player_bottom: tuple[str, ...] = (),
    opponent_bottom: tuple[str, ...] = (),
    chosen: str = "player",
    lucian_heads: tuple[bool, bool] | None = None,
) -> RedrawResult:
    """Resolve Iono/Marnie/Lucian/Thievul/Kingdra/Skwovet, acting player first."""
    if effect not in ("Iono", "Marnie", "Lucian", "Thievul", "Kingdra", "Skwovet"):
        raise ValueError("unsupported effect")
    if not all(type(s.prizes_remaining) is int and s.prizes_remaining >= 0
               for s in (player, opponent)):
        raise ValueError("invalid Prize counts")
    if effect == "Kingdra" and chosen not in ("player", "opponent"):
        raise ValueError("invalid Kingdra target")
    both = effect in ("Iono", "Marnie", "Lucian", "Thievul")
    affect_p = both or effect == "Skwovet" or chosen == "player"
    affect_q = both or (effect == "Kingdra" and chosen == "opponent")
    if (not affect_p and player_bottom) or (not affect_q and opponent_bottom):
        raise ValueError("non-targeted player's hand cannot be moved")
    if effect == "Lucian":
        if lucian_heads is None or len(lucian_heads) != 2 or any(type(v) is not bool for v in lucian_heads):
            raise ValueError("Lucian needs independently resolved coin flips")
    elif lucian_heads is not None:
        raise ValueError("coin flips only used by Lucian")
    p = _return(player, player_bottom) if affect_p else player
    q = _return(opponent, opponent_bottom) if affect_q else opponent
    moved = (len(player.hand) if affect_p else 0,
             len(opponent.hand) if affect_q else 0)
    if both and (moved[0] or moved[1]):
        if effect == "Iono":
            requested = (player.prizes_remaining, opponent.prizes_remaining)
        elif effect == "Marnie":
            requested = (5, 4)
        elif effect == "Thievul":
            requested = (4, 4)
        else:
            assert lucian_heads is not None
            requested = tuple(6 if heads else 3 for heads in lucian_heads)
    elif effect == "Kingdra":
        requested = (4 if moved[0] else 0, 4 if moved[1] else 0)
    elif effect == "Skwovet":
        requested = (1 if moved[0] else 0, 0)
    else:
        requested = (0, 0)
    p, np = _draw(p, requested[0])
    q, nq = _draw(q, requested[1])
    return RedrawResult(p, q, moved, (np, nq))
