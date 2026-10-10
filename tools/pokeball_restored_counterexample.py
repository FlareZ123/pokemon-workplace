from __future__ import annotations

# An intentionally small type-domain witness. See the rulebook's special
# "Restored Pokémon" appendix: Restored is neither Basic nor Evolution.
# All three stages in this test are directly enumerated in source records.

OLD_TARGET_WORDING = "Basic Pokémon or Evolution card"
NEW_TARGET_WORDING = "Pokémon"


def old_pokeball_can_fetch(card: dict) -> bool:
    if card.get("supertype") != "Pokémon":
        return False
    stages = set(card.get("subtypes") or ())
    if "Restored" in stages:
        return False
    if "Basic" in stages or "Stage 1" in stages or "Stage 2" in stages:
        return True
    raise ValueError(f"Stage not independently audited: {card.get('id')}")


def new_pokeball_can_fetch(card: dict) -> bool:
    return card.get("supertype") == "Pokémon"


def search_option_sets(deck: tuple[dict, ...]) -> tuple[frozenset[str], frozenset[str]]:
    """Compare reachable targets after a heads result, including no-find."""
    old = frozenset(c["id"] for c in deck if old_pokeball_can_fetch(c))
    new = frozenset(c["id"] for c in deck if new_pokeball_can_fetch(c))
    return old, new
