"""Analyze destination conflicts for Energy discarded by successful retreat."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class DestinationCandidate:
    effect_id: str
    destination_zone: str


@dataclass(frozen=True)
class RetreatDestinationAnalysis:
    candidates: tuple[DestinationCandidate, ...]
    prohibited_zones: tuple[str, ...]
    destination_zone: str | None

    @property
    def resolved(self) -> bool:
        return self.destination_zone is not None

    @property
    def requires_authority(self) -> bool:
        return self.destination_zone is None


def analyze_successful_retreat_energy_destination(
    *,
    dashing_pouch_active: bool,
    opposing_scoop_up_block_active: bool,
    holder_has_damage: bool,
    energy_is_prism_star: bool,
) -> RetreatDestinationAnalysis:
    """Return the currently supported destination analysis for one paid Energy.

    The ordinary successful-retreat destination is discard.

    Dashing Pouch proposes hand instead of discard. An opposing Scoop-Up Block
    prohibits attached cards on a damaged Pokémon from entering that player's
    hand, so the hand proposal is absent in that state.

    A Prism Star Energy proposes Lost Zone if it would go to discard.

    If both hand and Lost Zone remain live proposals, this layer deliberately
    leaves the result unresolved because the repository does not yet contain an
    authoritative ordering rule for that exact interaction.
    """

    prohibited = []
    hand_prohibited = opposing_scoop_up_block_active and holder_has_damage
    if hand_prohibited:
        prohibited.append("hand")

    candidates = []
    if dashing_pouch_active and not hand_prohibited:
        candidates.append(DestinationCandidate("Dashing Pouch", "hand"))
    if energy_is_prism_star:
        candidates.append(DestinationCandidate("Prism Star Rule", "lost_zone"))

    candidates = tuple(sorted(candidates))
    zones = {row.destination_zone for row in candidates}

    if not candidates:
        destination = "discard"
    elif len(zones) == 1:
        destination = next(iter(zones))
    else:
        destination = None

    return RetreatDestinationAnalysis(
        candidates,
        tuple(sorted(prohibited)),
        destination,
    )
