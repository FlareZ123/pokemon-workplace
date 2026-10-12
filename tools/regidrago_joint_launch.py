"""Exact simultaneous Regidrago V access and Dragapult discard with Item capacity.

Single first-turn action window under declared restricted action language.
Both resources must be available in one sequence of physical Items.
Prize/starter conditioning are exact. Decisions can depend on hidden prizes:
this is a full-information feasibility envelope, not K0 play or win rate.
"""
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb


@dataclass(frozen=True)
class Build:
    regidrago_v: int = 4
    other_basics: int = 11
    dragapult: int = 1
    vip: int = 3
    quick_ball: int = 3
    treasure: int = 3
    compressor: int = 1
    safe: int = 0
    total: int = 60


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@lru_cache(maxsize=None)
def can_achieve_joint(
    rv_held: bool, dp_hand: int, vip: int, qb: int, mt: int,
    bc: int, safe: int, rv_deck: int, dp_deck: int, loaded: bool,
) -> bool:
    """Exact feasibility of a modeled Item sequence (finite and acyclic)."""
    if rv_held and loaded:
        return True

    # Compressor loads one source from the deck, without hand payment.
    if bc and dp_deck and can_achieve_joint(
        rv_held, dp_hand, vip, qb, mt, bc-1, safe,
        rv_deck, dp_deck-1, True,
    ):
        return True

    # First-turn VIP benches one remaining Regidrago V.
    if vip and rv_deck and can_achieve_joint(
        True, dp_hand, vip-1, qb, mt, bc, safe,
        rv_deck-1, dp_deck, loaded,
    ):
        return True

    # Quick Ball and Treasure can each discard a hand Dragapult. Restricted
    # category searches can choose zero, or search one Regidrago V.
    if dp_hand:
        for use_quick in (True, False):
            if (qb if use_quick else mt) == 0:
                continue
            nq = qb-int(use_quick)
            nm = mt-int(not use_quick)
            if can_achieve_joint(
                rv_held, dp_hand-1, vip, nq, nm, bc, safe,
                rv_deck, dp_deck, True,
            ):
                return True
            if rv_deck and can_achieve_joint(
                True, dp_hand-1, vip, nq, nm, bc, safe,
                rv_deck-1, dp_deck, True,
            ):
                return True

    # Exogenous discardable hand filler can pay for a Basic or Dragon search.
    if safe:
        if rv_deck:
            if qb and can_achieve_joint(
                True, dp_hand, vip, qb-1, mt, bc, safe-1,
                rv_deck-1, dp_deck, loaded,
            ):
                return True
            if mt and can_achieve_joint(
                True, dp_hand, vip, qb, mt-1, bc, safe-1,
                rv_deck-1, dp_deck, loaded,
            ):
                return True
        if mt and dp_deck and can_achieve_joint(
            rv_held, dp_hand+1, vip, qb, mt-1, bc, safe-1,
            rv_deck, dp_deck-1, loaded,
        ):
            return True

    return False


def analyze(build: Build, *, opener: int = 7, prizes: int = 6) -> dict[str, Fraction]:
    other = build.total-sum((
        build.regidrago_v, build.other_basics, build.dragapult, build.vip,
        build.quick_ball, build.treasure, build.compressor, build.safe,
    ))
    if min(build.__dict__.values()) < 0 or other < 0:
        raise ValueError('Invalid deck')
    groups = (
        build.regidrago_v, build.other_basics, build.dragapult, build.vip,
        build.quick_ball, build.treasure, build.compressor, build.safe, other,
    )
    visible = opener+1
    if visible+prizes > build.total:
        raise ValueError('Deck too small')
    numerators = {key: 0 for key in (
        'joint_any', 'joint_bc', 'joint_no_bc', 'regidrago_access',
        'dragapult_discard', 'joint_rv_start_held', 'joint_dp_start_held',
        'joint_both_absent_start',
    )}
    denominator = 0
    for prefix in product(*(range(min(n, visible)+1) for n in groups[:-1])):
        rest = visible-sum(prefix)
        if not 0 <= rest <= other:
            continue
        hand = (*prefix, rest)
        basics = hand[0]+hand[1]
        allowed = visible if basics >= 2 else visible-1 if basics == 1 else 0
        if not allowed:
            continue
        hand_ways = allowed
        for count, held in zip(groups, hand):
            hand_ways *= choose(count, held)
        unknown_rv = build.regidrago_v-hand[0]
        unknown_dp = build.dragapult-hand[2]
        remaining = build.total-visible-unknown_rv-unknown_dp
        for prized_rv in range(min(prizes, unknown_rv)+1):
            for prized_dp in range(min(prizes-prized_rv, unknown_dp)+1):
                prize_ways = (
                    choose(unknown_rv, prized_rv)
                    * choose(unknown_dp, prized_dp)
                    * choose(remaining, prizes-prized_rv-prized_dp)
                )
                if not prize_ways:
                    continue
                weight = hand_ways*prize_ways
                denominator += weight
                rv_deck = unknown_rv-prized_rv
                dp_deck = unknown_dp-prized_dp
                state = (
                    hand[0] > 0, hand[2], hand[3], hand[4], hand[5],
                    hand[6], hand[7], rv_deck, dp_deck, False,
                )
                joint = can_achieve_joint(*state)
                without_bc = can_achieve_joint(*(state[:5]+(0,)+state[6:]))
                events = {
                    'joint_any': joint,
                    'joint_bc': joint and not without_bc,
                    'joint_no_bc': without_bc,
                    'regidrago_access': hand[0]>0 or (
                        rv_deck>0 and (hand[3]>0 or (
                            hand[4]+hand[5]>0 and hand[2]+hand[7]>0))),
                    'dragapult_discard': (
                        hand[6]>0 and dp_deck>0
                    ) or (
                        hand[2]>0 and hand[4]+hand[5]>0
                    ) or (
                        dp_deck>0 and hand[5]>0 and hand[7]>0
                        and hand[4]+hand[5]>=2
                    ),
                    'joint_rv_start_held': joint and hand[0]>0,
                    'joint_dp_start_held': joint and hand[2]>0,
                    'joint_both_absent_start': (
                        joint and not hand[0] and not hand[2]
                    ),
                }
                for key, yes in events.items():
                    if yes:
                        numerators[key] += weight
    if not denominator:
        raise ValueError('No valid opening hands')
    return {key: Fraction(value, denominator) for key, value in numerators.items()}


def candidates(safe: int = 0) -> dict[str, Build]:
    return {
        'published': Build(safe=safe),
        '+Dragapult -VIP': Build(dragapult=2, vip=2, safe=safe),
        '+Dragapult -Compressor': Build(dragapult=2, compressor=0, safe=safe),
        '+Dragapult -QB': Build(dragapult=2, quick_ball=2, safe=safe),
        '+Dragapult -MT': Build(dragapult=2, treasure=2, safe=safe),
    }


if __name__ == '__main__':
    for disposable in (0, 5, 10, 20, 30):
        print('safe', disposable)
        for name, build in candidates(disposable).items():
            probabilities = analyze(build)
            print(name, {
                key: f'{100 * float(probabilities[key]):.6f}%'
                for key in (
                    'joint_any', 'joint_no_bc', 'joint_bc',
                    'regidrago_access', 'dragapult_discard',
                )
            })
