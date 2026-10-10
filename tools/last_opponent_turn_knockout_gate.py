"""Track previous-opponent-turn Knock Outs across consecutive extra turns.

This is a minimal event-time projection. A Knock Out during the owner's turn
is recorded under that specific completed turn, including which player's
Pokémon were Knocked Out. Pokémon Checkup KOs are excluded: Checkup is
between turns and does not satisfy "during your opponent's last turn".
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class CompletedTurnKnockouts:
    owner: str
    victim_players: frozenset[str]
    turn_number: int

    def __post_init__(self) -> None:
        if not self.owner or self.turn_number < 1:
            raise ValueError("completed turn requires an owner and positive index")


@dataclass(frozen=True)
class LastOpponentTurnKO:
    """Exactly one latest *completed* turn per distinct owner."""
    turns: tuple[CompletedTurnKnockouts, ...] = ()
    next_turn_number: int = 1

    def complete_turn(
        self, owner: str, victim_players: frozenset[str] = frozenset()
    ) -> "LastOpponentTurnKO":
        if owner in victim_players:
            # Self-KOs can happen, and are valid here; victim sets can include
            # any player. We intentionally do not require KO attribution.
            pass
        other = tuple(turn for turn in self.turns if turn.owner != owner)
        entry = CompletedTurnKnockouts(owner, victim_players, self.next_turn_number)
        return replace(
            self, turns=tuple(sorted(other + (entry,), key=lambda x: x.owner)),
            next_turn_number=self.next_turn_number + 1
        )

    def raihan_eligible(self, player: str, opponent: str) -> bool:
        if player == opponent:
            raise ValueError("player and opponent must differ")
        latest = next((turn for turn in self.turns if turn.owner == opponent), None)
        return latest is not None and player in latest.victim_players

    def last_opponent_turn_index(self, opponent: str) -> int | None:
        latest = next((turn for turn in self.turns if turn.owner == opponent), None)
        return latest.turn_number if latest is not None else None
