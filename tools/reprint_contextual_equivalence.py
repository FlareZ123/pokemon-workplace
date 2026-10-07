from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.reprint_errata_resolution import ReprintResolver, build_reprint_resolver

HISTORICAL_REPRINT_SOURCE = (
    "https://assets.pokemon.com/assets/cms/pdf/op/tournaments/2012/"
    "2012_modified_legal_reprints.pdf"
)


@dataclass(frozen=True)
class ContextualDivergenceWitness:
    historical_card_id: str
    current_card_id: str
    witness_card_id: str
    name: str
    historical_restriction: str
    current_scope_fact: str
    consequence: str


def life_herb_pokemon_ex_witness(
    resources_root: Path,
    *,
    resolver: ReprintResolver | None = None,
) -> tuple[ContextualDivergenceWitness, ...]:
    resolver = resolver or build_reprint_resolver(resources_root)

    current = resolver.cards_by_id["sm7-136"]
    witness = resolver.cards_by_id["me55c-108"]
    if resolver.resolve("sm7-136").kind != "direct_legal":
        raise ValueError("Expected current Life Herb to be directly legal")
    if resolver.resolve("me55c-108").kind != "direct_legal":
        raise ValueError("Expected Classic Collection Scizor ex to be directly legal")
    if not any("Pokémon-ex" in rule for rule in witness.get("rules") or ()):
        raise ValueError("Witness card no longer identifies the historical Pokémon-ex class")

    current_text = " ".join(current.get("rules") or ())
    if "excluding Pokémon-ex" in current_text:
        raise ValueError("Current Life Herb unexpectedly retains the historical exclusion")

    rows: list[ContextualDivergenceWitness] = []
    for historical_id in ("ex5-90", "ex6-93"):
        historical = resolver.cards_by_id[historical_id]
        historical_text = " ".join(historical.get("rules") or ())
        if "excluding Pokémon-ex" not in historical_text:
            raise ValueError(f"Historical Life Herb restriction missing: {historical_id}")
        if historical["name"] != current["name"] != "Life Herb":
            raise ValueError("Life Herb name mismatch")

        rows.append(
            ContextualDivergenceWitness(
                historical_card_id=historical_id,
                current_card_id="sm7-136",
                witness_card_id="me55c-108",
                name="Life Herb",
                historical_restriction="historical printing cannot choose Pokémon-ex",
                current_scope_fact=(
                    "paper Expanded contains the directly legal Classic Collection Scizor ex, "
                    "whose rule text identifies it as Pokémon-ex"
                ),
                consequence=(
                    "the historical and current Life Herb texts permit different target sets "
                    "in the current Expanded card pool"
                ),
            )
        )

    return tuple(rows)


def summarize_contextual_divergence(
    resources_root: Path,
    *,
    resolver: ReprintResolver | None = None,
) -> dict[str, object]:
    witnesses = life_herb_pokemon_ex_witness(resources_root, resolver=resolver)
    return {
        "historical_source": HISTORICAL_REPRINT_SOURCE,
        "counts": {
            "life_herb_historical_prints_with_current_divergence": len(witnesses),
            "distinct_witness_cards": len({row.witness_card_id for row in witnesses}),
        },
        "witnesses": [
            {
                "historical_card_id": row.historical_card_id,
                "current_card_id": row.current_card_id,
                "witness_card_id": row.witness_card_id,
                "name": row.name,
                "historical_restriction": row.historical_restriction,
                "current_scope_fact": row.current_scope_fact,
                "consequence": row.consequence,
            }
            for row in witnesses
        ],
    }
