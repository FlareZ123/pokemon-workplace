"""Regidrago joint-launch K0 first-Item policy with adaptive K1 continuation.

The first search Item and its physical hand discard cost must be chosen
before inspecting remaining deck/Prize composition. The target of that first
search and all later modeled Item choices may adapt after deck inspection.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import product
from math import comb

from regidrago_joint_launch import Build, can_achieve_joint, choose


def first_actions(hand: tuple[int, ...]) -> tuple[str, ...]:
    """Hand indices: RV, other Basic, DP, VIP, QB, MT, BC, safe, other."""
    _rv, _basic, dp, vip, qb, mt, bc, safe, _other = hand
    choices = []
    if bc:
        choices.append("bc")
    if vip:
        choices.append("vip")
    if qb and dp:
        choices.append("qb_dp")
    if mt and dp:
        choices.append("mt_dp")
    if qb and safe:
        choices.append("qb_safe")
    if mt and safe:
        choices.append("mt_safe")
    return tuple(choices)


def first_action_succeeds(
    action: str,
    hand: tuple[int, ...],
    *,
    rv_deck: int,
    dp_deck: int,
) -> bool:
    """Existential search target/continuation choice after first search reveals K1."""
    rv, _basic, dp, vip, qb, mt, bc, safe, _other = hand
    has_rv = rv > 0
    if action == "bc":
        if not bc:
            raise ValueError("Battle Compressor unavailable")
        # Search may whiff on Dragon; non-payload deck cards can still be
        # discarded as a legal first search. Their count is not modeled.
        return can_achieve_joint(
            has_rv, dp, vip, qb, mt, bc - 1, safe,
            rv_deck, dp_deck - int(dp_deck > 0), dp_deck > 0,
        )
    if action == "vip":
        if not vip:
            raise ValueError("VIP unavailable")
        if rv_deck and can_achieve_joint(
            True, dp, vip - 1, qb, mt, bc, safe, rv_deck - 1, dp_deck, False,
        ):
            return True
        return can_achieve_joint(
            has_rv, dp, vip - 1, qb, mt, bc, safe, rv_deck, dp_deck, False,
        )

    item, payment = action.split("_", 1)
    if item not in {"qb", "mt"} or payment not in {"dp", "safe"}:
        raise ValueError("unknown first Item choice")
    if (qb if item == "qb" else mt) == 0 or (dp if payment == "dp" else safe) == 0:
        raise ValueError("first Item or its payment is absent")
    nq = qb - int(item == "qb")
    nm = mt - int(item == "mt")
    ndp = dp - int(payment == "dp")
    nsafe = safe - int(payment == "safe")
    loaded = payment == "dp"

    options = [(has_rv, ndp, rv_deck, dp_deck)]
    if rv_deck:
        options.append((True, ndp, rv_deck - 1, dp_deck))
    if item == "mt" and dp_deck:
        options.append((has_rv, ndp + 1, rv_deck, dp_deck - 1))
    return any(
        can_achieve_joint(
            held_rv, held_dp, vip, nq, nm, bc, nsafe,
            remaining_rv, remaining_dp, loaded,
        )
        for held_rv, held_dp, remaining_rv, remaining_dp in options
    )


def analyze_k0(build: Build, *, opener: int = 7, prizes: int = 6) -> dict[str, Fraction]:
    """Optimize first search Item over K0 Prize uncertainty for each observed hand."""
    other = build.total - sum((
        build.regidrago_v, build.other_basics, build.dragapult,
        build.vip, build.quick_ball, build.treasure, build.compressor, build.safe,
    ))
    if min(build.__dict__.values()) < 0 or other < 0 or opener < 1:
        raise ValueError("invalid build")
    if opener + 1 + prizes > build.total:
        raise ValueError("opening, Prizes and draw exceed deck size")
    groups = (
        build.regidrago_v, build.other_basics, build.dragapult,
        build.vip, build.quick_ball, build.treasure, build.compressor,
        build.safe, other,
    )
    visible = opener + 1
    numerator = Counter()
    denominator = 0
    action_names = ("bc", "vip", "qb_dp", "mt_dp", "qb_safe", "mt_safe")

    for prefix in product(*(range(min(n, visible) + 1) for n in groups[:-1])):
        remaining_hand = visible - sum(prefix)
        if not 0 <= remaining_hand <= other:
            continue
        hand = (*prefix, remaining_hand)
        basics = hand[0] + hand[1]
        placements = visible if basics >= 2 else opener if basics == 1 else 0
        if not placements:
            continue
        hand_ways = placements
        for n, selected in zip(groups, hand):
            hand_ways *= choose(n, selected)

        unknown_rv = build.regidrago_v - hand[0]
        unknown_dp = build.dragapult - hand[2]
        other_unknown = build.total - visible - unknown_rv - unknown_dp
        first = first_actions(hand)
        action_value = {a: 0 for a in first}
        oracle_value = 0
        prize_mass = 0

        for r_prized in range(min(prizes, unknown_rv) + 1):
            for d_prized in range(min(prizes - r_prized, unknown_dp) + 1):
                ways = (choose(unknown_rv, r_prized)
                        * choose(unknown_dp, d_prized)
                        * choose(other_unknown, prizes - r_prized - d_prized))
                if not ways:
                    continue
                prize_mass += ways
                rv_deck = unknown_rv - r_prized
                dp_deck = unknown_dp - d_prized
                oracle_value += ways * can_achieve_joint(
                    hand[0] > 0, hand[2], hand[3], hand[4], hand[5],
                    hand[6], hand[7], rv_deck, dp_deck, False,
                )
                for action in first:
                    action_value[action] += ways * first_action_succeeds(
                        action, hand, rv_deck=rv_deck, dp_deck=dp_deck,
                    )

        denominator += hand_ways * prize_mass
        numerator["clairvoyant_joint"] += hand_ways * oracle_value
        if first:
            best = max(first, key=action_value.__getitem__)
            numerator["k0_joint"] += hand_ways * action_value[best]
            numerator[f"first_{best}"] += hand_ways * prize_mass

    numerator["information_gap"] = (
        numerator["clairvoyant_joint"] - numerator["k0_joint"]
    )
    if not denominator:
        raise ValueError("no legal opening hands")
    return {
        metric: Fraction(numerator[metric], denominator)
        for metric in (
            "clairvoyant_joint", "k0_joint", "information_gap",
            *(f"first_{name}" for name in action_names),
        )
    }
