"""Aichi 2026 Shadow Rider counter-ALS against Regidrago VSTAR.

This module models the response-turn constraints around the already-established
Copycat -> Apex Dragon -> Timeless-GX copy chain. It focuses on three pieces
that a static copy graph does not capture:

* Mimikyu must be materialized for the attack while Dialga-GX must be in discard;
* the same discard-search Item can sometimes route both singleton payloads;
* Mimikyu's [P,C] Copycat cost collapses to [P] under Dimension Valley.

The model is intentionally bounded to the named routing cards in Yasunori
Kato's CL Aichi Open League winning Shadow Rider Calyrex list.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
from enum import Enum
from math import comb


class PayloadZone(str, Enum):
    DECK = "deck"
    HAND = "hand"
    DISCARD = "discard"
    PRIZE = "prize"


@dataclass(frozen=True)
class RoutingResources:
    mysterious_treasure: int = 4
    fog_crystal: int = 4
    quick_ball: int = 1
    battle_compressor: int = 1
    hisuian_heavy_ball: int = 1
    night_stretcher: int = 1
    tulip: int = 1
    item_play: bool = True
    supporter_quota: int = 1
    supporter_used: int = 0
    disposable_hand_cards: int = 1

    def __post_init__(self) -> None:
        counts = (
            self.mysterious_treasure,
            self.fog_crystal,
            self.quick_ball,
            self.battle_compressor,
            self.hisuian_heavy_ball,
            self.night_stretcher,
            self.tulip,
            self.supporter_quota,
            self.supporter_used,
            self.disposable_hand_cards,
        )
        if any(value < 0 for value in counts):
            raise ValueError("routing resource counts must be non-negative")
        if self.supporter_used > self.supporter_quota:
            raise ValueError("supporter_used cannot exceed supporter_quota")


@dataclass(frozen=True)
class PayloadState:
    mimikyu: PayloadZone
    dialga: PayloadZone
    resources: RoutingResources = RoutingResources()


@dataclass(frozen=True)
class PayloadRoute:
    before: PayloadState
    after: PayloadState
    actions: tuple[str, ...]


@dataclass(frozen=True)
class PrizeCollisionProbability:
    neither_prized: float
    exactly_one_prized: float
    both_prized: float


@dataclass(frozen=True)
class EnergyReadiness:
    required_units: int
    preexisting_units: int
    new_attachments: int
    ready: bool


def _replace_resources(
    resources: RoutingResources,
    **changes: object,
) -> RoutingResources:
    return replace(resources, **changes)


def _routing_transitions(
    state: PayloadState,
) -> tuple[tuple[str, PayloadState], ...]:
    """Enumerate one legal named routing action from the coarse payload state."""

    m = state.mimikyu
    d = state.dialga
    r = state.resources
    out: list[tuple[str, PayloadState]] = []

    def add(
        label: str,
        next_m: PayloadZone,
        next_d: PayloadZone,
        next_r: RoutingResources,
    ) -> None:
        out.append((label, PayloadState(next_m, next_d, next_r)))

    # Mysterious Treasure and the Sword & Shield Quick Ball both have a
    # one-card discard gate. Dialga in hand can itself pay that gate. Their
    # searches are constrained searches, so zero retrieval remains legal after
    # the discard has changed game state.
    if r.item_play and r.mysterious_treasure > 0:
        next_r = _replace_resources(
            r,
            mysterious_treasure=r.mysterious_treasure - 1,
        )
        if d == PayloadZone.HAND:
            add(
                "Mysterious Treasure: discard Dialga-GX",
                m,
                PayloadZone.DISCARD,
                next_r,
            )
            if m == PayloadZone.DECK:
                add(
                    "Mysterious Treasure: discard Dialga-GX, search Mimikyu",
                    PayloadZone.HAND,
                    PayloadZone.DISCARD,
                    next_r,
                )
        if r.disposable_hand_cards > 0:
            paid_r = _replace_resources(
                next_r,
                disposable_hand_cards=r.disposable_hand_cards - 1,
            )
            add(
                "Mysterious Treasure: discard other card",
                m,
                d,
                paid_r,
            )
            if m == PayloadZone.DECK:
                add(
                    "Mysterious Treasure: discard other card, search Mimikyu",
                    PayloadZone.HAND,
                    d,
                    paid_r,
                )

    if r.item_play and r.quick_ball > 0:
        next_r = _replace_resources(r, quick_ball=r.quick_ball - 1)
        if d == PayloadZone.HAND:
            add(
                "Quick Ball: discard Dialga-GX",
                m,
                PayloadZone.DISCARD,
                next_r,
            )
            if m == PayloadZone.DECK:
                add(
                    "Quick Ball: discard Dialga-GX, search Mimikyu",
                    PayloadZone.HAND,
                    PayloadZone.DISCARD,
                    next_r,
                )
        if r.disposable_hand_cards > 0:
            paid_r = _replace_resources(
                next_r,
                disposable_hand_cards=r.disposable_hand_cards - 1,
            )
            add("Quick Ball: discard other card", m, d, paid_r)
            if m == PayloadZone.DECK:
                add(
                    "Quick Ball: discard other card, search Mimikyu",
                    PayloadZone.HAND,
                    d,
                    paid_r,
                )

    if (
        r.item_play
        and r.fog_crystal > 0
        and m == PayloadZone.DECK
    ):
        add(
            "Fog Crystal: search Mimikyu",
            PayloadZone.HAND,
            d,
            _replace_resources(r, fog_crystal=r.fog_crystal - 1),
        )

    if (
        r.item_play
        and r.battle_compressor > 0
        and (m == PayloadZone.DECK or d == PayloadZone.DECK)
    ):
        next_r = _replace_resources(
            r,
            battle_compressor=r.battle_compressor - 1,
        )
        if m == PayloadZone.DECK:
            add(
                "Battle Compressor: discard Mimikyu",
                PayloadZone.DISCARD,
                d,
                next_r,
            )
        if d == PayloadZone.DECK:
            add(
                "Battle Compressor: discard Dialga-GX",
                m,
                PayloadZone.DISCARD,
                next_r,
            )
        if (
            m == PayloadZone.DECK
            and d == PayloadZone.DECK
        ):
            add(
                "Battle Compressor: discard Mimikyu and Dialga-GX",
                PayloadZone.DISCARD,
                PayloadZone.DISCARD,
                next_r,
            )

    if (
        r.item_play
        and r.night_stretcher > 0
        and m == PayloadZone.DISCARD
    ):
        add(
            "Night Stretcher: recover Mimikyu",
            PayloadZone.HAND,
            d,
            _replace_resources(
                r,
                night_stretcher=r.night_stretcher - 1,
            ),
        )

    if r.item_play and r.hisuian_heavy_ball > 0:
        next_r = _replace_resources(
            r,
            hisuian_heavy_ball=r.hisuian_heavy_ball - 1,
        )
        if m == PayloadZone.PRIZE:
            add(
                "Hisuian Heavy Ball: recover Mimikyu",
                PayloadZone.HAND,
                d,
                next_r,
            )
        if d == PayloadZone.PRIZE:
            add(
                "Hisuian Heavy Ball: recover Dialga-GX",
                m,
                PayloadZone.HAND,
                next_r,
            )

    if (
        r.tulip > 0
        and r.supporter_used < r.supporter_quota
        and m == PayloadZone.DISCARD
    ):
        add(
            "Tulip: recover Mimikyu",
            PayloadZone.HAND,
            d,
            _replace_resources(
                r,
                tulip=r.tulip - 1,
                supporter_used=r.supporter_used + 1,
            ),
        )

    return tuple(out)


def payload_ready(state: PayloadState) -> bool:
    """Mimikyu can be played from hand while Dialga is an Apex Dragon payload."""

    return (
        state.mimikyu == PayloadZone.HAND
        and state.dialga == PayloadZone.DISCARD
    )


def find_payload_route(
    mimikyu: PayloadZone,
    dialga: PayloadZone,
    resources: RoutingResources = RoutingResources(),
    *,
    max_actions: int = 8,
) -> PayloadRoute | None:
    """Return a shortest named route to Mimikyu-in-hand + Dialga-in-discard."""

    start = PayloadState(mimikyu, dialga, resources)
    queue: deque[tuple[PayloadState, tuple[str, ...]]] = deque(
        [(start, ())]
    )
    seen = {start}

    while queue:
        state, actions = queue.popleft()
        if payload_ready(state):
            return PayloadRoute(start, state, actions)
        if len(actions) >= max_actions:
            continue
        for label, next_state in _routing_transitions(state):
            if next_state in seen:
                continue
            seen.add(next_state)
            queue.append((next_state, actions + (label,)))
    return None


def prize_collision_probability(
    *,
    deck_size: int = 60,
    prize_count: int = 6,
) -> PrizeCollisionProbability:
    """Exact initial Prize distribution for two distinct singleton payloads."""

    if deck_size < 2:
        raise ValueError("deck_size must be at least 2")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")

    total = comb(deck_size, prize_count)
    neither = comb(deck_size - 2, prize_count) / total
    exactly_one = (
        2 * comb(deck_size - 2, prize_count - 1) / total
        if prize_count >= 1
        else 0.0
    )
    both = (
        comb(deck_size - 2, prize_count - 2) / total
        if prize_count >= 2
        else 0.0
    )
    return PrizeCollisionProbability(
        neither,
        exactly_one,
        both,
    )


def copycat_required_energy_units(
    *,
    dimension_valley_live: bool,
) -> int:
    """Return attachments needed for Psychic/Colorless Copycat from zero Energy."""

    return 1 if dimension_valley_live else 2


def mimikyu_energy_readiness(
    *,
    dimension_valley_live: bool,
    preexisting_psychic_energy: int = 0,
    psychic_energy_in_hand: int,
    underworld_door_uses: int,
    manual_attachment_available: bool,
    mimikyu_is_benched_before_promotion: bool = True,
) -> EnergyReadiness:
    """Evaluate deterministic same-turn Psychic attachments onto Mimikyu.

    Underworld Door contributes only while Mimikyu is Benched. Every modeled
    Energy card is a Basic Psychic Energy from the Aichi list and supplies one
    Psychic unit, which also satisfies the Colorless symbol on Copycat.
    """

    values = (
        preexisting_psychic_energy,
        psychic_energy_in_hand,
        underworld_door_uses,
    )
    if any(value < 0 for value in values):
        raise ValueError("Energy counts must be non-negative")

    required = copycat_required_energy_units(
        dimension_valley_live=dimension_valley_live,
    )
    door_channels = (
        underworld_door_uses
        if mimikyu_is_benched_before_promotion
        else 0
    )
    attachment_channels = (
        door_channels
        + int(manual_attachment_available)
    )
    new_attachments = min(
        psychic_energy_in_hand,
        attachment_channels,
    )
    ready = (
        preexisting_psychic_energy + new_attachments
        >= required
    )
    return EnergyReadiness(
        required_units=required,
        preexisting_units=preexisting_psychic_energy,
        new_attachments=new_attachments,
        ready=ready,
    )


def supporter_line_feasible(
    *,
    recover_mimikyu_with_tulip: bool,
    promote_mimikyu_with_guzma: bool,
    supporter_quota: int = 1,
    supporter_used: int = 0,
) -> bool:
    """Check the ordinary Supporter collision between Tulip and Guzma."""

    if supporter_quota < 0 or supporter_used < 0:
        raise ValueError("Supporter counts must be non-negative")
    required = (
        int(recover_mimikyu_with_tulip)
        + int(promote_mimikyu_with_guzma)
    )
    return supporter_used + required <= supporter_quota
