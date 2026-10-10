"""Named same-turn Regidrago VSTAR recharge routes after copied Trifrost.

Trifrost discards all Energy attached to the Regidrago actor, so the listed
scenarios begin from exactly zero attached Energy. We model a single action
line for each named Crispin/Raihan plus manual Double Dragon attachment,
optionally using an unspent Legacy Star to return Double Dragon from discard.
This is conditional route existence, not a complete deck search simulator.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RechargeState:
    double_dragon_hand: int = 0
    double_dragon_deck: int = 0
    double_dragon_discard: int = 0
    grass_deck: int = 0
    fire_deck: int = 0
    grass_discard: int = 0
    fire_discard: int = 0
    any_card_remaining_in_deck: bool = True
    crispin_access: bool = True
    raihan_access: bool = True
    knockout_last_opponent_turn: bool = False
    supporter_unused: bool = True
    manual_attachment_unused: bool = True
    legacy_star_unused: bool = True
    legacy_star_ability_live: bool = True

    def __post_init__(self) -> None:
        counts = (
            self.double_dragon_hand, self.double_dragon_deck,
            self.double_dragon_discard, self.grass_deck,
            self.fire_deck, self.grass_discard, self.fire_discard,
        )
        if min(counts) < 0:
            raise ValueError("Energy zone counts cannot be negative")


@dataclass(frozen=True)
class RechargeRoute:
    label: str
    actions: tuple[str, ...]
    basic_type: str
    double_dragon_source: str


def pays_apex_dragon(*, basic_type: str, double_dragon_cards: int = 1) -> bool:
    """With a Basic Grass/Fire and DDE, check [G,G,F] using flexible units."""
    if basic_type not in {"Grass", "Fire"}:
        raise ValueError("model accepts only Basic Grass or Fire")
    grass = int(basic_type == "Grass")
    fire = int(basic_type == "Fire")
    unmet = max(0, 2 - grass) + max(0, 1 - fire)
    return 2 * double_dragon_cards >= unmet


def find_recharge_routes(s: RechargeState) -> tuple[RechargeRoute, ...]:
    if not (s.supporter_unused and s.manual_attachment_unused):
        return ()
    out = []
    # Crispin: choose both different-type Basic Energy from deck. One goes
    # to hand and the other is attached to the Regidrago VSTAR. Importantly
    # the unneeded hand Basic is *not* a second attachment that turn.
    if s.crispin_access and s.grass_deck and s.fire_deck:
        basic = "Grass"
        if s.double_dragon_hand:
            out.append(RechargeRoute(
                "Crispin + held Double Dragon Energy",
                (
                    "Crispin: search different-type Basics, attach Grass to Regidrago",
                    "Manually attach held Double Dragon Energy to Regidrago",
                ),
                basic, "hand"
            ))
        if (s.double_dragon_discard and s.legacy_star_unused
                and s.legacy_star_ability_live):
            out.append(RechargeRoute(
                "Crispin + Legacy Star + discarded Double Dragon Energy",
                (
                    "Crispin: search different-type Basics, attach Grass to Regidrago",
                    "Legacy Star: discard top seven, recover Double Dragon from discard",
                    "Manually attach recovered Double Dragon Energy to Regidrago",
                ),
                basic, "discard"
            ))

    # Raihan: must have suffered a KO on opponent's immediately previous turn
    # and attach a Basic Energy from discard to unlock its universal deck
    # search. That search can locate the manual-attachment Double Dragon.
    basic = "Grass" if s.grass_discard else ("Fire" if s.fire_discard else None)
    if (s.raihan_access and s.knockout_last_opponent_turn
            and basic is not None):
        if s.double_dragon_deck:
            out.append(RechargeRoute(
                "Raihan + searched Double Dragon Energy",
                (
                    f"Raihan: attach discarded {basic}, then search deck for Double Dragon Energy",
                    "Manually attach the searched Double Dragon Energy to Regidrago",
                ),
                basic, "deck"
            ))
        if (s.double_dragon_discard and s.legacy_star_unused
                and s.legacy_star_ability_live
                and s.any_card_remaining_in_deck):
            out.append(RechargeRoute(
                "Raihan + Legacy Star + discarded Double Dragon Energy",
                (
                    f"Raihan: attach discarded {basic}, then search a card from deck",
                    "Legacy Star: discard top seven, recover Double Dragon from discard",
                    "Manually attach recovered Double Dragon Energy to Regidrago",
                ),
                basic, "discard"
            ))

    assert all(pays_apex_dragon(basic_type=r.basic_type) for r in out)
    return tuple(out)
