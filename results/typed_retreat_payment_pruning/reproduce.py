"""Compare full legal payment minimax against minimal-payment solver."""
from __future__ import annotations
from collections import Counter
from dataclasses import replace
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.typed_retreat_gust import Target, minimum_attacks, retreat_payment_remainders


@lru_cache(None)
def full_payment_remainders(energy_cards: tuple[int, ...], cost: int) -> tuple[tuple[int, ...], ...]:
    """Retreat payments with no more than cost positive-unit physical cards."""
    if cost < 0:
        raise ValueError("negative Retreat Cost")
    if cost == 0:
        return (energy_cards,)
    results = set()
    for size in range(1, min(len(energy_cards), cost) + 1):
        for chosen in combinations(range(len(energy_cards)), size):
            if sum(energy_cards[i] for i in chosen) >= cost:
                results.add(tuple(x for i, x in enumerate(energy_cards) if i not in chosen))
    return tuple(sorted(results))


@lru_cache(None)
def minimum_attacks_full(
    active: Target, bench: tuple[Target, ...], gusts: int,
    switch_items: int = 0, item_play_allowed: bool = True, prizes_needed: int = 6,
) -> int:
    """Independent attack-min / defense-max solver with every legal payment."""
    attack_choices = [(active, bench, gusts)]
    if gusts:
        for i, target in enumerate(bench):
            rest = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
            attack_choices.append((target, rest, gusts - 1))
    costs = []
    for target, others, remaining_gusts in attack_choices:
        if target.hits > 1:
            wounded = replace(target, hits=target.hits - 1)
            replies = [minimum_attacks_full(
                wounded, others, remaining_gusts, switch_items, item_play_allowed, prizes_needed,
            )]
            for i, replacement in enumerate(others):
                rest = others[:i] + others[i + 1:]
                if not wounded.retreat_blocked:
                    for leftover in full_payment_remainders(wounded.energy_cards, wounded.retreat_cost):
                        moved = replace(wounded, energy_cards=leftover)
                        replies.append(minimum_attacks_full(
                            replacement, tuple(sorted((moved,) + rest)), remaining_gusts,
                            switch_items, item_play_allowed, prizes_needed,
                        ))
                if switch_items and item_play_allowed:
                    replies.append(minimum_attacks_full(
                        replacement, tuple(sorted((wounded,) + rest)), remaining_gusts,
                        switch_items - 1, item_play_allowed, prizes_needed,
                    ))
            costs.append(1 + max(replies))
        elif target.prize >= prizes_needed or not others:
            costs.append(1)
        else:
            costs.append(1 + max(
                minimum_attacks_full(
                    replacement, others[:i] + others[i + 1:], remaining_gusts,
                    switch_items, item_play_allowed, prizes_needed - target.prize,
                ) for i, replacement in enumerate(others)
            ))
    return min(costs)


def verify_payment_inclusion() -> int:
    total = 0
    found_redundancy = False
    for count in range(5):
        for cards in combinations_with_replacement((1, 2), count):
            for cost in range(5):
                full = full_payment_remainders(cards, cost)
                minimal = retreat_payment_remainders(cards, cost)
                assert set(minimal) <= set(full), (cards, cost)
                for f in full:
                    assert any(not (Counter(f) - Counter(m)) for m in minimal), (cards, cost, f)
                found_redundancy |= set(full) != set(minimal)
                total += len(full)
    assert found_redundancy and total == 107
    return total


def verify_two_pokemon() -> int:
    count = 0
    for p, h, c, e, bp, bh, bc, be, gust, item, allowed in product(
        (1, 3), (1, 2), (1, 2), ((), (1,), (1, 2)),
        (1, 3), (1, 2), (1, 2), ((), (1,), (2,)),
        (0, 1), (0, 1), (False, True),
    ):
        active = Target(p, h, c, e)
        bench = (Target(bp, bh, bc, be),)
        expected = minimum_attacks(active, bench, gust, item, allowed)
        actual = minimum_attacks_full(active, bench, gust, item, allowed)
        assert actual == expected, (active, bench, gust, item, allowed)
        count += 1
    assert count == 4608
    return count


def verify_three_pokemon() -> int:
    count = 0
    energies = ((), (1,), (2,), (1, 2))
    for ea, eb, ec, ca, cb, cc, gust, item in product(
        energies, energies, energies,
        (1, 2), (1, 2), (1, 2), (0, 1, 2), (0, 1),
    ):
        active = Target(2, 2, ca, ea)
        bench = tuple(sorted((Target(3, 2, cb, eb), Target(1, 2, cc, ec))))
        expected = minimum_attacks(active, bench, gust, item)
        actual = minimum_attacks_full(active, bench, gust, item)
        assert actual == expected, (active, bench, gust, item)
        count += 1
    assert count == 3072
    return count


def main() -> None:
    p = verify_payment_inclusion()
    a = verify_two_pokemon()
    b = verify_three_pokemon()
    print("Typed gust physical payment pruning: PASS")
    print({"physical_payment_remainders": p, "two_pokemon": a, "three_pokemon": b,
           "total_minimax_checks": a + b, "full_solver_cached_states": minimum_attacks_full.cache_info().currsize})


if __name__ == "__main__":
    main()
