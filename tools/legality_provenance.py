from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from tools.build_expanded_legality_baseline import (
    OFFICIAL_BAN_OVERLAY,
    classify_effective_legality,
    has_tournament_ban_rule,
    load_json,
)
from tools.release_legality import release_status
from tools.reprint_errata_resolution import ReprintResolver, build_reprint_resolver

DirectStatus = Literal["Legal", "Banned"]
TimingStatus = Literal[
    "before_set_release",
    "audited_waiting_period",
    "audited_release_eligible",
    "post_release_not_audited",
]
Disposition = Literal[
    "direct_banned",
    "direct_not_yet_released",
    "direct_release_waiting",
    "direct_legal_release_verified",
    "direct_legal_snapshot_timing_unverified",
    "high_confidence_reprint_candidate",
    "known_non_equivalent",
    "semantic_review",
    "no_expanded_counterpart",
    "outside_disallowed",
    "outside_not_yet_released",
]

HIGH_CONFIDENCE_REPRINT_KINDS = frozenset(
    {
        "official_semantic_candidate",
        "exact_fingerprint_candidate",
        "historical_official_reprint_candidate",
        "official_errata_candidate",
    }
)


@dataclass(frozen=True)
class TargetEvidence:
    card_id: str
    set_id: str
    timing_status: TimingStatus
    ordinary_legal_date: date | None


@dataclass(frozen=True)
class CardLegalityProvenance:
    card_id: str
    name: str
    set_id: str
    as_of: date
    disposition: Disposition
    direct_status: DirectStatus | None
    direct_status_source: str | None
    timing_status: TimingStatus | None
    ordinary_legal_date: date | None
    reprint_kind: str
    target_evidence: tuple[TargetEvidence, ...]
    semantic_source: str = "bundled_en_snapshot"
    regional_legality_scope: str = "not_evaluated"


def parse_set_date(value: str) -> date:
    return date.fromisoformat(value.replace("/", "-"))


def classify_direct_as_of(card: dict, *, as_of: date) -> tuple[DirectStatus, str]:
    """Apply dated official overlays without backdating them before their effective date."""

    overlay = OFFICIAL_BAN_OVERLAY.get(card["id"])
    if overlay is None or as_of >= date.fromisoformat(overlay["effective_date"]):
        status, source = classify_effective_legality(card)
        return status, source

    database_status = (card.get("legalities") or {}).get("expanded")
    if database_status == "Banned":
        return "Banned", "database"
    if has_tournament_ban_rule(card):
        return "Banned", "card_text_tournament_ban"
    if database_status == "Legal":
        return "Legal", "database_pre_overlay"
    return "Legal", "set_fallback_pre_overlay"


def timing_for_set(
    set_id: str,
    *,
    set_release_date: date,
    as_of: date,
) -> tuple[TimingStatus, date | None]:
    if as_of < set_release_date:
        return "before_set_release", None

    audited_status, ordinary_legal_date = release_status(set_id, as_of=as_of)
    if audited_status == "waiting_period":
        return "audited_waiting_period", ordinary_legal_date
    if audited_status == "ordinary_release_eligible":
        return "audited_release_eligible", ordinary_legal_date
    return "post_release_not_audited", None


class LegalityProvenanceIndex:
    def __init__(
        self,
        resolver: ReprintResolver,
        set_release_dates: dict[str, date],
    ) -> None:
        self.resolver = resolver
        self.set_release_dates = set_release_dates

    @classmethod
    def from_resources(cls, resources_root: Path) -> "LegalityProvenanceIndex":
        sets = load_json(resources_root / "sets" / "en.json")
        return cls(
            build_reprint_resolver(resources_root),
            {row["id"]: parse_set_date(row["releaseDate"]) for row in sets},
        )

    def target_evidence(
        self,
        card_ids: tuple[str, ...],
        *,
        as_of: date,
    ) -> tuple[TargetEvidence, ...]:
        rows = []
        for card_id in card_ids:
            target = self.resolver.cards_by_id[card_id]
            set_id = target["_set_id"]
            timing_status, ordinary_legal_date = timing_for_set(
                set_id,
                set_release_date=self.set_release_dates[set_id],
                as_of=as_of,
            )
            rows.append(
                TargetEvidence(
                    card_id=card_id,
                    set_id=set_id,
                    timing_status=timing_status,
                    ordinary_legal_date=ordinary_legal_date,
                )
            )
        return tuple(rows)

    def resolve(self, card_id: str, *, as_of: date) -> CardLegalityProvenance:
        card = self.resolver.cards_by_id[card_id]
        set_id = card["_set_id"]
        resolution = self.resolver.resolve(card_id)

        if set_id in self.resolver.expanded_sets:
            status, source = classify_direct_as_of(card, as_of=as_of)
            timing_status, ordinary_legal_date = timing_for_set(
                set_id,
                set_release_date=self.set_release_dates[set_id],
                as_of=as_of,
            )

            if timing_status == "before_set_release":
                disposition: Disposition = "direct_not_yet_released"
            elif status == "Banned":
                disposition = "direct_banned"
            elif timing_status == "audited_waiting_period":
                disposition = "direct_release_waiting"
            elif timing_status == "audited_release_eligible":
                disposition = "direct_legal_release_verified"
            else:
                disposition = "direct_legal_snapshot_timing_unverified"

            return CardLegalityProvenance(
                card_id=card_id,
                name=card["name"],
                set_id=set_id,
                as_of=as_of,
                disposition=disposition,
                direct_status=status,
                direct_status_source=source,
                timing_status=timing_status,
                ordinary_legal_date=ordinary_legal_date,
                reprint_kind=resolution.kind,
                target_evidence=(),
            )

        source_unreleased = as_of < self.set_release_dates[set_id]
        if source_unreleased:
            disposition = "outside_not_yet_released"
        elif resolution.kind in HIGH_CONFIDENCE_REPRINT_KINDS:
            disposition = "high_confidence_reprint_candidate"
        elif resolution.kind == "known_non_equivalent":
            disposition = "known_non_equivalent"
        elif resolution.kind == "semantic_review":
            disposition = "semantic_review"
        elif resolution.kind == "no_expanded_counterpart":
            disposition = "no_expanded_counterpart"
        elif resolution.kind == "outside_disallowed":
            disposition = "outside_disallowed"
        else:
            raise ValueError(f"Unhandled outside-scope reprint resolution: {resolution.kind}")

        return CardLegalityProvenance(
            card_id=card_id,
            name=card["name"],
            set_id=set_id,
            as_of=as_of,
            disposition=disposition,
            direct_status=None,
            direct_status_source=None,
            timing_status="before_set_release" if source_unreleased else None,
            ordinary_legal_date=None,
            reprint_kind=resolution.kind,
            target_evidence=self.target_evidence(
                resolution.target_print_ids,
                as_of=as_of,
            ),
        )
