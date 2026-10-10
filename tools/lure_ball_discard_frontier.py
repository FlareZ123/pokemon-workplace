from __future__ import annotations

from fractions import Fraction
from itertools import product, permutations
from math import comb, perm

# The old Lure Ball uses "choose ... show" on the public discard pile.
# The newer wording uses "put", with choice implicit under rulebook II-D-04.
# This bounded model considers only Stage 1/Stage 2 Evolution targets;
# broader historical Evolution-card classification is a separate question.


def historical_frontier(eligible: tuple[str, ...], other: tuple[str, ...]) -> dict[tuple, Fraction]:
    possibilities: dict[tuple, Fraction] = {}
    initial = eligible + other
    for coins in product((False, True), repeat=3):
        hits = sum(coins)
        for chosen in permutations(eligible, min(hits, len(eligible))):
            after = tuple(x for x in initial if x not in chosen)
            # Reveal each chosen identity; the discard pile is already public.
            possibilities[(coins, chosen, after, chosen)] = Fraction(1, 8)
    return possibilities


def current_frontier(eligible: tuple[str, ...], other: tuple[str, ...]) -> dict[tuple, Fraction]:
    possibilities: dict[tuple, Fraction] = {}
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                hits = a + b + c
                for selected in permutations(eligible, min(hits, len(eligible))):
                    remaining = tuple(x for x in eligible + other if x not in selected)
                    # Retrieval from a public discard pile exposes the same IDs.
                    possibilities[((bool(a), bool(b), bool(c)), selected, remaining, selected)] = Fraction(1, 8)
    return possibilities


def exhaustive_comparison() -> dict[str, object]:
    total_worlds = 0
    total_outcomes = 0
    by_target_count: dict[int, int] = {}
    for n in range(7):
        expected_histories = sum(comb(3, h) * perm(n, min(h, n)) for h in range(4))
        for unrelated in range(4):
            eligible = tuple(f"E{i}" for i in range(n))
            others = tuple(f"X{i}" for i in range(unrelated))
            old = historical_frontier(eligible, others)
            new = current_frontier(eligible, others)
            assert old == new
            assert len(old) == expected_histories
            assert all(weight == Fraction(1, 8) for weight in old.values())
            total_worlds += 1
            total_outcomes += len(old)
        by_target_count[n] = expected_histories
    return {
        "source_states": total_worlds,
        "conditional_outcomes": total_outcomes,
        "histories_by_evolution_targets": by_target_count,
    }
