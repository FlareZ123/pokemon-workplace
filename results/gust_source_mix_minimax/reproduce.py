"""Independent Boolean deadline oracle checks source-typed gust minimax."""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.gust_source_mix_minimax import TARGET_TYPES, boards, minimum_attack_turns


@lru_cache(maxsize=None)
def can_win_within(active, bench, items, supporters, prizes_needed, turns):
    """Independent Boolean alternating-game feasibility recurrence."""
    if prizes_needed <= 0:
        return True
    if turns <= 0:
        return False
    if not bench:
        return True
    for target_index in (-1, *range(len(bench))):
        if target_index == -1:
            knock = active
            remainder = bench
            source_left = ((items, supporters),)
        else:
            knock = bench[target_index]
            remainder = tuple(sorted(
                (active,) + bench[:target_index] + bench[target_index + 1 :]
            ))
            source_left = ()
            if items and TARGET_TYPES[knock].item_gust:
                source_left += ((items - 1, supporters),)
            if supporters and TARGET_TYPES[knock].supporter_gust:
                source_left += ((items, supporters - 1),)
        for next_items, next_supporters in source_left:
            if TARGET_TYPES[knock].prizes >= prizes_needed or not remainder:
                return True
            if all(
                can_win_within(
                    promotion, remainder[:j] + remainder[j + 1 :],
                    next_items, next_supporters,
                    prizes_needed - TARGET_TYPES[knock].prizes,
                    turns - 1,
                )
                for j, promotion in enumerate(remainder)
            ):
                return True
    return False


def validate_print_anchors():
    cases = {
        "swshp-SWSH155": ("Greninja V-UNION", "Ninja Body", "Item", "3 Prize"),
        "sm11-154": ("Axew", "Unnerve", "Item or Supporter", None),
        "sv10-65": ("Cetitan ex", "Snow Camouflage", "Item or Supporter", "2 Prize"),
    }
    for print_id, (name, ability, phrase, reward) in cases.items():
        set_id = print_id.split("-")[0]
        cards = json.loads(
            (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
                encoding="utf-8",
            )
        )
        row = next(card for card in cards if card["id"] == print_id)
        assert row["name"] == name
        assert row["legalities"]["expanded"] == "Legal"
        assert any(
            part["name"] == ability and phrase in part["text"]
            for part in row["abilities"]
        )
        if reward is not None:
            assert any(reward in rule for rule in row.get("rules", ()))

    ponchos = json.loads(
        (ROOT / "resources" / "cards" / "en" / "swsh12.json").read_text(
            encoding="utf-8",
        )
    )
    poncho = next(row for row in ponchos if row["id"] == "swsh12-160")
    assert poncho["name"] == "Leafy Camo Poncho"
    assert "Supporter card" in " ".join(poncho["rules"])
    assert "VSTAR or Pokémon VMAX" in " ".join(poncho["rules"])

    arceus = next(
        row for row in json.loads(
            (ROOT / "resources" / "cards" / "en" / "swsh9.json").read_text(
                encoding="utf-8",
            )
        )
        if row["id"] == "swsh9-123"
    )
    assert arceus["name"] == "Arceus VSTAR"
    assert any("2 Prize" in rule for rule in arceus["rules"])
    crobat = next(
        row for row in json.loads(
            (ROOT / "resources" / "cards" / "en" / "swsh45.json").read_text(
                encoding="utf-8",
            )
        )
        if row["id"] == "swsh45-45"
    )
    assert crobat["name"] == "Crobat VMAX"
    assert any("3 Prize" in rule for rule in crobat["rules"])


def main():
    validate_print_anchors()
    count = 0
    mixed_beats_both = mixed_worse_best = 0
    gains = Counter()
    losses = Counter()
    wins_by_size = Counter()
    for active, bench in boards():
        count += 1
        results = (
            minimum_attack_turns(active, bench, 2, 0),
            minimum_attack_turns(active, bench, 0, 2),
            minimum_attack_turns(active, bench, 1, 1),
        )
        improvement = min(results[:2]) - results[2]
        if improvement > 0:
            mixed_beats_both += 1
            gains[improvement] += 1
            wins_by_size[len(bench) + 1] += 1
        elif improvement < 0:
            mixed_worse_best += 1
            losses[-improvement] += 1
        for inventory, result in zip(((2, 0), (0, 2), (1, 1)), results):
            items, supporters = inventory
            assert can_win_within(
                active, bench, items, supporters, 6, result,
            ), (active, bench, inventory, result)
            assert not can_win_within(
                active, bench, items, supporters, 6, result - 1,
            ), (active, bench, inventory, result)

    assert count == 10107, count
    assert mixed_beats_both == 330, mixed_beats_both
    assert gains == Counter({1: 298, 2: 32}), gains
    assert wins_by_size == Counter({6: 207, 5: 89, 4: 29, 3: 5})
    assert mixed_worse_best == 991, mixed_worse_best
    assert losses == Counter({1: 869, 2: 122}), losses

    active, bench = "U1", ("I3", "S3")
    assert (
        minimum_attack_turns(active, bench, 2, 0),
        minimum_attack_turns(active, bench, 0, 2),
        minimum_attack_turns(active, bench, 1, 1),
    ) == (3, 3, 2)
    assert minimum_attack_turns("U1", ("S3",), 1, 0, 3) == 1
    assert minimum_attack_turns("S3", ("U1",), 1, 0, 3) == 1
    assert minimum_attack_turns("U1", ("U3", "U3"), 2, 0) == 2
    assert minimum_attack_turns("U1", ("U3", "U3"), 0, 2) == 2

    print(
        "gust_source_mix_minimax regression: PASS; "
        f"{count} abstract board/Active classes x 3 allocations = {count * 3} "
        "independently checked minimax/deadline scenarios"
    )
    print(
        f"mixed faster than both: {mixed_beats_both}; gains={dict(gains)}; "
        f"mixed slower than best homogeneous: {mixed_worse_best}; "
        f"losses={dict(losses)}; mixed winners by board size={dict(wins_by_size)}"
    )


if __name__ == "__main__":
    main()
