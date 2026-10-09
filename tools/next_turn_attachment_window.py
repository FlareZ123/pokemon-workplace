"""Attack-created, player-scoped next-turn manual Energy-attachment permissions.

Dragonair sm1-95 / Dragon's Wish says that during your next turn you
may attach any number of Energy cards from your hand to your Pokémon.
This changes the ordinary from-hand action channel itself. By contrast,
an Ability or Trainer that instructs its user to attach Energy performs a
separate effect and need not change the ordinary action quota.

This is a typed overlay on the shared TurnActionBudget. Integer usage
remains authoritative history; the active permission can authorize a play
when ordinary remaining quota is zero. The overlay does not validate
the particular Energy card, target, locks, or physical card movement.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class NextTurnAttachmentWindow:
    """Player-scoped Dragon's Wish permission on a future/current turn.

    pending_for survives intervening opponent turns, including extra turns.
    active_for is cleared on every real turn start and activated for the
    arriving player only if that player had a pending permission.
    """

    pending_for: frozenset[str] = frozenset()
    active_for: frozenset[str] = frozenset()

    def queue_dragon_wish(self, player: str) -> "NextTurnAttachmentWindow":
        """Record the attack's effect; it is not active on the attack turn."""
        if not player:
            raise ValueError("player identifier must be non-empty")
        return replace(self, pending_for=self.pending_for | {player})

    def on_turn_start(self, player: str) -> "NextTurnAttachmentWindow":
        """Apply the permission as a new turn begins for the named player."""
        if not player:
            raise ValueError("player identifier must be non-empty")
        return NextTurnAttachmentWindow(
            pending_for=self.pending_for - {player},
            active_for=frozenset({player}) if player in self.pending_for else frozenset(),
        )

    def remove_attack_effects(self) -> "NextTurnAttachmentWindow":
        """Pokémon Ranger-like removal of attack effects on players."""
        return NextTurnAttachmentWindow()

    def can_manually_attach(self, player: str, budget: TurnActionBudget) -> bool:
        """Generic hand-attachment bandwidth; physical restrictions are separate."""
        return not budget.turn_ended and (
            player in self.active_for
            or budget.can(TurnAction.MANUAL_ENERGY_ATTACHMENT)
        )

    def consume_manual_attachment(
        self, player: str, budget: TurnActionBudget
    ) -> TurnActionBudget | None:
        """Record a hand attachment without imposing an arbitrary finite cap."""
        if not self.can_manually_attach(player, budget):
            return None
        if player in self.active_for:
            return replace(
                budget,
                manual_energy_attachments_used=budget.manual_energy_attachments_used + 1,
            )
        return budget.consume(TurnAction.MANUAL_ENERGY_ATTACHMENT)
