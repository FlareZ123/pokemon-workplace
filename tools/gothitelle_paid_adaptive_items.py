"""Additional paid Quick Ball capacity inside a first-turn Nest/VIP Item mix.

One mandatory Quick Ball discards Sky Field. Any further early Quick Ball
can search an additional Basic only if paid by a *separate* card from a
disjoint approved-discard category. At most min(extra Quick copies,
approved payment copies) additional searches are permitted.

Nest Ball and Battle VIP Pass provide distinct discard-free Basic
search capacity in parallel. Exact joint Prize conditioning and the
delayed Stage2/Rare Candy draw are evaluated in one fixed population.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from gothitelle_dual_use_joint_access import choose
from gothitelle_two_quick_joint_board import prize_conditioned_basic_search


MODES = ("one_quick", "paid_quick", "free_item_mix", "adaptive_all")


@dataclass(frozen=True)
class PaidAdaptiveSetup:
    total: int = 60
    opening: int = 7
    prizes: int = 6
    gothita: int = 3
    gothitelle: int = 2
    rare_candy: int = 4
    other_basics: int = 8
    quick_ball: int = 4
    sky_field: int = 2
    nest_ball: int = 4
    battle_vip_pass: int = 4
    approved_discard: int = 12

    @property
    def categories(self) -> tuple[int, ...]:
        first = (
            self.gothita, self.gothitelle, self.rare_candy,
            self.other_basics, self.quick_ball, self.sky_field,
            self.nest_ball, self.battle_vip_pass,
            self.approved_discard,
        )
        return first + (self.total-sum(first),)

    def __post_init__(self) -> None:
        if (
            min(self.categories) < 0 or self.opening < 1
            or self.prizes < 0
            or self.total-self.opening-self.prizes-2 < 0
            or self.other_basics == 0
        ):
            raise ValueError("invalid paid Item mix population")


@dataclass(frozen=True)
class PaidAdaptiveOdds:
    by_policy: dict[str, tuple[Fraction, ...]]
    legal_opener: Fraction

    def probability(self, mode: str) -> Fraction:
        return sum(self.by_policy[mode], Fraction())

    @property
    def paid_quick_gain_alone(self) -> Fraction:
        return (
            self.probability("paid_quick")
            - self.probability("one_quick")
        )

    @property
    def paid_quick_gain_with_free_items(self) -> Fraction:
        return (
            self.probability("adaptive_all")
            - self.probability("free_item_mix")
        )

    @property
    def paid_quick_interaction(self) -> Fraction:
        return (
            self.paid_quick_gain_with_free_items
            - self.paid_quick_gain_alone
        )


def exact_paid_adaptive_access(case: PaidAdaptiveSetup) -> PaidAdaptiveOdds:
    sizes = case.categories
    n, h = case.total, case.opening
    denominator = choose(n,h)*(n-h)
    rows = {
        mode:[Fraction(0) for _ in range(5)]
        for mode in MODES
    }
    for counts in product(
        *(range(min(size,h)+1) for size in sizes[:9])
    ):
        filler = h-sum(counts)
        if filler < 0 or filler > sizes[-1] or not counts[3]:
            continue
        opener = counts+(filler,)
        ways = 1
        for original,taken in zip(sizes,opener):
            ways *= choose(original,taken)
        available = tuple(
            size-taken for size,taken in zip(sizes,opener)
        )
        for first_type,first_ways in enumerate(available):
            if not first_ways:
                continue
            seen = tuple(
                count+int(index == first_type)
                for index,count in enumerate(opener)
            )
            if not seen[4] or not seen[5]:
                continue  # First Quick and Sky must both be in hand.
            need_g = int(seen[0] == 0)
            need_o = max(0,4-seen[3])
            missing = need_g+need_o
            if missing > 4:
                continue
            has_stage,has_candy = bool(seen[1]),bool(seen[2])
            if not has_stage and not has_candy:
                continue
            after_first = list(available)
            after_first[first_type] -= 1
            if missing == 0:
                chance = (
                    Fraction(1) if has_stage and has_candy
                    else Fraction(
                        after_first[2 if has_stage else 1],
                        n-h-1,
                    )
                )
            else:
                chance = prize_conditioned_basic_search(
                    case.prizes,tuple(after_first),
                    need_gothita=need_g,need_core=need_o,
                    gothitelle_seen=has_stage,
                    candy_seen=has_candy,
                )
            if not chance:
                continue
            weight = Fraction(ways*first_ways,denominator)*chance
            extra_paid_quick = min(seen[4]-1,seen[8])
            limits = {
                "one_quick":1,
                "paid_quick":1+extra_paid_quick,
                "free_item_mix":1+seen[6]+2*seen[7],
                "adaptive_all":1+extra_paid_quick+seen[6]+2*seen[7],
            }
            for mode,capacity in limits.items():
                if missing <= capacity:
                    rows[mode][missing] += weight

    legal = Fraction(
        choose(n,h)-choose(n-case.gothita-case.other_basics,h),
        choose(n,h),
    )
    return PaidAdaptiveOdds(
        {key:tuple(values) for key,values in rows.items()},
        legal,
    )
