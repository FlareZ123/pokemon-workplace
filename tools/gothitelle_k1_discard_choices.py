"""K1-aware discard-payment choices for the two-turn Gothitelle setup.

The first Quick Ball pays Sky Field and searches the deck, revealing
to its player which important card copies are Prized. If an additional
Quick Ball is needed for first-turn Basic capacity, the player can
pay with an approved disposable card or a *surplus* held resource
without jeopardizing the narrow turn-two evolution goal.

When one critical evolution card must be sacrificed to fund that
additional search, the player can make a K1-aware choice of which
piece to discard, based on the exact number of unprized replacement
Gothitelle versus Rare Candy copies. Only one turn-two draw remains.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from gothitelle_dual_use_joint_access import choose
from gothitelle_paid_adaptive_items import (
    PaidAdaptiveSetup, exact_paid_adaptive_access,
)
from gothitelle_two_quick_joint_board import prize_conditioned_basic_search


@dataclass(frozen=True)
class DynamicPaymentOdds:
    approved_only: Fraction
    safe_surplus_increment: Fraction
    k1_critical_increment: Fraction

    @property
    def safe_surplus_total(self) -> Fraction:
        return self.approved_only + self.safe_surplus_increment

    @property
    def k1_optimal_total(self) -> Fraction:
        return self.safe_surplus_total + self.k1_critical_increment


def k1_critical_discard_chance(
    remaining: tuple[int, ...],
    *,
    prizes: int,
    need_gothita: int,
    need_core: int,
) -> Fraction:
    """Optimally discard one critical T or C after observing Prize counts.

    Both types are currently held; after discarding the last retained
    copy of one of them, the next natural draw must replace that type.
    The choice is made after searching the deck, using the larger
    count of unprized Stage2 or Candy copies available in the deck.
    """
    unknown = sum(remaining)
    g,t,c,o = remaining[:4]
    other = unknown-g-t-c-o
    number_searched = need_gothita+need_core
    after_search = unknown-prizes-number_searched
    if after_search <= 0:
        return Fraction(0)
    denominator = choose(unknown,prizes)
    total = Fraction(0)
    for g_prized in range(min(g,prizes)+1):
        for o_prized in range(min(o,prizes-g_prized)+1):
            for t_prized in range(min(t,prizes-g_prized-o_prized)+1):
                for c_prized in range(
                    min(c,prizes-g_prized-o_prized-t_prized)+1
                ):
                    other_prized = (
                        prizes-g_prized-o_prized-t_prized-c_prized
                    )
                    ways = (
                        choose(g,g_prized)
                        * choose(o,o_prized)
                        * choose(t,t_prized)
                        * choose(c,c_prized)
                        * choose(other,other_prized)
                    )
                    if not ways:
                        continue
                    if (
                        g-g_prized < need_gothita
                        or o-o_prized < need_core
                    ):
                        continue
                    best_replacement = max(
                        t-t_prized,c-c_prized
                    )
                    total += (
                        Fraction(ways,denominator)
                        * Fraction(best_replacement,after_search)
                    )
    return total


def exact_dynamic_payment(case: PaidAdaptiveSetup) -> DynamicPaymentOdds:
    """Conservative baseline plus disjoint new first-turn payment paths.

    Only the *minimum* number of additional paid Quick Ball plays
    needed for the Bench goal is considered. Existing Nest and VIP
    cards are never sacrificed to pay Quick because doing so cannot
    add capacity for this Basic-only goal.

    Beyond the exogenously approved D category, safe spare cards are:
    another Sky Field, Gothita or ordinary Basic above the required
    amount, an additional Stage2 or Candy beyond one retained copy,
    and a Quick Ball copy left unused after the required plays.
    """
    old = exact_paid_adaptive_access(case)
    baseline = old.probability("adaptive_all")
    sizes = case.categories
    n,h = case.total,case.opening
    denominator = choose(n,h)*(n-h)
    safe_increment = Fraction(0)
    critical_increment = Fraction(0)

    for observed_counts in product(
        *(range(min(size,h)+1) for size in sizes[:9])
    ):
        filler = h-sum(observed_counts)
        if filler < 0 or filler > sizes[-1] or not observed_counts[3]:
            continue
        opener = observed_counts+(filler,)
        opener_ways = 1
        for size,count in zip(sizes,opener):
            opener_ways *= choose(size,count)
        unknown_after_opener = tuple(
            size-count for size,count in zip(sizes,opener)
        )

        for first_type,first_ways in enumerate(unknown_after_opener):
            if not first_ways:
                continue
            seen = tuple(
                count+int(i==first_type)
                for i,count in enumerate(opener)
            )
            if not seen[4] or not seen[5] or not (seen[1] or seen[2]):
                continue
            missing_g = int(seen[0] == 0)
            missing_o = max(0,4-seen[3])
            missing = missing_g+missing_o
            if missing > 4:
                continue
            free_capacity = 1+seen[6]+2*seen[7]
            additional_q = max(0,missing-free_capacity)
            if additional_q == 0 or seen[4]-1 < additional_q:
                continue
            if seen[8] >= additional_q:
                continue  # The old approved-only model already succeeds.

            extra_safe = (
                seen[8]
                + seen[5]-1  # Sky used by first Quick already
                + max(0,seen[0]-1)
                + max(0,seen[3]-4)
                + max(0,seen[1]-1)
                + max(0,seen[2]-1)
                + seen[4]-1-additional_q
            )
            after_first = list(unknown_after_opener)
            after_first[first_type] -= 1
            weight = Fraction(
                opener_ways*first_ways,denominator
            )

            if extra_safe >= additional_q:
                continuation = prize_conditioned_basic_search(
                    case.prizes,tuple(after_first),
                    need_gothita=missing_g,
                    need_core=missing_o,
                    gothitelle_seen=bool(seen[1]),
                    candy_seen=bool(seen[2]),
                )
                safe_increment += weight*continuation
            elif (
                extra_safe == additional_q-1
                and seen[1]>=1 and seen[2]>=1
            ):
                continuation = k1_critical_discard_chance(
                    tuple(after_first),
                    prizes=case.prizes,
                    need_gothita=missing_g,
                    need_core=missing_o,
                )
                critical_increment += weight*continuation

    return DynamicPaymentOdds(
        approved_only=baseline,
        safe_surplus_increment=safe_increment,
        k1_critical_increment=critical_increment,
    )
