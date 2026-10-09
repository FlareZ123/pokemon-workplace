"""SFT: exact joint dual-use Quick Ball/Sky Field -> Gothitelle line."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_expanded_legality_baseline import classify_effective_legality
from gothitelle_dual_use_joint_access import DualUseSetup, exact_dual_use_access


def exhaustive(case: DualUseSetup) -> tuple[Fraction, Fraction]:
    """Independent labeled opener, Prize, T1 draw, search and T2 draw."""
    labels = "".join(
        symbol * copies for symbol, copies in zip(
            "GTCOQSX", case.categories
        )
    )
    ids = set(range(case.total))
    denominator = (
        comb(case.total, case.opening)
        * comb(case.total - case.opening, case.prizes)
        * (case.total - case.opening - case.prizes)
    )
    natural = Fraction(0)
    searched = Fraction(0)
    for opener in combinations(range(case.total), case.opening):
        seen_opening = {labels[i] for i in opener}
        if not ({"G", "O"} & seen_opening):
            continue
        remaining = ids - set(opener)
        for prize in combinations(sorted(remaining), case.prizes):
            deck = remaining - set(prize)
            for first in deck:
                seen = seen_opening | {labels[first]}
                if not {"Q", "S"} <= seen:
                    continue
                after_first = deck - {first}
                if "G" in seen:
                    live = after_first
                    wins = sum(
                        ("T" in seen or labels[i] == "T")
                        and ("C" in seen or labels[i] == "C")
                        for i in live
                    )
                    natural += Fraction(wins, len(live))
                else:
                    found = next(
                        (i for i in after_first if labels[i] == "G"), None
                    )
                    if found is None:
                        continue
                    live = after_first - {found}
                    wins = sum(
                        ("T" in seen or labels[i] == "T")
                        and ("C" in seen or labels[i] == "C")
                        for i in live
                    )
                    searched += Fraction(wins, len(live))
    return natural / denominator, searched / denominator


def grounded_cards() -> None:
    checks = {
        "xy3": ("xy3-39", "xy3-41"),
        "sv1": ("sv1-191",),
        "swsh1": ("swsh1-179",),
        "xy6": ("xy6-89",),
    }
    found = {}
    for set_code, ids in checks.items():
        rows = json.loads(
            (ROOT / "resources" / "cards" / "en" / f"{set_code}.json")
            .read_text(encoding="utf-8")
        )
        found.update({c["id"]: c for c in rows if c["id"] in ids})
    assert len(found) == 5
    assert all(classify_effective_legality(c)[0] == "Legal"
               for c in found.values())
    assert found["xy3-39"]["name"] == "Gothita"
    assert "Basic" in found["xy3-39"]["subtypes"]
    assert "Teleport Room" in {
        a["name"] for a in found["xy3-41"]["abilities"]
    }
    quick_text = " ".join(found["swsh1-179"]["rules"])
    assert "discard another card from your hand" in quick_text
    assert "Search your deck for a Basic Pokémon" in quick_text
    candy_text = " ".join(found["sv1-191"]["rules"])
    assert "Basic Pokémon that was put into play this turn" in candy_text
    assert "skipping the Stage 1" in candy_text
    assert found["xy6-89"]["name"] == "Sky Field"
    print("PASS legal print/type/text anchors for Gothita, Gothitelle, "
          "Rare Candy, Quick Ball, Sky Field")


def main() -> None:
    grounded_cards()
    small = DualUseSetup(
        total=11, opening=3, prizes=1,
        gothita=1, gothitelle=1, rare_candy=1,
        other_basics=2, quick_ball=2, sky_field=1,
    )
    richer = DualUseSetup(
        total=13, opening=3, prizes=2,
        gothita=2, gothitelle=1, rare_candy=1,
        other_basics=2, quick_ball=2, sky_field=2,
    )
    for case in (small, richer, replace(small, prizes=0)):
        odds = exact_dual_use_access(case)
        brute = exhaustive(case)
        assert (odds.natural_gothita, odds.searched_gothita) == brute
        print("PASS independently enumerated labeled paths", case, brute)
    assert (
        exact_dual_use_access(small).natural_gothita
        == exact_dual_use_access(replace(small, prizes=0)).natural_gothita
    )
    assert (
        exact_dual_use_access(small).searched_gothita
        != exact_dual_use_access(replace(small, prizes=0)).searched_gothita
    )
    base = DualUseSetup()
    result = exact_dual_use_access(base)
    assert result.natural_gothita == Fraction(130411081, 66524141970)
    assert result.searched_gothita == Fraction(
        1028083746728, 296863983541125
    )
    assert exact_dual_use_access(replace(base, quick_ball=0)).per_attempt == 0
    assert exact_dual_use_access(replace(base, sky_field=0)).per_attempt == 0
    assert exact_dual_use_access(replace(base, sky_field=1)).per_attempt < result.per_attempt
    assert exact_dual_use_access(replace(base, sky_field=3)).per_attempt > result.per_attempt
    print(json.dumps({
        "example": {
            "natural_percent": round(float(result.natural_gothita)*100, 9),
            "searched_percent": round(float(result.searched_gothita)*100, 9),
            "combined_percent": round(float(result.per_attempt)*100, 9),
            "conditional_legal_percent": round(
                float(result.conditional_legal_opener)*100, 9
            ),
        },
        "interpretation": "Joint access conditional on an independently established compatible board, a turn-two Teleport Room lock context, a held target Bench-entry demand and no intervening KO or Item/Ability lock.",
    }, indent=2))
    print("gothitelle_dual_use_joint_access regression: PASS")


if __name__ == "__main__":
    main()
