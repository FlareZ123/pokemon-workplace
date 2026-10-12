"""Adaptive Trainers' Mail allocation between VIP Pass and Ultra Ball.

Each physical Mail selects at most one Trainer from the inspected top k.
A Mail selecting VIP cannot simultaneously retrieve Ultra. A successful
selection removes one deck card; every remaining card is shuffled.

This is a deliberately conditioned 46-card Mew/Genesect microstate, not
an unconditional opening frequency or win-rate estimate.
"""

from __future__ import annotations

import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path


def both_targets(
    deck_size: int,
    vip_in_deck: int,
    ultra_in_deck: int,
    held_mail: int,
    *,
    look_size: int = 4,
    policy: str = "optimal",
) -> Fraction:
    """Exact finite adaptive search policy over physical one-output Mail."""
    assert deck_size >= vip_in_deck + ultra_in_deck
    assert held_mail >= 0
    assert policy in ("optimal", "vip_first", "ultra_first")

    @lru_cache(maxsize=None)
    def solve(
        n: int, vip: int, ultra: int, mails: int,
        need_vip: bool, need_ultra: bool,
    ) -> Fraction:
        if not need_vip and not need_ultra:
            return Fraction(1)
        if mails == 0:
            return Fraction(0)
        top = min(look_size, n)
        denominator = comb(n, top)
        success = Fraction(0)
        for seen_vip in range(min(top, vip) + 1):
            for seen_ultra in range(min(top - seen_vip, ultra) + 1):
                seen_other = top - seen_vip - seen_ultra
                if seen_other > n - vip - ultra:
                    continue
                probability = Fraction(
                    comb(vip, seen_vip)
                    * comb(ultra, seen_ultra)
                    * comb(n - vip - ultra, seen_other),
                    denominator,
                )
                skip = solve(
                    n, vip, ultra, mails - 1, need_vip, need_ultra
                )
                choose_vip = (
                    solve(n - 1, vip - 1, ultra, mails - 1, False, need_ultra)
                    if seen_vip and need_vip else None
                )
                choose_ultra = (
                    solve(n - 1, vip, ultra - 1, mails - 1, need_vip, False)
                    if seen_ultra and need_ultra else None
                )
                if policy == "optimal":
                    options = [skip]
                    if choose_vip is not None:
                        options.append(choose_vip)
                    if choose_ultra is not None:
                        options.append(choose_ultra)
                    value = max(options)
                elif policy == "vip_first":
                    value = (
                        choose_vip if choose_vip is not None else
                        choose_ultra if choose_ultra is not None else skip
                    )
                else:
                    value = (
                        choose_ultra if choose_ultra is not None else
                        choose_vip if choose_vip is not None else skip
                    )
                success += probability * value
        return success

    return solve(
        deck_size, vip_in_deck, ultra_in_deck,
        held_mail, True, True,
    )


def physical_oracle(
    deck_size: int,
    vip_in_deck: int,
    ultra_in_deck: int,
    held_mail: int,
    *,
    look_size: int = 2,
    policy: str = "optimal",
) -> Fraction:
    """Enumerate actual labeled top-k looks and physical target removal."""
    assert deck_size <= 10
    contents = tuple(
        [0] * vip_in_deck + [1] * ultra_in_deck
        + [2] * (deck_size - vip_in_deck - ultra_in_deck)
    )

    @lru_cache(maxsize=None)
    def search(
        ids: tuple[int, ...], mails: int,
        need_vip: bool, need_ultra: bool,
    ) -> Fraction:
        if not need_vip and not need_ultra:
            return Fraction(1)
        if mails == 0:
            return Fraction(0)
        looks = tuple(combinations(ids, min(look_size, len(ids))))
        success = Fraction(0)
        for top in looks:
            selected_vip = next(
                (i for i in top if contents[i] == 0), None
            )
            selected_ultra = next(
                (i for i in top if contents[i] == 1), None
            )
            skip = search(ids, mails - 1, need_vip, need_ultra)
            retrieve_vip = (
                search(
                    tuple(i for i in ids if i != selected_vip),
                    mails - 1, False, need_ultra,
                )
                if selected_vip is not None and need_vip else None
            )
            retrieve_ultra = (
                search(
                    tuple(i for i in ids if i != selected_ultra),
                    mails - 1, need_vip, False,
                )
                if selected_ultra is not None and need_ultra else None
            )
            if policy == "optimal":
                choices = [skip]
                if retrieve_vip is not None:
                    choices.append(retrieve_vip)
                if retrieve_ultra is not None:
                    choices.append(retrieve_ultra)
                value = max(choices)
            elif policy == "vip_first":
                value = (
                    retrieve_vip if retrieve_vip is not None else
                    retrieve_ultra if retrieve_ultra is not None else skip
                )
            else:
                value = (
                    retrieve_ultra if retrieve_ultra is not None else
                    retrieve_vip if retrieve_vip is not None else skip
                )
            success += value
        return success / len(looks)

    return search(
        tuple(range(deck_size)), held_mail, True, True
    )


def independent_graph_proxy(
    n: int, vip: int, ultra: int, mails: int,
    look_size: int = 4,
) -> Fraction:
    """Incorrect hypothetical joint probability from independent access."""
    inspected = min(look_size, n)
    miss_vip = Fraction(comb(n - vip, inspected), comb(n, inspected))
    miss_ultra = Fraction(comb(n - ultra, inspected), comb(n, inspected))
    return (1 - miss_vip ** mails) * (1 - miss_ultra ** mails)


def source_check() -> None:
    cards = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "resources" / "cards" / "en" / "xy6.json"
        ).read_text(encoding="utf-8")
    )
    mail = next(c for c in cards if c["id"] == "xy6-92")
    assert mail["name"] == "Trainers' Mail"
    assert "top 4 cards" in mail["rules"][0]
    assert "(except Trainers' Mail)" in mail["rules"][0]


def self_test() -> None:
    source_check()
    for n, vip, ultra, mails, look in (
        (8, 2, 2, 2, 2),
        (8, 1, 3, 2, 2),
        (9, 3, 2, 3, 2),
        (9, 2, 3, 3, 2),
    ):
        for policy in ("optimal", "vip_first", "ultra_first"):
            grouped = both_targets(
                n, vip, ultra, mails,
                look_size=look, policy=policy,
            )
            physical = physical_oracle(
                n, vip, ultra, mails,
                look_size=look, policy=policy,
            )
            assert grouped == physical, (
                n, vip, ultra, mails, policy, grouped, physical
            )
        print(f"Exact labeled physical Mail policy: {n}/{vip}/{ultra}/{mails} PASS")

    for mails in (1, 2, 3):
        optimum = both_targets(46, 3, 4, mails)
        vip_first = both_targets(46, 3, 4, mails, policy="vip_first")
        ultra_first = both_targets(46, 3, 4, mails, policy="ultra_first")
        naive = independent_graph_proxy(46, 3, 4, mails)
        assert optimum == vip_first >= ultra_first
        assert naive > optimum
        print(
            f"N46 VIP3 Ultra4 Mail{mails}: "
            f"optimal={float(optimum):.9%}, "
            f"VIP-priority={float(vip_first):.9%}, "
            f"Ultra-priority={float(ultra_first):.9%}, "
            f"independent graph proxy={float(naive):.9%}"
        )


if __name__ == "__main__":
    self_test()
