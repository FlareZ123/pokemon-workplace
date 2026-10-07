from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Relation = Literal["equivalent", "not_equivalent"]


@dataclass(frozen=True)
class PairEvidence:
    left_print_id: str
    right_print_id: str
    relation: Relation
    reason: str
    source: str


HANDBOOK_SOURCE = (
    "https://play.pokemon.com/en-gb/resources/documents/?filter=all"
)
ERRATA_SOURCE = (
    "https://play.pokemon.com/fr-ca/resources/documents/tcg-errata/"
)

# Worked examples from the Tournament Handbook section on reprinted cards.
HANDBOOK_PAIR_EVIDENCE = (
    PairEvidence(
        "ex7-83",
        "sm7-127",
        "equivalent",
        "Copycat wording changed while the described effect remained functionally identical.",
        HANDBOOK_SOURCE,
    ),
    PairEvidence(
        "base5-17",
        "sm7-151",
        "not_equivalent",
        "Rainbow Energy uses damage in the older printing and damage counters in the newer printing.",
        HANDBOOK_SOURCE,
    ),
)

# Current official errata page, last-update field 2024-11-07 as served in 2026.
# These are name-level major changes whose corrected text applies to older printings.
MAJOR_NAME_ERRATA = frozenset(
    {
        "Leftovers",
        "Super Rod",
        "Superior Energy Retrieval",
        "Rare Candy",
        "Potion",
        "Great Ball",
        "Pokémon Catcher",
        "Energy Retrieval",
        "Pal Pad",
        "Energy Recycler",
        "Lum Berry",
        "Sitrus Berry",
        "Hyper Potion",
        "Quick Ball",
        "PlusPower",
    }
)

ERRATA_LAST_UPDATE = "2024-11-07"


def normalized_pair(left_print_id: str, right_print_id: str) -> tuple[str, str]:
    return tuple(sorted((left_print_id, right_print_id)))


PAIR_RELATIONS = {
    normalized_pair(e.left_print_id, e.right_print_id): e
    for e in HANDBOOK_PAIR_EVIDENCE
}


def handbook_relation(left_print_id: str, right_print_id: str) -> PairEvidence | None:
    return PAIR_RELATIONS.get(normalized_pair(left_print_id, right_print_id))
