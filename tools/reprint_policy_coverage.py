from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from tools.deck_legality_proof import (
    ReprintEvidencePolicy,
    classify_print_eligibility,
)
from tools.legality_provenance import LegalityProvenanceIndex


@dataclass(frozen=True)
class PolicyCoverage:
    policy: ReprintEvidencePolicy
    eligible: int
    ineligible: int
    unresolved: int

    @property
    def total(self) -> int:
        return self.eligible + self.ineligible + self.unresolved


def summarize_reprint_policy_coverage(
    resources_root: Path,
    *,
    as_of: date,
) -> dict[str, object]:
    index = LegalityProvenanceIndex.from_resources(resources_root)
    snapshot_reference_date = max(
        index.set_release_dates[set_id]
        for set_id in index.resolver.expanded_sets
    )

    pool_ids = tuple(
        sorted(
            card_id
            for card_id, card in index.resolver.cards_by_id.items()
            if card["_set_id"] not in index.resolver.expanded_sets
            and card["name"] in index.resolver.legal_expanded_by_name
        )
    )

    coverage: dict[str, dict[str, int]] = {}
    kinds_by_policy: dict[str, dict[str, dict[str, int]]] = {}

    for policy in ("conservative", "current_semantic_evidence"):
        disposition_counts: Counter[str] = Counter()
        kind_counts: dict[str, Counter[str]] = {
            "eligible": Counter(),
            "ineligible": Counter(),
            "unresolved": Counter(),
        }
        for card_id in pool_ids:
            provenance = index.resolve(card_id, as_of=as_of)
            eligibility, _reason = classify_print_eligibility(
                provenance,
                snapshot_reference_date=snapshot_reference_date,
                reprint_evidence_policy=policy,
            )
            disposition_counts[eligibility] += 1
            kind_counts[eligibility][provenance.reprint_kind] += 1

        coverage[policy] = {
            "eligible": disposition_counts["eligible"],
            "ineligible": disposition_counts["ineligible"],
            "unresolved": disposition_counts["unresolved"],
            "total": len(pool_ids),
        }
        kinds_by_policy[policy] = {
            eligibility: dict(sorted(counts.items()))
            for eligibility, counts in kind_counts.items()
        }

    return {
        "as_of": as_of.isoformat(),
        "snapshot_reference_date": snapshot_reference_date.isoformat(),
        "same_name_outside_scope_prints": len(pool_ids),
        "coverage": coverage,
        "kinds_by_policy": kinds_by_policy,
    }
