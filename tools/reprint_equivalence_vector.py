from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from tools.pokedex_information_semantics import summarize_distinct_prefix

AxisStatus = Literal["equivalent", "divergent", "unmodeled"]
StateModelStatus = Literal["equivalent", "divergent", "unresolved"]
TournamentStatus = Literal[
    "certified_equivalent",
    "certified_non_equivalent",
    "unresolved",
]


@dataclass(frozen=True)
class EquivalenceAxes:
    material_transition: AxisStatus
    private_observation: AxisStatus
    public_observation: AxisStatus
    target_domain: AxisStatus
    timing: AxisStatus
    event_semantics: AxisStatus
    rule_category: AxisStatus

    def state_model_status(self) -> StateModelStatus:
        values = (
            self.material_transition,
            self.private_observation,
            self.public_observation,
            self.target_domain,
            self.timing,
            self.event_semantics,
            self.rule_category,
        )
        if "divergent" in values:
            return "divergent"
        if "unmodeled" in values:
            return "unresolved"
        return "equivalent"


@dataclass(frozen=True)
class ReprintEquivalenceProfile:
    source_id: str
    target_id: str
    name: str
    axes: EquivalenceAxes
    tournament_status: TournamentStatus
    expected_resolver_kind: str
    evidence: tuple[str, ...]


def _pokedex_axes() -> EquivalenceAxes:
    summaries = [summarize_distinct_prefix(size) for size in range(1, 6)]
    if not all(row["physical_outcomes_equal"] is True for row in summaries):
        raise ValueError("Pokédex physical outcome proof failed")
    if not any(
        row["legacy_outcomes_with_lower_information_witness"] > 0
        for row in summaries
        if row["available_cards"] > 1
    ):
        raise ValueError("Pokédex private-observation witness was not recovered")

    return EquivalenceAxes(
        material_transition="equivalent",
        private_observation="divergent",
        public_observation="equivalent",
        target_domain="equivalent",
        timing="equivalent",
        event_semantics="equivalent",
        rule_category="equivalent",
    )


def benchmark_profiles() -> tuple[ReprintEquivalenceProfile, ...]:
    return (
        ReprintEquivalenceProfile(
            source_id="ex7-83",
            target_id="sm7-127",
            name="Copycat",
            axes=EquivalenceAxes(
                material_transition="equivalent",
                private_observation="equivalent",
                public_observation="equivalent",
                target_domain="equivalent",
                timing="equivalent",
                event_semantics="equivalent",
                rule_category="equivalent",
            ),
            tournament_status="certified_equivalent",
            expected_resolver_kind="official_semantic_candidate",
            evidence=(
                "Current Tournament Handbook functional-reprint exemplar",
                "Current-semantic fingerprint equality",
            ),
        ),
        ReprintEquivalenceProfile(
            source_id="base5-17",
            target_id="sm7-151",
            name="Rainbow Energy",
            axes=EquivalenceAxes(
                material_transition="unmodeled",
                private_observation="equivalent",
                public_observation="equivalent",
                target_domain="equivalent",
                timing="equivalent",
                event_semantics="divergent",
                rule_category="equivalent",
            ),
            tournament_status="certified_non_equivalent",
            expected_resolver_kind="known_non_equivalent",
            evidence=(
                "Current Tournament Handbook functional-reprint counterexample",
                "Damage and damage-counter placement are distinct mechanics",
            ),
        ),
        ReprintEquivalenceProfile(
            source_id="ex5-90",
            target_id="sm7-136",
            name="Life Herb",
            axes=EquivalenceAxes(
                material_transition="unmodeled",
                private_observation="equivalent",
                public_observation="equivalent",
                target_domain="divergent",
                timing="equivalent",
                event_semantics="equivalent",
                rule_category="equivalent",
            ),
            tournament_status="unresolved",
            expected_resolver_kind="known_non_equivalent",
            evidence=(
                "Historical print excludes Pokémon-ex targets",
                "Current Expanded contains a reachable Pokémon-ex witness",
            ),
        ),
        ReprintEquivalenceProfile(
            source_id="base1-87",
            target_id="bw1-98",
            name="Pokédex",
            axes=_pokedex_axes(),
            tournament_status="unresolved",
            expected_resolver_kind="semantic_review",
            evidence=(
                "Physical top-deck outcome sets are equal for one through five available cards",
                "Legacy text permits lower-information private-observation witnesses",
            ),
        ),
    )


def summarize_benchmark_profiles() -> dict[str, object]:
    profiles = benchmark_profiles()
    return {
        "counts": {
            "profiles": len(profiles),
            "state_model_equivalent": sum(
                row.axes.state_model_status() == "equivalent" for row in profiles
            ),
            "state_model_divergent": sum(
                row.axes.state_model_status() == "divergent" for row in profiles
            ),
            "state_model_unresolved": sum(
                row.axes.state_model_status() == "unresolved" for row in profiles
            ),
            "tournament_certified_equivalent": sum(
                row.tournament_status == "certified_equivalent" for row in profiles
            ),
            "tournament_certified_non_equivalent": sum(
                row.tournament_status == "certified_non_equivalent" for row in profiles
            ),
            "tournament_unresolved": sum(
                row.tournament_status == "unresolved" for row in profiles
            ),
        },
        "profiles": [
            {
                "source_id": row.source_id,
                "target_id": row.target_id,
                "name": row.name,
                "state_model_status": row.axes.state_model_status(),
                "tournament_status": row.tournament_status,
                "expected_resolver_kind": row.expected_resolver_kind,
                "axes": {
                    "material_transition": row.axes.material_transition,
                    "private_observation": row.axes.private_observation,
                    "public_observation": row.axes.public_observation,
                    "target_domain": row.axes.target_domain,
                    "timing": row.axes.timing,
                    "event_semantics": row.axes.event_semantics,
                    "rule_category": row.axes.rule_category,
                },
                "evidence": list(row.evidence),
            }
            for row in profiles
        ],
    }
