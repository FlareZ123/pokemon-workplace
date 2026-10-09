"""Joint adaptive Quick Ball, Nest Ball and Battle VIP Pass setup policy.

One first-turn Quick Ball discards Sky Field and searches at most one
Basic. Every available first-turn Nest Ball can directly Bench one,
and each Battle VIP Pass can Bench up to two. Their joint access is
evaluated in the SAME 60-card population rather than by adding
probabilities from alternative decks or overlapping policy events.

All relevant searched Basics must survive six random Prize cards.
The second natural draw may finish Candy and Gothitelle on turn two.
An exogenous compatible Collapsed Stadium/Barrier Shrine state and
the later two extra Bench entrants remain outside this access model.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from gothitelle_dual_use_joint_access import choose
from gothitelle_two_quick_joint_board import prize_conditioned_basic_search


MODES = ("quick_only", "nest_only", "vip_only", "adaptive")
PARTS = (
    "base", "nest_exclusive", "vip_exclusive",
    "shared_extra", "combined_only",
)


@dataclass(frozen=True)
class AdaptiveItemSetup:
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

    @property
    def categories(self) -> tuple[int, ...]:
        first = (
            self.gothita, self.gothitelle, self.rare_candy,
            self.other_basics, self.quick_ball, self.sky_field,
            self.nest_ball, self.battle_vip_pass,
        )
        return first + (self.total-sum(first),)

    def __post_init__(self) -> None:
        if (
            min(self.categories) < 0 or self.opening < 1
            or self.prizes < 0
            or self.total - self.opening - self.prizes - 5 <= 0
            or self.other_basics == 0
        ):
            raise ValueError("invalid adaptive Item search population")


@dataclass(frozen=True)
class AdaptiveItemOdds:
    """Each mode is a five-element exact fraction row, indexed by
    number of missing Basics in the original first eight cards.
    Partition classes assign each success state once and only once.
    """
    per_mode: dict[str, tuple[Fraction, ...]]
    decomposition: dict[str, tuple[Fraction, ...]]
    legal_opener: Fraction

    def probability(self, mode: str) -> Fraction:
        return sum(self.per_mode[mode], Fraction())

    def component(self, name: str) -> Fraction:
        return sum(self.decomposition[name], Fraction())

    @property
    def positive_complementarity(self) -> Fraction:
        """Joint combined success beyond additive marginal improvement."""
        return (
            self.component("combined_only")
            - self.component("shared_extra")
        )


def exact_adaptive_item_access(case: AdaptiveItemSetup) -> AdaptiveItemOdds:
    """Count first-turn Item copies as typed action bandwidth.

    Quick is the single mandatory search/payment connector. Every
    already-observed Nest has one Basic-Bench placement capacity and
    every observed first-turn VIP has two. Optional use means there is
    no need to exhaust capacity when fewer targets remain missing.
    """
    categories = case.categories
    n, opening = case.total, case.opening
    denominator = choose(n, opening) * (n-opening)
    mode_rows = {
        mode: [Fraction(0) for _ in range(5)] for mode in MODES
    }
    part_rows = {
        name: [Fraction(0) for _ in range(5)] for name in PARTS
    }
    for first_seven in product(
        *(range(min(count, opening)+1) for count in categories[:8])
    ):
        filler = opening - sum(first_seven)
        if filler < 0 or filler > categories[-1] or not first_seven[3]:
            continue  # Require an ordinary Basic as the opening Active.
        opener = first_seven + (filler,)
        opener_ways = 1
        for size, seen in zip(categories, opener):
            opener_ways *= choose(size, seen)
        unknown_after_opener = tuple(
            size-seen for size, seen in zip(categories, opener)
        )
        for first_type, first_ways in enumerate(unknown_after_opener):
            if not first_ways:
                continue
            seen = tuple(
                value + int(first_type == i)
                for i, value in enumerate(opener)
            )
            if not seen[4] or not seen[5]:
                continue  # The mandatory Quick and Sky payload are absent.
            missing_g = int(seen[0] == 0)
            missing_o = max(0,4-seen[3])
            missing = missing_g+missing_o
            if missing > 4:
                continue
            has_stage = bool(seen[1])
            has_candy = bool(seen[2])
            if not has_stage and not has_candy:
                continue
            after_first = list(unknown_after_opener)
            after_first[first_type] -= 1
            if missing == 0:
                chance = (
                    Fraction(1) if has_stage and has_candy
                    else Fraction(
                        after_first[2 if has_stage else 1],
                        n-opening-1,
                    )
                )
            else:
                chance = prize_conditioned_basic_search(
                    case.prizes, tuple(after_first),
                    need_gothita=missing_g, need_core=missing_o,
                    gothitelle_seen=has_stage,
                    candy_seen=has_candy,
                )
            weight = (
                Fraction(opener_ways*first_ways, denominator)
                * chance
            )
            if not weight:
                continue
            capacities = {
                "quick_only": 1,
                "nest_only": 1+seen[6],
                "vip_only": 1+2*seen[7],
                "adaptive": 1+seen[6]+2*seen[7],
            }
            good = {
                mode: missing <= capacity
                for mode, capacity in capacities.items()
            }
            for mode, success in good.items():
                if success:
                    mode_rows[mode][missing] += weight
            if good["quick_only"]:
                partition = "base"
            elif good["nest_only"] and good["vip_only"]:
                partition = "shared_extra"
            elif good["nest_only"]:
                partition = "nest_exclusive"
            elif good["vip_only"]:
                partition = "vip_exclusive"
            elif good["adaptive"]:
                partition = "combined_only"
            else:
                continue
            part_rows[partition][missing] += weight

    legal = Fraction(
        choose(n,opening)
        - choose(n-case.gothita-case.other_basics,opening),
        choose(n,opening),
    )
    results = AdaptiveItemOdds(
        {key: tuple(values) for key,values in mode_rows.items()},
        {key: tuple(values) for key,values in part_rows.items()},
        legal,
    )
    assert results.probability("adaptive") == sum(
        (results.component(name) for name in PARTS), Fraction()
    )
    return results
