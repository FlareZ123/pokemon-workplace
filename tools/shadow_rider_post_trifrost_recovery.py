"""Deterministic one-turn Mimikyu recovery/promotion after Regidrago Trifrost.

The scope is a bounded physical/action-budget witness search for the CL2026
Aichi Shadow Rider list, not a complete game simulator. Unknown draws from
Underworld Door are ignored. Every used card is assumed individually available.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class RecoveryScenario:
    mimikyu_zone: str = "discard"
    psychic_in_hand: int = 0
    psychic_in_discard: int = 2
    psychic_attached: int = 0
    dimension_valley: bool = False
    bench_space: bool = True
    opponent_has_bench: bool = True
    active_damaged: bool = True
    active_tool_free: bool = True
    float_effect_enabled: bool = True
    ordinary_retreat_allowed: bool = True
    item_play_enabled: bool = True
    underworld_door_enabled: bool = True
    tulip_available: bool = True
    night_stretcher_available: bool = True
    float_stone_available: bool = True
    guzma_available: bool = True
    acerola_available: bool = True
    supporter_spent: bool = False
    manual_attachment_spent: bool = False
    gx_spent: bool = False
    apex_exposed: bool = True
    dialga_in_discard: bool = True

    def __post_init__(self) -> None:
        if self.mimikyu_zone not in {"discard", "hand", "bench", "active"}:
            raise ValueError("unsupported Mimikyu zone")
        if min(self.psychic_in_hand, self.psychic_in_discard, self.psychic_attached) < 0:
            raise ValueError("Energy counts must be nonnegative")


@dataclass(frozen=True)
class RecoveryState:
    zone: str
    hand_energy: int
    discard_energy: int
    attached_energy: int
    supporter_used: bool
    manual_used: bool
    door_used: bool = False
    incumbent_active: bool = True
    float_attached: bool = False
    retreat_used: bool = False
    stretcher_used: bool = False
    tulip_used: bool = False
    guzma_used: bool = False
    acerola_used: bool = False


@dataclass(frozen=True)
class RecoveryWitness:
    actions: tuple[str, ...]
    finish: RecoveryState


def _transitions(s: RecoveryState, c: RecoveryScenario):
    """Yield action and state. Only positive, available transitions are emitted."""
    if (c.night_stretcher_available and c.item_play_enabled
            and not s.stretcher_used):
        if s.zone == "discard":
            yield "Night Stretcher: Mimikyu to hand", replace(
                s, zone="hand", stretcher_used=True
            )
        if s.discard_energy:
            yield "Night Stretcher: one Psychic Energy to hand", replace(
                s, discard_energy=s.discard_energy - 1,
                hand_energy=s.hand_energy + 1, stretcher_used=True
            )

    if c.tulip_available and not s.supporter_used and not s.tulip_used:
        recover_m = s.zone == "discard"
        if recover_m or s.discard_energy:
            count = min(s.discard_energy, 4 - int(recover_m))
            yield "Tulip: recover Mimikyu and " + str(count) + " Psychic Energy", replace(
                s, zone="hand" if recover_m else s.zone,
                hand_energy=s.hand_energy + count,
                discard_energy=s.discard_energy - count,
                supporter_used=True, tulip_used=True
            )

    if s.zone == "hand" and c.bench_space and s.incumbent_active:
        yield "Bench recovered Mimikyu", replace(s, zone="bench")

    if s.zone == "bench" and s.hand_energy:
        if not s.manual_used:
            yield "Manual Psychic attachment to Mimikyu", replace(
                s, hand_energy=s.hand_energy - 1,
                attached_energy=s.attached_energy + 1, manual_used=True
            )
        if (c.underworld_door_enabled and s.incumbent_active
                and not s.door_used):
            yield "Underworld Door: Psychic to Benched Mimikyu", replace(
                s, hand_energy=s.hand_energy - 1,
                attached_energy=s.attached_energy + 1, door_used=True
            )

    if (c.float_stone_available and s.incumbent_active
            and c.active_tool_free and not s.float_attached):
        # XY-era Float Stone is a Pokémon Tool even when its older text
        # mentions Item; Tools are distinct from Items for Item locks.
        yield "Attach Float Stone to incumbent", replace(s, float_attached=True)

    if s.zone == "bench" and s.incumbent_active:
        if (s.float_attached and c.float_effect_enabled
                and c.ordinary_retreat_allowed and not s.retreat_used):
            yield "Free retreat using Float Stone; promote Mimikyu", replace(
                s, zone="active", incumbent_active=False, retreat_used=True
            )
        if (c.guzma_available and c.opponent_has_bench
                and not s.supporter_used and not s.guzma_used):
            yield "Guzma: opponent switch then promote Mimikyu", replace(
                s, zone="active", incumbent_active=False,
                supporter_used=True, guzma_used=True
            )
        if (c.acerola_available and c.active_damaged and not s.supporter_used
                and not s.acerola_used):
            yield "Acerola: pick up damaged incumbent; promote Mimikyu", replace(
                s, zone="active", incumbent_active=False,
                supporter_used=True, acerola_used=True
            )


def find_recovery(c: RecoveryScenario) -> RecoveryWitness | None:
    """Shortest bounded deterministic witness to next-turn ready Copycat."""
    if c.gx_spent or not c.apex_exposed or not c.dialga_in_discard:
        return None
    required_energy = 1 if c.dimension_valley else 2
    start = RecoveryState(
        zone=c.mimikyu_zone,
        hand_energy=c.psychic_in_hand,
        discard_energy=c.psychic_in_discard,
        attached_energy=c.psychic_attached,
        supporter_used=c.supporter_spent,
        manual_used=c.manual_attachment_spent,
        incumbent_active=(c.mimikyu_zone != "active")
    )
    todo = deque([(start, ())])
    seen = {start}
    while todo:
        state, actions = todo.popleft()
        if state.zone == "active" and state.attached_energy >= required_energy:
            return RecoveryWitness(actions, state)
        for action, child in _transitions(state, c):
            if child not in seen:
                seen.add(child)
                todo.append((child, actions + (action,)))
    return None
