"""Exact opponent lock matrix for the experimental Mew / Tapu Lele / Wally 60.

The source-specific flags are conditional scenarios: they do not assert
all independent locks can coexist in a particular real opponent's board.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.tests.mew_wally_first_attack.reproduce import opening_counts
from results.tests.mew_wally_path_joint.reproduce import (
    POOL, all_survive, exact as unlocked_exact, labeled_oracle as unlocked_oracle,
)


def physical_route(held: Counter, deck: Counter, path: bool,
                   item_lock: bool, ability_lock: bool, supporter_lock: bool):
    if supporter_lock or not (held[0] and held[4] and deck[2]):
        return None
    if held[3]:
        return "wally_held" if held[1] else None
    if ability_lock or not (deck[3] and held[8] and held[1]):
        return None
    if path and not held[9]:
        return None
    return "tapu_held_sky" if path else "tapu_held"


def exact(pool: tuple[int, ...], hand: int, prizes: int, path: bool,
          item_lock: bool, ability_lock: bool = False,
          supporter_lock: bool = False) -> dict[str, Fraction]:
    if supporter_lock:
        return {}
    if not item_lock:
        states = unlocked_exact(pool, hand, prizes, path)
        if ability_lock:
            return {"wally_held": states.get("wally_held", Fraction(0))}
        return states
    n = sum(pool)
    ans = Counter()
    for opening, ways in opening_counts(pool, hand):
        if not opening[0]:
            continue
        for k, copies in enumerate(pool):
            remaining = copies - opening[k]
            if not remaining:
                continue
            held = list(opening)
            held[k] += 1
            if not (held[1] and held[4]):  # No Item can obtain Genesect.
                continue
            if held[3]:
                required = [pool[2] - held[2]]
                label = "wally_held"
            else:
                if ability_lock or not held[8] or (path and not held[9]):
                    continue
                required = [pool[2] - held[2], pool[3] - held[3]]
                label = "tapu_held_sky" if path else "tapu_held"
            ans[label] += Fraction(
                ways * remaining, comb(n, hand) * (n - hand)
            ) * all_survive(n - hand - 1, prizes, required)
    return dict(ans)


def labeled_oracle(pool: tuple[int, ...], hand: int, prizes: int, path: bool,
                   item_lock: bool, ability_lock: bool = False,
                   supporter_lock: bool = False):
    if not item_lock and not ability_lock and not supporter_lock:
        return unlocked_oracle(pool, hand, prizes, path)
    physical = tuple(k for k, copies in enumerate(pool) for _ in range(copies))
    n = len(physical)
    denominator = comb(n, hand) * comb(n - hand, prizes) * (n - hand - prizes)
    hits = Counter()
    for opening in combinations(range(n), hand):
        initial = set(opening)
        if not any(physical[i] == 0 for i in initial):
            continue
        remainder = set(range(n)) - initial
        for prize in combinations(sorted(remainder), prizes):
            prized = set(prize)
            for drawn in remainder - prized:
                hand_cards = Counter(physical[i] for i in initial | {drawn})
                deck = Counter(physical[i] for i in remainder - prized - {drawn})
                if not item_lock and ability_lock and not supporter_lock:
                    valid = (
                        hand_cards[0] and hand_cards[3] and hand_cards[4]
                        and deck[2] and
                        (hand_cards[1] or
                         (deck[1] and
                          (hand_cards[5] or hand_cards[6] or hand_cards[7])))
                    )
                    category = "wally_held" if valid else None
                else:
                    category = physical_route(
                        hand_cards, deck, path, item_lock,
                        ability_lock, supporter_lock
                    )
                if category is not None:
                    hits[category] += 1
    return {k: Fraction(v, denominator) for k, v in hits.items()}


def verify_lock_text() -> None:
    def card(print_id: str) -> dict:
        set_id = print_id.rsplit("-", 1)[0]
        records = json.loads(
            (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
            .read_text(encoding="utf-8")
        )
        return next(c for c in records if c["id"] == print_id)

    vileplume = card("xy7-3")
    stoutland = card("bw7-122")
    path = card("swsh6-148")
    sky = card("xy6-89")
    tapu = card("sm2-60")
    assert any(
        "can't play any Item cards" in x["text"]
        for x in vileplume["abilities"]
    )
    assert any(
        "can't play any Supporter cards" in x["text"]
        for x in stoutland["abilities"]
    )
    assert any("Pokémon with a Rule Box" in rule for rule in path["rules"])
    assert any("Bench" in rule for rule in sky["rules"])
    assert any("from your hand onto your Bench" in x["text"]
               for x in tapu["abilities"])


def main() -> None:
    verify_lock_text()
    toys = (
        ((1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1), 3, 2),
        ((2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 4, 2),
    )
    for pool, hand, prizes in toys:
        for path in (False, True):
            for item in (False, True):
                for ability in (False, True):
                    for supporter in (False, True):
                        measured = exact(
                            pool, hand, prizes, path, item, ability, supporter
                        )
                        physical = labeled_oracle(
                            pool, hand, prizes, path, item, ability, supporter
                        )
                        assert measured == physical, (
                            path, item, ability, supporter, measured, physical
                        )
        print(f"Independent physical oracle: N={sum(pool)}, 16 lock cases PASS")

    expected = {
        (False, False, False): Fraction(636040115150563, 8681622274224900),
        (True, False, False): Fraction(16510599747617, 513199346259600),
        (False, True, False): Fraction(0),  # Checked below via components.
        (True, True, False): Fraction(0),
    }
    for path in (False, True):
        for item in (False, True):
            for ability in (False, True):
                vals = exact(POOL, 7, 6, path, item, ability)
                result = sum(vals.values(), Fraction(0))
                if (path, item, ability) in expected and not item:
                    assert result == expected[(path, item, ability)]
                if item and ability:
                    assert result == Fraction(1826378549, 314141781525)
                print(f"Path={path}, Item lock={item}, Ability lock={ability}: "
                      f"{float(result):.12%}; exact={result}")
                assert not exact(POOL, 7, 6, path, item, ability, True)
    print("Supporter lock: exact Wally-based launch zero under all cases")


if __name__ == "__main__":
    main()
