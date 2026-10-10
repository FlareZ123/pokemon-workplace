from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb
from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality, gameplay_fingerprint, load_json

BENCH_TRIGGER_RE = re.compile(r"play this Pokémon from your hand onto your Bench", re.IGNORECASE)


@dataclass(frozen=True)
class OpeningTriggerAnalysis:
    valid_start_probability: Fraction
    naive_success_given_valid: Fraction
    role_aware_success_given_valid: Fraction
    active_role_overstatement_given_valid: Fraction
    forced_active_support_given_valid: Fraction
    expected_support_in_opening_given_valid: Fraction
    expected_support_retained_given_valid: Fraction


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def analyze_opening_trigger_role(
    *,
    deck_size: int = 60,
    opening_size: int = 7,
    trigger_basics: int,
    other_basics: int,
    required_triggers: int = 1,
    available_bench_slots: int = 5,
) -> OpeningTriggerAnalysis:
    """Exact accepted-opening analysis for Basic Pokémon with Bench-entry triggers.

    The opening hand is accepted when it contains at least one Basic among
    ``trigger_basics`` and ``other_basics``. During setup one Basic must become
    Active. The player chooses the Active to preserve as many trigger Basics in
    hand as possible. Optional setup benching is omitted; ``available_bench_slots``
    is the number of slots intentionally left available for these trigger plays.
    """

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if opening_size <= 0 or opening_size > deck_size:
        raise ValueError("opening_size must be in 1..deck_size")
    if trigger_basics < 0 or other_basics < 0:
        raise ValueError("Basic counts must be non-negative")
    if trigger_basics + other_basics > deck_size:
        raise ValueError("Basic counts cannot exceed deck_size")
    if required_triggers <= 0:
        raise ValueError("required_triggers must be positive")
    if available_bench_slots < 0 or available_bench_slots > 5:
        raise ValueError("available_bench_slots must be in 0..5")

    filler = deck_size - trigger_basics - other_basics
    denominator = _choose(deck_size, opening_size)

    valid_mass = 0
    naive_success_mass = 0
    role_success_mass = 0
    forced_support_mass = 0
    support_count_mass = 0
    retained_count_mass = 0

    for support_count in range(min(trigger_basics, opening_size) + 1):
        max_other = min(other_basics, opening_size - support_count)
        for other_count in range(max_other + 1):
            filler_count = opening_size - support_count - other_count
            ways = (
                _choose(trigger_basics, support_count)
                * _choose(other_basics, other_count)
                * _choose(filler, filler_count)
            )
            if ways == 0 or support_count + other_count == 0:
                continue

            valid_mass += ways
            support_count_mass += ways * support_count

            must_use_support_as_active = other_count == 0 and support_count > 0
            retained_support = support_count - int(must_use_support_as_active)
            retained_count_mass += ways * retained_support
            if must_use_support_as_active:
                forced_support_mass += ways

            naive_available = min(support_count, available_bench_slots)
            role_aware_available = min(retained_support, available_bench_slots)
            if naive_available >= required_triggers:
                naive_success_mass += ways
            if role_aware_available >= required_triggers:
                role_success_mass += ways

    if valid_mass == 0:
        zero = Fraction(0, 1)
        return OpeningTriggerAnalysis(zero, zero, zero, zero, zero, zero, zero)

    valid_probability = Fraction(valid_mass, denominator)
    naive = Fraction(naive_success_mass, valid_mass)
    role_aware = Fraction(role_success_mass, valid_mass)

    return OpeningTriggerAnalysis(
        valid_start_probability=valid_probability,
        naive_success_given_valid=naive,
        role_aware_success_given_valid=role_aware,
        active_role_overstatement_given_valid=naive - role_aware,
        forced_active_support_given_valid=Fraction(forced_support_mass, valid_mass),
        expected_support_in_opening_given_valid=Fraction(support_count_mass, valid_mass),
        expected_support_retained_given_valid=Fraction(retained_count_mass, valid_mass),
    )


def scan_literal_bench_trigger_basics(resources_root: Path) -> dict[str, Any]:
    """Catalog legal Expanded Basic Pokémon with literal hand-to-Bench triggers."""

    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    prints: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            if "Basic" not in (card.get("subtypes") or []):
                continue

            matching = [
                ability
                for ability in (card.get("abilities") or [])
                if BENCH_TRIGGER_RE.search(ability.get("text", ""))
            ]
            if not matching:
                continue

            prints.append(
                {
                    "id": card["id"],
                    "name": card["name"],
                    "fingerprint": gameplay_fingerprint(card),
                    "abilities": matching,
                }
            )

    return {
        "print_count": len(prints),
        "unique_names": len({row["name"] for row in prints}),
        "gameplay_variants": len({row["fingerprint"] for row in prints}),
        "names": sorted({row["name"] for row in prints}),
        "prints": prints,
    }
