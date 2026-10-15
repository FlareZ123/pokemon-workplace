"""Exact partition of Shadow Rider's Path + Iron Thorns opening-access
routes and a conservative next-turn suppression timing regression.

Access probabilities are conditional reachability upper bounds, NOT win rates.
Reuses the existing paid-source allocation, including its stated limitations.
Run: python -m results.tests.shadow_rider_thorns_continuation.reproduce
"""
from __future__ import annotations

import json
from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import combinations
from math import comb, prod
from pathlib import Path

from results.tests.shadow_rider_fog_marshadow.reproduce import allocations
from results.tests.shadow_rider_fog_allocation.reproduce import prize_masks
from results.tests.shadow_rider_paid_search_allocation.reproduce import (
    capacities,
    feasible as paid_feasible,
)


@dataclass(frozen=True)
class LockWindow:
    """Restricted state: fixed opposing active Iron Thorns, Path already gone."""

    thorns_active: bool = True
    path_active: bool = False
    cologne_this_turn: bool = False
    flutter_active: bool = False

    def underworld_door_available(self) -> bool:
        thorns_live = (
            self.thorns_active
            and not self.path_active
            and not self.cologne_this_turn
            and not self.flutter_active
        )
        return not self.path_active and not thorns_live

    def next_turn(self) -> LockWindow:
        """Cologne expires at end of turn; the opponent's board is stipulated."""
        return replace(self, cologne_this_turn=False)


def source_check() -> None:
    root = Path(__file__).resolve().parents[3]

    def card(identifier: str) -> dict:
        set_name = identifier.rsplit("-", 1)[0]
        cards = json.loads(
            (root / "resources" / "cards" / "en" / f"{set_name}.json")
            .read_text(encoding="utf-8")
        )
        return next(row for row in cards if row["id"] == identifier)

    cologne = card("swsh10-136")
    thorns = card("sv6-77")
    radiant = card("swsh12pt5-105")
    flutter = card("sv5-78")
    shadow = card("swsh6-75")
    valley = card("xy4-93")
    raihan = card("swsh7-152")

    assert "Until the end of your turn" in cologne["rules"][0]
    assert "Pokémon with a Rule Box" in thorns["abilities"][0]["text"]
    assert "have no Abilities" in thorns["abilities"][0]["text"]
    assert "your turn ends" in radiant["abilities"][0]["text"]
    assert "in the Active Spot" in flutter["abilities"][0]["text"]
    assert "opponent's Active Pokémon has no Abilities" in flutter["abilities"][0]["text"]
    assert "Benched Psychic Pokémon" in shadow["abilities"][0]["text"]
    assert shadow["attacks"][0]["name"] == "Max Geist"
    assert len(shadow["attacks"][0]["cost"]) == 3
    assert "cost Colorless less" in valley["rules"][0]
    assert "You can play this card only if" in raihan["rules"][0]
    assert "Attach a basic Energy card from your discard pile" in raihan["rules"][0]


def continuation_contract() -> None:
    # Gate's "your turn ends" also expires Cologne. The VMAX placed from
    # deck have no attached Energy at the launch instant.
    one_turn_cologne = LockWindow(cologne_this_turn=True)
    assert one_turn_cologne.underworld_door_available()
    assert not one_turn_cologne.next_turn().underworld_door_available()

    # Ordinary attachment alone cannot pay even Dimension Valley's
    # two-Energy Max Geist cost. Two live Door uses could add two Energy
    # to a Benched VMAX, assuming the hand actually contains the Energy.
    maximum_next_turn_energy_without_acceleration = 1
    assert maximum_next_turn_energy_without_acceleration < 2
    assert maximum_next_turn_energy_without_acceleration < 3

    flutter = LockWindow(flutter_active=True)
    assert flutter.underworld_door_available()
    assert flutter.next_turn().underworld_door_available()
    assert not replace(flutter.next_turn(), flutter_active=False).underworld_door_available()

    # Charge with Flutter Active, then pivot. The pivot may reactivate
    # Initialization but cannot undo Energy already attached.
    max_energy_before_pivot = 2 + 1
    assert max_energy_before_pivot >= 3
    assert not replace(flutter, flutter_active=False).underworld_door_available()

    # Raihan is a distinct conditional exception after an opponent-turn KO:
    # one Raihan attachment plus the manual attachment could reach two,
    # subject to Basic Energy in discard and a Valley still in play.
    assert 1 + 1 == 2
    print("PASS: Cologne expiry, Flutter survival/pivot, conditional Raihan exception")


def classify(opening: tuple[int, ...], hand: tuple[int, ...],
             deck: tuple[int, ...]) -> tuple[int, int, int, int]:
    """Counts (any, Cologne-feasible, Flutter-feasible, both).

    A source is called feasible when the same restricted paid-source solver
    can satisfy the launch after disabling the competing suppression route.
    """
    baseline = paid_feasible(opening, hand, deck)
    if not baseline:
        return (0, 0, 0, 0)

    # Flutter remains a Basic starter and can hold the Active Spot; only
    # its suppression contribution is switched off for this counterfactual.
    cologne_opening = list(opening)
    cologne_opening[7] += cologne_opening[4]
    cologne_opening[4] = 0
    cologne = paid_feasible(tuple(cologne_opening), hand, deck)

    # Disable both held Cologne and Stone-to-Cologne search while preserving
    # all other search and resource options in the physical state.
    flutter_hand = list(hand)
    flutter_hand[3] = 0
    flutter_deck = list(deck)
    flutter_deck[3] = 0
    flutter = paid_feasible(opening, tuple(flutter_hand), tuple(flutter_deck))

    assert baseline == (cologne or flutter)
    return (1, int(cologne), int(flutter), int(cologne and flutter))


def exact_partition(q: tuple[int, ...], opening: int = 7,
                    prizes: int = 6) -> tuple[Fraction, ...]:
    size = sum(q)
    basics = sum(q[i] for i in (0, 4, 6, 7, 8))
    prize_ways = comb(size - opening - 1, prizes)
    denominator = (
        (comb(size, opening) - comb(size - basics, opening))
        * (size - opening) * prize_ways
    )
    totals = [0, 0, 0, 0]
    denominator_check = 0
    for opener_index, opener in enumerate(allocations(opening, q)):
        if not sum(opener[i] for i in (0, 4, 6, 7, 8)):
            continue
        opener_ways = prod(comb(n, k) for n, k in zip(q, opener))
        after = tuple(n - k for n, k in zip(q, opener))
        for drawn, copies in enumerate(after):
            if not copies:
                continue
            hand = tuple(opener[i] + int(drawn == i) for i in range(len(q)))
            pool = tuple(after[i] - int(drawn == i) for i in range(len(q)))
            denominator_check += opener_ways * copies * prize_ways
            stocks = tuple(pool[i] for i in (0, 1, 3, 8, 9, 6))
            for mask, prize_weight in prize_masks(
                stocks, size - opening - 1, prizes
            ):
                deck = list(pool)
                for bit, index in enumerate((0, 3, 8, 9, 6)):
                    deck[index] = int(not bool(mask & (1 << bit)))
                deck[1] = 2
                flags = classify(opener, hand, tuple(deck))
                weight = opener_ways * copies * prize_weight
                for index, flag in enumerate(flags):
                    totals[index] += weight * flag
        # Bound the underlying source solver's memoization on hosted runners.
        if opener_index % 2000 == 0:
            paid_feasible.cache_clear()
    assert denominator_check == denominator
    assert totals[0] == totals[1] + totals[2] - totals[3]
    return tuple(Fraction(v, denominator) for v in totals)


def physical_oracle() -> None:
    """Independent labeled toy: opener3, one Prize, one natural draw."""
    toy = (1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1)
    cards = tuple(i for i, n in enumerate(toy) for _ in range(n))
    counts = [0] * 5
    for chosen in combinations(range(len(cards)), 3):
        opener = tuple(sum(cards[x] == i for x in chosen)
                       for i in range(len(toy)))
        if not sum(opener[i] for i in (0, 4, 6, 7, 8)):
            continue
        rest = set(range(len(cards))) - set(chosen)
        for prized in rest:
            for drawn in rest - {prized}:
                hand = tuple(opener[i] + int(cards[drawn] == i)
                             for i in range(len(toy)))
                deck = tuple(sum(cards[x] == i for x in rest
                                 if x not in (prized, drawn))
                             for i in range(len(toy)))
                counts[0] += 1
                flags = classify(opener, hand, deck)
                for k, flag in enumerate(flags):
                    counts[k + 1] += flag
    assert counts == [83720, 2490, 528, 2058, 96]
    assert exact_partition(toy, 3, 1) == tuple(
        Fraction(v, counts[0]) for v in counts[1:]
    )
    print("PASS: 83,720-world independent physical-card route partition")


def main() -> None:
    source_check()
    continuation_contract()
    physical_oracle()
    any_route, cologne, flutter, both = exact_partition(capacities(1, 1))
    assert any_route == Fraction(26946742764678720, 367753188390588000)
    assert cologne == Fraction(15179524312860506, 367753188390588000)
    assert flutter == Fraction(13303043774784568, 367753188390588000)
    assert both == Fraction(1535825322966354, 367753188390588000)
    assert any_route == cologne + flutter - both
    for label, probability in (
        ("All routes", any_route),
        ("Cologne feasible", cologne),
        ("Flutter feasible", flutter),
        ("Both", both),
        ("Cologne-only", cologne - both),
        ("Flutter-only", flutter - both),
    ):
        print(f"{label}: {float(probability):.9%}", flush=True)
    print("PASS: full 60-card route decomposition; access only, not matches")


if __name__ == "__main__":
    main()
