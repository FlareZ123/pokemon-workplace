"""Conservative named-Pokémon Ability guard catalog for paper Expanded.

Scans exact "if/as long as you have [names] in play/on your Bench" clauses.
This is positive evidence only: it does not detect every dependency grammar,
or imply that the Ability is useful, usable, or active under other effects.
"""
from __future__ import annotations

import argparse
import json
import re
import unittest
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator

from build_expanded_legality_baseline import classify_effective_legality

GUARD = re.compile(
    r"\b(?P<guard>if|as long as) you have (?:an? |any )?"
    r"(?P<requirements>.+?) (?P<location>in play|on your Bench)\b",
    flags=re.IGNORECASE,
)
SPLIT_NAMES = re.compile(r",\s*(?:and\s+)?|\s+and\s+")


def iter_expanded_pokemon(root: Path) -> Iterator[dict[str, Any]]:
    sets = json.loads((root / "sets" / "en.json").read_text(encoding="utf-8"))
    expanded_ids = {
        row["id"] for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    for path in sorted((root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_ids:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if (
                card.get("supertype") == "Pokémon"
                and classify_effective_legality(card)[0] == "Legal"
            ):
                yield card


def minimum_bench_slots(
    source: str, required_names: tuple[str, ...], location: str
) -> int:
    """Necessary simultaneous Bench slots; one object can be Active."""
    unique_names = set((source, *required_names))
    if location.lower() == "on your bench":
        return max(len(set(required_names)), len(unique_names) - 1)
    return len(unique_names) - 1


def build(root: Path) -> dict[str, Any]:
    pokemon = list(iter_expanded_pokemon(root))
    legal_names = {card["name"] for card in pokemon}
    grouped: dict[tuple[Any, ...], list[str]] = defaultdict(list)
    omitted: dict[str, int] = defaultdict(int)

    for card in pokemon:
        for ability in card.get("abilities") or []:
            text = " ".join(ability.get("text", "").split())
            for match in GUARD.finditer(text):
                phrase = match.group("requirements").strip()
                prerequisites = tuple(
                    token.strip() for token in SPLIT_NAMES.split(phrase)
                )
                if not prerequisites or not all(name in legal_names for name in prerequisites):
                    omitted[phrase] += 1
                    continue
                loc = match.group("location").lower()
                guard = match.group("guard").lower()
                key = (
                    card["name"], ability["name"], prerequisites, loc, guard, text,
                )
                grouped[key].append(card["id"])

    entries = []
    for key in sorted(grouped, key=str):
        source, ability, prerequisites, location, guard, full_text = key
        entries.append({
            "source_name": source,
            "ability": ability,
            "guard": guard,
            "required_names": list(prerequisites),
            "location": location,
            "minimum_bench_slots": minimum_bench_slots(source, prerequisites, location),
            "source_in_required_names": source in prerequisites,
            "text": full_text,
            "print_ids": sorted(grouped[key]),
        })

    exact_single = {
        (entry["source_name"], entry["required_names"][0])
        for entry in entries
        if len(entry["required_names"]) == 1
        and entry["source_name"] != entry["required_names"][0]
    }
    reciprocal = sorted({
        tuple(sorted((a, b)))
        for a, b in exact_single
        if (b, a) in exact_single
    })
    return {
        "scope": "Paper Expanded, Black & White onward; legality-overlay and legal-set fallback",
        "method": "Conservative exact named-species Ability-guard extraction",
        "counts": {
            "legal_pokemon_prints_scanned": len(pokemon),
            "matched_prints": sum(len(group) for group in grouped.values()),
            "unique_guard_variants": len(entries),
            "sources": len({entry["source_name"] for entry in entries}),
            "five_bench_required_variants": sum(
                entry["minimum_bench_slots"] >= 5 for entry in entries
            ),
            "unparsed_guard_prints": sum(omitted.values()),
        },
        "reciprocal_single_name_pairs": reciprocal,
        "entries": entries,
        "unparsed_requirements": dict(sorted(omitted.items())),
    }


class NamedAbilityDependencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build(Path("resources"))

    def test_snapshot_coverage(self) -> None:
        counts = self.report["counts"]
        self.assertEqual(counts["matched_prints"], 38)
        self.assertEqual(counts["unique_guard_variants"], 25)
        self.assertEqual(counts["five_bench_required_variants"], 1)

    def test_regigigas_requires_five_bench_slots(self) -> None:
        matches = [
            row for row in self.report["entries"]
            if row["source_name"] == "Regigigas"
            and row["ability"] == "Ancient Wisdom"
        ]
        self.assertEqual(len(matches), 1)
        row = matches[0]
        self.assertEqual(row["print_ids"], ["swsh10-130"])
        self.assertEqual(
            row["required_names"],
            ["Regirock", "Regice", "Registeel", "Regieleki", "Regidrago"],
        )
        self.assertEqual(row["minimum_bench_slots"], 5)
        self.assertGreater(row["minimum_bench_slots"], 4)
        self.assertGreater(row["minimum_bench_slots"], 3)

    def test_conditional_pair_and_reciprocals(self) -> None:
        pairs = list(map(tuple, self.report["reciprocal_single_name_pairs"]))
        self.assertIn(("Karrablast", "Shelmet"), pairs)
        self.assertIn(("Lunala", "Solgaleo"), pairs)
        self.assertIn(("Lunatone", "Solrock"), pairs)
        self.assertTrue(any(
            row["source_name"] == "Lunatone"
            and row["ability"] == "Lunar Cycle"
            and "me1-74" in row["print_ids"]
            for row in self.report["entries"]
        ))

    def test_legal_set_fallback_catches_unmarked_2026_prints(self) -> None:
        self.assertTrue(any(
            row["source_name"] == "Illumise"
            and row["required_names"] == ["Volbeat"]
            and "me55-4" in row["print_ids"]
            for row in self.report["entries"]
        ))

    def test_minimum_capacity_formula(self) -> None:
        self.assertEqual(minimum_bench_slots("A", ("B",), "in play"), 1)
        self.assertEqual(minimum_bench_slots("A", ("B", "C"), "in play"), 2)
        self.assertEqual(minimum_bench_slots("A", ("A", "B"), "in play"), 1)
        self.assertEqual(minimum_bench_slots("A", ("B", "C"), "on your bench"), 2)
        self.assertEqual(minimum_bench_slots("A", ("A", "B"), "on your bench"), 2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["bench_named_ability_dependencies"], verbosity=2)
    else:
        print(json.dumps(build(args.resources_root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
