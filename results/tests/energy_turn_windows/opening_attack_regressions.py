"""SFT: print-specific opening attack window coverage against card JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from opening_attack_permissions import (
    OpeningKind, classify, counts, legal_opening_attack, scan_card_dir,
)


def main() -> None:
    rows = scan_card_dir(ROOT / "resources" / "cards" / "en")
    assert len(rows) == 51
    assert counts(rows) == {
        "first_player_exception": 21,
        "second_first_banned": 8,
        "second_first_bonus": 10,
        "second_first_only": 12,
    }
    by_id = {(row.print_id, row.attack_name): row for row in rows}
    assert len(by_id) == len(rows)
    examples = {
        ("sm5-73", "Sneaky Smash"): OpeningKind.SECOND_FIRST_ONLY,
        ("sm5-140", "Fast Raid"): OpeningKind.FIRST_PLAYER_EXCEPTION,
        ("sm8-96", "Quick Hunt"): OpeningKind.FIRST_PLAYER_EXCEPTION,
        ("swsh9-45", "Fast Charge"): OpeningKind.FIRST_PLAYER_EXCEPTION,
        ("sv7-128", "Unified Beatdown"): OpeningKind.SECOND_FIRST_BANNED,
        ("swsh6-64", "Crescent Glow"): OpeningKind.SECOND_FIRST_BONUS,
        ("sv6-94", "Scream"): OpeningKind.SECOND_FIRST_ONLY,
        ("me1-105", "Quick Gift"): OpeningKind.FIRST_PLAYER_EXCEPTION,
    }
    for key, expected in examples.items():
        assert by_id[key].kind is expected, key

    # Attacks that explicitly override the going-first rule still cannot
    # authorize an ordinary sibling attack with no exception on its text.
    assert legal_opening_attack(
        by_id[("sm5-140", "Fast Raid")].kind,
        went_first=True, own_turn=1,
    )
    assert not legal_opening_attack(None, went_first=True, own_turn=1)
    assert not legal_opening_attack(
        by_id[("sv7-128", "Unified Beatdown")].kind,
        went_first=False, own_turn=1,
    )
    assert not legal_opening_attack(
        by_id[("sv6-94", "Scream")].kind,
        went_first=False, own_turn=2,
    )
    assert legal_opening_attack(
        by_id[("swsh6-64", "Crescent Glow")].kind,
        went_first=False, own_turn=1,
    )

    # Enumerate role and own-turn truth-table for every classified family.
    for kind in OpeningKind:
        for went_first in (False, True):
            for own_turn in (1, 2, 3):
                actual = legal_opening_attack(
                    kind, went_first=went_first, own_turn=own_turn
                )
                if kind is OpeningKind.SECOND_FIRST_ONLY:
                    expected = not went_first and own_turn == 1
                elif kind is OpeningKind.SECOND_FIRST_BANNED:
                    expected = not (not went_first and own_turn == 1)
                    expected = expected and not (went_first and own_turn == 1)
                elif kind is OpeningKind.FIRST_PLAYER_EXCEPTION:
                    expected = True
                else:
                    expected = not (went_first and own_turn == 1)
                assert actual == expected, (kind, went_first, own_turn)

    assert classify("This attack deals 40 damage") is None
    try:
        classify("During your first turn, you may do anything.")
    except ValueError:
        pass
    else:
        raise AssertionError("unrecognized first-turn wording silently accepted")

    print(json.dumps({
        "expanded_labeled_prints": len(rows),
        "classified": counts(rows),
        "verified_named_witnesses": len(examples),
        "attack_scoped_exceptions": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
