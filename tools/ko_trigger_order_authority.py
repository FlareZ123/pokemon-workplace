"""Represent source-scoped claims about triggered-effect ordering."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class OrderingAuthority(str, Enum):
    CURRENT_PLAYER = "current_player"
    NEXT_PLAYER = "next_player"
    KNOCKED_OUT_POKEMON_OWNER = "knocked_out_pokemon_owner"


class TimingWindow(str, Enum):
    DURING_TURN = "during_turn"
    POKEMON_CHECKUP = "pokemon_checkup"


class TriggerKind(str, Enum):
    POKEMON_KNOCKED_OUT = "pokemon_knocked_out"
    ENERGY_ATTACHED = "energy_attached"
    OTHER = "other"


@dataclass(frozen=True)
class OrderingContext:
    timing_window: TimingWindow
    trigger_kind: TriggerKind
    simultaneous_knockout_count: int = 1
    interaction_id: str | None = None

    def __post_init__(self) -> None:
        if self.simultaneous_knockout_count < 0:
            raise ValueError("simultaneous_knockout_count must be non-negative")


@dataclass(frozen=True)
class AuthorityClaim:
    source_id: str
    authority: OrderingAuthority
    scope_note: str


@dataclass(frozen=True)
class AuthorityAssessment:
    claims: tuple[AuthorityClaim, ...]

    @property
    def authorities(self) -> frozenset[OrderingAuthority]:
        return frozenset(claim.authority for claim in self.claims)

    @property
    def resolved_authority(self) -> OrderingAuthority | None:
        if len(self.authorities) != 1:
            return None
        return next(iter(self.authorities))

    @property
    def has_conflict(self) -> bool:
        return len(self.authorities) > 1


TPCI_FEB_2026 = "tpci_professor_feb_2026"
ASIA_LOST_CITY_REUNICLUS_QA = "pokemon_asia_lost_city_reuniclus_qa"\nJAPAN_LOST_CITY_REUNICLUS_QA = "pokemon_japan_lost_city_reuniclus_qa"
ADVANCED_RULEBOOK_3_4 = "advanced_rulebook_3_4"
LOST_CITY_REUNICLUS = "lost_city_reuniclus"


def _claims_for_source(
    context: OrderingContext,
    source_id: str,
) -> tuple[AuthorityClaim, ...]:
    if source_id == TPCI_FEB_2026:
        if (
            context.timing_window == TimingWindow.DURING_TURN
            and context.trigger_kind
            in {
                TriggerKind.POKEMON_KNOCKED_OUT,
                TriggerKind.ENERGY_ATTACHED,
            }
        ):
            return (
                AuthorityClaim(
                    source_id,
                    OrderingAuthority.CURRENT_PLAYER,
                    "Current player chooses during-turn trigger order.",
                ),
            )
        if context.timing_window == TimingWindow.POKEMON_CHECKUP:
            return (
                AuthorityClaim(
                    source_id,
                    OrderingAuthority.NEXT_PLAYER,
                    "Next player chooses effect order during Pokemon Checkup.",
                ),
            )
        return ()

    if source_id in {ASIA_LOST_CITY_REUNICLUS_QA, JAPAN_LOST_CITY_REUNICLUS_QA}:
        if context.interaction_id == LOST_CITY_REUNICLUS:
            return (
                AuthorityClaim(
                    source_id,
                    OrderingAuthority.KNOCKED_OUT_POKEMON_OWNER,
                    "Reuniclus owner chooses Persistent Cells versus Lost City.",
                ),
            )
        return ()

    if source_id == ADVANCED_RULEBOOK_3_4:
        if (
            context.trigger_kind == TriggerKind.POKEMON_KNOCKED_OUT
            and context.simultaneous_knockout_count >= 2
        ):
            return (
                AuthorityClaim(
                    source_id,
                    OrderingAuthority.CURRENT_PLAYER,
                    "Current player orders effects from simultaneous Knock Outs.",
                ),
            )
        return ()

    raise ValueError(f"unknown source_id: {source_id!r}")


def assess_ordering_authority(
    context: OrderingContext,
    source_ids: Iterable[str],
) -> AuthorityAssessment:
    selected = tuple(source_ids)
    if len(selected) != len(set(selected)):
        raise ValueError("source_ids must be unique")

    return AuthorityAssessment(
        tuple(
            claim
            for source_id in selected
            for claim in _claims_for_source(context, source_id)
        )
    )
