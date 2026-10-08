from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Literal

from tools.deck_validator import DeckEntry, ValidationReport, validate_deck_construction
from tools.legality_provenance import CardLegalityProvenance, LegalityProvenanceIndex

PrintEligibility = Literal["eligible", "ineligible", "unresolved"]
DeckDisposition = Literal["eligible_snapshot", "invalid", "unresolved"]


@dataclass(frozen=True)
class PrintLegalityProof:
    card_id: str
    name: str | None
    quantity: int
    eligibility: PrintEligibility
    reason: str
    provenance: CardLegalityProvenance | None


@dataclass(frozen=True)
class DeckLegalityProof:
    as_of: date
    snapshot_reference_date: date
    disposition: DeckDisposition
    construction: ValidationReport
    print_proofs: tuple[PrintLegalityProof, ...]
    semantic_source: str = "bundled_en_snapshot"
    regional_legality_scope: str = "not_evaluated"


def _classify_print(
    provenance: CardLegalityProvenance,
    *,
    snapshot_reference_date: date,
) -> tuple[PrintEligibility, str]:
    disposition = provenance.disposition

    if disposition == "direct_legal_release_verified":
        return "eligible", "Direct Expanded status and audited release timing both support this print."

    if disposition == "direct_legal_snapshot_timing_unverified":
        if provenance.as_of >= snapshot_reference_date:
            return (
                "eligible",
                "The current bundled Expanded snapshot supports this direct print; historical release timing is not reconstructed.",
            )
        return (
            "unresolved",
            "The current snapshot supports this direct print, but the requested historical date predates the snapshot reference and release timing is unaudited.",
        )

    if disposition == "direct_banned":
        if provenance.direct_status_source == "official_overlay" or provenance.as_of >= snapshot_reference_date:
            return "ineligible", "The print is banned or tournament-excluded for the evaluated current-state boundary."
        return (
            "unresolved",
            "The snapshot records this print as banned, but the repository lacks an effective date for applying that current-state fact to this historical query.",
        )

    if disposition == "direct_not_yet_released":
        return "ineligible", "The print's set had not been released by the requested date."

    if disposition == "direct_release_waiting":
        return "ineligible", "The print was still inside an audited tournament release waiting period."

    if disposition == "high_confidence_reprint_candidate":
        return (
            "unresolved",
            "Strong repository reprint evidence exists, but it is preserved as candidate evidence rather than an automatic tournament ruling.",
        )

    if disposition == "semantic_review":
        return "unresolved", "The older print still requires semantic reprint review."

    if disposition == "known_non_equivalent":
        return "ineligible", "The outside-scope print has explicit evidence of non-equivalence to its Expanded counterpart."

    if disposition == "no_expanded_counterpart":
        return "ineligible", "No legal Expanded counterpart is known for this outside-scope print."

    if disposition == "outside_disallowed":
        if provenance.as_of >= snapshot_reference_date:
            return "ineligible", "The outside-scope print is explicitly disallowed by current card or legality data."
        return (
            "unresolved",
            "The outside-scope print is currently disallowed, but the repository does not carry enough date evidence to backdate that conclusion.",
        )

    raise ValueError(f"Unhandled legality disposition: {disposition}")


def adjudicate_deck(
    entries: Iterable[DeckEntry],
    resources_root: Path,
    *,
    as_of: date,
    deck_size: int = 60,
) -> DeckLegalityProof:
    entries = tuple(entries)
    construction = validate_deck_construction(
        entries,
        resources_root,
        deck_size=deck_size,
    )
    index = LegalityProvenanceIndex.from_resources(resources_root)
    snapshot_reference_date = max(
        index.set_release_dates[set_id]
        for set_id in index.resolver.expanded_sets
    )

    quantities: Counter[str] = Counter()
    card_ids: set[str] = set()
    for entry in entries:
        card_ids.add(entry.card_id)
        if (
            not isinstance(entry.quantity, bool)
            and isinstance(entry.quantity, int)
            and entry.quantity > 0
        ):
            quantities[entry.card_id] += entry.quantity

    proofs: list[PrintLegalityProof] = []
    for card_id in sorted(card_ids):
        card = index.resolver.cards_by_id.get(card_id)
        if card is None:
            proofs.append(
                PrintLegalityProof(
                    card_id=card_id,
                    name=None,
                    quantity=quantities[card_id],
                    eligibility="ineligible",
                    reason="The exact print is absent from the bundled card snapshot.",
                    provenance=None,
                )
            )
            continue

        provenance = index.resolve(card_id, as_of=as_of)
        eligibility, reason = _classify_print(
            provenance,
            snapshot_reference_date=snapshot_reference_date,
        )
        proofs.append(
            PrintLegalityProof(
                card_id=card_id,
                name=card["name"],
                quantity=quantities[card_id],
                eligibility=eligibility,
                reason=reason,
                provenance=provenance,
            )
        )

    has_construction_error = any(
        issue.severity == "error" for issue in construction.issues
    )
    if has_construction_error or any(p.eligibility == "ineligible" for p in proofs):
        disposition: DeckDisposition = "invalid"
    elif any(p.eligibility == "unresolved" for p in proofs):
        disposition = "unresolved"
    else:
        disposition = "eligible_snapshot"

    return DeckLegalityProof(
        as_of=as_of,
        snapshot_reference_date=snapshot_reference_date,
        disposition=disposition,
        construction=construction,
        print_proofs=tuple(proofs),
    )
