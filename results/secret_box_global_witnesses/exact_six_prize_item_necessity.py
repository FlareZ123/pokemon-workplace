"""Exact all-six-Prized Item-output necessity in the Aichi compressed solver.

Enumerates multivariate-hypergeometric opening multisets, first draw, active
selection, and Jirachi Stellar Wish top-five *category presence*, with exact
integer multiplicities. Unlike the older 100k conditioned Monte Carlo, this
has zero sampling uncertainty. Card groups retain every distinction used by
the source first-turn core; all other physical identities are exchangeable.

One ACE SPEC differs between paired decks. The six forced Prizes are all
three Stealthy Hood, one Counter Gain, and both Artazon copies. The goal is
Bunnelby in play, TM: Evolution and Jet Energy in hand going second.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from accepted_opening_prize_probabilities import (
    fixed_nonbasic_prized_given_valid_opener,
)
from aichi_vileplume_secret_box import (
    HAND_INDEX, DECK_INDEX, _core_possible, BASE_DECK,
)

# Category positions are stable. Basic-other includes 10 ordinary Basics;
# filler-other includes the thirteen remaining nonBasic nonsearch cards.
GNH, TAG, TM, JET, ACE, BUN, FAN, JIR, BASIC, SUPPORT, TAG_OTHER, \
    SPECIAL_OTHER, FILLER = range(13)
COUNTS = (4, 4, 2, 2, 1, 2, 1, 1, 10, 10, 1, 3, 13)
assert sum(COUNTS) == 54
ACE_HAND = HAND_INDEX["secret_box"]
H_ROLE = {
    GNH: HAND_INDEX["gnh"],
    TAG: HAND_INDEX["tag_call"],
    TM: HAND_INDEX["tm_evolution"],
    JET: HAND_INDEX["jet_energy"],
    ACE: ACE_HAND,
    BUN: HAND_INDEX["bunnelby"],
    FAN: HAND_INDEX["fan_rotom"],
}
D_ROLE = {
    GNH: DECK_INDEX["gnh"],
    TAG: DECK_INDEX["tag_call"],
    TM: DECK_INDEX["tm_evolution"],
    JET: DECK_INDEX["jet_energy"],
    ACE: DECK_INDEX["secret_box"],
    BUN: DECK_INDEX["bunnelby"],
    SUPPORT: DECK_INDEX["supporter_other"],
    TAG_OTHER: DECK_INDEX["tag_team_other"],
    SPECIAL_OTHER: DECK_INDEX["special_energy_other"],
}
STELLAR = (GNH, TAG, TM, ACE)
UNSEEN_TOP = comb(46, 5)
ACTIVE_MULTIPLIER = 840  # lcm(1..8): exact first non-Bunnelby Basic choice.


def composition(k, stocks=COUNTS):
    if not stocks:
        if k == 0:
            yield ()
        return
    for n in range(min(stocks[0], k) + 1):
        for rest in composition(k-n, stocks[1:]):
            yield (n,) + rest


def physical_combinations(opening):
    product = 1
    for total, count in zip(COUNTS, opening):
        product *= comb(total, count)
    return product


@lru_cache(maxsize=None)
def top_masks(stocks):
    """Numbers of unordered five-card subsets with each exact hit mask."""
    other = 46 - sum(stocks)
    assert other >= 0
    out = []
    for mask in range(16):
        n = 0
        subset = mask
        while True:
            allowed = other + sum(
                stocks[i] for i in range(4) if subset & (1 << i)
            )
            n += (-1 if (mask.bit_count()-subset.bit_count()) % 2 else 1) \
                * comb(allowed, 5) if allowed >= 5 else 0
            if subset == 0:
                break
            subset = (subset-1) & mask
        assert n >= 0
        if n:
            out.append((mask, n))
    assert sum(n for _, n in out) == UNSEEN_TOP
    return tuple(out)


def active_variants(opening):
    """Exactly follows the repository's starting-Active selection policy."""
    if opening[JIR]:
        return (("Jirachi", ACTIVE_MULTIPLIER),)
    n_fan = opening[FAN]
    n_other = opening[BASIC]
    if n_fan + n_other:
        total = n_fan + n_other
        assert ACTIVE_MULTIPLIER % total == 0
        return tuple(
            (identity, ACTIVE_MULTIPLIER * count // total)
            for identity, count in (
                ("Fan Rotom", n_fan), ("other Basic", n_other)
            ) if count
        )
    if opening[BUN]:
        return (("Bunnelby", ACTIVE_MULTIPLIER),)
    return ()


def state(opening, draw, active, secret):
    hand = [0] * len(HAND_INDEX)
    deck = [0] * len(DECK_INDEX)
    exposed = tuple(n+int(i == draw) for i, n in enumerate(opening))
    for i, qty in enumerate(exposed):
        if not qty:
            continue
        if i == ACE and not secret:
            hand[HAND_INDEX["other"]] += qty
        else:
            hand[H_ROLE.get(i, HAND_INDEX["other"])] += qty
    if active == "Jirachi" or active == "other Basic":
        hand[HAND_INDEX["other"]] -= 1
    elif active == "Fan Rotom":
        hand[HAND_INDEX["fan_rotom"]] -= 1
    else:
        assert active == "Bunnelby"
        hand[HAND_INDEX["bunnelby"]] -= 1
    for i, count in enumerate(COUNTS):
        remaining = count - exposed[i]
        if i in D_ROLE and (i != ACE or secret):
            deck[D_ROLE[i]] = remaining
    assert all(n >= 0 for n in hand + deck)
    flags = (False, False, False, active == "Bunnelby",
             active == "Fan Rotom")
    return tuple(hand), tuple(deck), flags


def picked_state(s, category):
    hand, deck, flags = s
    hi = H_ROLE[category]
    di = D_ROLE[category]
    assert deck[di] > 0
    hand = list(hand)
    deck = list(deck)
    hand[hi] += 1
    deck[di] -= 1
    return tuple(hand), tuple(deck), flags


def possible(s, mask):
    hand, deck, flags = s
    return _core_possible((hand, deck, *flags), mask)


def outcome(opening, draw, active, stellar_mask):
    secret = state(opening, draw, active, True)
    baseline = state(opening, draw, active, False)
    # Without Box in the hand or accessible via Jirachi, output masks
    # 15 and 14 are equivalent for this baseline first-turn planner.
    box_held = bool(secret[0][ACE_HAND])
    box_stellar = active == "Jirachi" and bool(stellar_mask & 8)
    if not (box_held or box_stellar):
        return False

    picks = [None]
    if active == "Jirachi":
        picks += [cat for bit, cat in enumerate(STELLAR)
                  if stellar_mask & (1 << bit)]
    def exists(use_secret, mask):
        s = secret if use_secret else baseline
        for pick in picks:
            if pick is ACE and not use_secret:
                continue
            if pick is None:
                candidate = s
            else:
                candidate = picked_state(s, pick)
            if possible(candidate, mask):
                return True
        return False

    # Check the failure of all outputs except Item first for pruning.
    if exists(True, 14):
        return False
    return exists(True, 15) and not exists(False, 15)


def main():
    accepted_combinations = comb(54, 7) - comb(40, 7)
    expected_total = accepted_combinations * 47 * UNSEEN_TOP * ACTIVE_MULTIPLIER
    accepted_weight = 0
    success_weight = 0
    by_access = defaultdict(int)
    considered = 0
    opener_count = 0

    for opening in composition(7):
        variations = active_variants(opening)
        if not variations:
            continue
        opener_count += 1
        hand_ways = physical_combinations(opening)
        assert sum(w for _, w in variations) == ACTIVE_MULTIPLIER

        for draw, pool in enumerate(COUNTS):
            available = pool - opening[draw]
            if available <= 0:
                continue
            weight_before_active = hand_ways * available
            after = tuple(pool - opening[i] - int(draw == i)
                          for i, pool in enumerate(COUNTS))
            assert sum(after) == 46

            for active, active_weight in variations:
                leading = weight_before_active * active_weight
                accepted_weight += leading * UNSEEN_TOP
                if active != "Jirachi":
                    if outcome(opening, draw, active, 0):
                        success_weight += leading * UNSEEN_TOP
                        by_access[("non-Jirachi", "Box held")] += \
                            leading * UNSEEN_TOP
                    considered += 1
                    continue

                stocks = tuple(after[i] for i in STELLAR)
                for mask, top_weight in top_masks(stocks):
                    if outcome(opening, draw, active, mask):
                        success_weight += leading * top_weight
                        access = (
                            "Box held" if opening[ACE] or draw == ACE
                            else "Stellar Box"
                        )
                        by_access[("Jirachi", access)] += leading * top_weight
                    considered += 1

        if opener_count % 1000 == 0:
            print("processed_opening_groups", opener_count,
                  "test_branches", considered, flush=True)
            if _core_possible.cache_info().currsize > 250_000:
                _core_possible.cache_clear()

    assert accepted_weight == expected_total, (
        accepted_weight, expected_total,
    )
    assert 0 < success_weight < accepted_weight
    conditional = Fraction(success_weight, accepted_weight)
    exact_prizes = fixed_nonbasic_prized_given_valid_opener(
        cards=60, basics=14, opening=7, prizes=6, forced_nonbasic=6,
    )
    unconditional = exact_prizes * conditional

    for (active, access), weight in sorted(by_access.items()):
        print("source", active, access,
              "conditional_given_prizes", Fraction(weight, accepted_weight))
    print("accepted_opening_group_count", opener_count)
    print("tested_branches", considered)
    print("conditional_item_necessity", conditional, float(conditional))
    print("exact_forced_prize_probability", exact_prizes)
    print("unconditional_item_necessity", unconditional,
          float(unconditional))
    print("expected_cases_in_100k_forced_prize_samples",
          float(conditional * 100_000))
    assert unconditional >= Fraction(1, 4570469263360)
    print("Full exact six-Prize Item necessity enumeration passed.")


if __name__ == "__main__":
    main()
