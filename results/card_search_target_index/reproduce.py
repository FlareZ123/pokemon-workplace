"""Audit typed Trainer-search selectors against the legal Expanded card pool."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from card_search_target_index import (
    load_legal_target_candidates,
    matching_candidates,
)
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from typed_search_target_allocator import (
    BASIC_ENERGY,
    ITEM,
    POKEMON_TOOL,
    TYPE_PREFIX,
    selector_from_label,
)


def main() -> None:
    candidates = load_legal_target_candidates(ROOT / "resources")
    compiled = compile_multi_output_trainer_profiles(ROOT / "resources")
    labels = sorted(
        {
            output.label
            for profile in compiled
            for output in profile.base_outputs + profile.conditional_outputs
        }
    )

    coverage: dict[str, dict[str, object]] = {}
    for label in labels:
        matches = matching_candidates(label, candidates)
        selector = selector_from_label(label)
        row: dict[str, object] = {
            "print_candidates": len(matches),
            "unique_names": len({candidate.name for candidate in matches}),
        }

        if selector.distinct_prefix is not None:
            single_type = [
                candidate
                for candidate in matches
                if len(
                    {
                        tag
                        for tag in candidate.tags
                        if tag.startswith(TYPE_PREFIX)
                    }
                )
                == 1
            ]
            distinct_types = sorted(
                {
                    next(
                        tag
                        for tag in candidate.tags
                        if tag.startswith(TYPE_PREFIX)
                    )
                    for candidate in single_type
                }
            )
            row["single_type_print_candidates"] = len(single_type)
            row["distinct_type_tags"] = distinct_types
            assert len(distinct_types) >= 3

        assert matches, label
        coverage[label] = row

    basic_energy_candidates = [
        candidate
        for candidate in candidates
        if BASIC_ENERGY in candidate.tags
    ]
    untyped_basic_energy_names = sorted(
        {
            candidate.name
            for candidate in basic_energy_candidates
            if not any(tag.startswith(TYPE_PREFIX) for tag in candidate.tags)
        }
    )

    tool_candidates = [
        candidate
        for candidate in candidates
        if POKEMON_TOOL in candidate.tags
    ]
    assert tool_candidates
    assert all(ITEM not in candidate.tags for candidate in tool_candidates)
    assert untyped_basic_energy_names == []

    assert len(labels) == 23
    assert len(candidates) == 14829

    print(
        json.dumps(
            {
                "legal_print_candidates": len(candidates),
                "compiled_labels": len(labels),
                "labels_with_candidates": sum(
                    row["print_candidates"] > 0
                    for row in coverage.values()
                ),
                "pokemon_tools_tagged_as_items": sum(
                    ITEM in candidate.tags
                    for candidate in tool_candidates
                ),
                "basic_energy_unique_names": sorted(
                    {candidate.name for candidate in basic_energy_candidates}
                ),
                "untyped_basic_energy_names": untyped_basic_energy_names,
                "coverage": coverage,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
