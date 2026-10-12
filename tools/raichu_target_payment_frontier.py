"""Exact source-payment to singleton Alolan Raichu access on Harto's 2024 list.

The one-Item, one-Supporter endpoint uses a seven-card valid Basic opener,
one Active, six unknown Prizes, then a natural draw going second. Source payments
use explicitly selected hypothetical discardability policies. No other setup,
search, draw Abilities, or retained-resource value is included.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb

CATEGORIES = ("target", "gladion", "ultra", "computer", "giratina",
              "other_basics", "energy", "protected")
DEFAULT = (1, 2, 3, 1, 1, 15, 11, 26)
POLICIES = ("strict", "ultra_spare", "non_ace_sources", "any_source", "extra_basics")
EVENTS = ("target_in_hand", "target_prized", "source_payable", "direct_access",
          "static_access", "adaptive_access", "prized_adaptive",
          "computer_prize_rescue")


def _choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def payment_options(hand: tuple[int, ...], policy: str) -> tuple[bool, bool]:
    """Return (Ultra payable, Computer payable), reserving each played source.

    Additional discard permissions are deliberately nested. Gladion and target
    remain protected because they are required for this endpoint.
    """
    if policy not in POLICIES:
        raise ValueError("unknown payment policy")
    _, _, u, c, g, b, f, _ = hand
    safe = g + f
    ultra_payment = safe + (u - 1 if policy != "strict" else 0)
    computer_payment = safe
    if policy in ("non_ace_sources", "any_source", "extra_basics"):
        computer_payment += u
    if policy in ("any_source", "extra_basics"):
        ultra_payment += c
    if policy == "extra_basics":
        ultra_payment += b
        computer_payment += b
    return u >= 1 and ultra_payment >= 2, c >= 1 and computer_payment >= 2


def state_flags(hand: tuple[int, ...], remainder: tuple[int, ...],
                prized_target: int, prized_gladion: int,
                policy: str) -> dict[str, bool]:
    """Compute legal immediate endpoint in a physical, fully specified world.

    A K0 policy can choose Computer first whenever payable, then Ultra if not:
    Computer Search can take the target or a deck Gladion based on its own search,
    so no advance knowledge of the target's Prize location is required.
    """
    ultra, computer = payment_options(hand, policy)
    target_hand = hand[0] == 1
    target_prized = prized_target == 1
    target_deck = remainder[0] - prized_target == 1
    gladion_hand = hand[1] >= 1
    gladion_deck = remainder[1] - prized_gladion >= 1
    direct = target_hand or (target_prized and gladion_hand) or (target_deck and ultra)
    static = direct or (target_deck and computer)
    computer_rescue = target_prized and not gladion_hand and computer and gladion_deck
    adaptive = static or computer_rescue
    return dict(zip(EVENTS, (
        target_hand, target_prized, ultra or computer, direct, static, adaptive,
        target_prized and adaptive, computer_rescue,
    )))


def raichu_target_payment_frontier(*, counts: tuple[int, ...] = DEFAULT,
                                   opening: int = 7, prizes: int = 6,
                                   active_policy: str = "preserve_giratina"
                                   ) -> dict[str, dict[str, Fraction]]:
    """Exact joint opening, Active-choice, hidden Prize and turn-draw law.

    Conditional on opener and turn draw, remaining unknown instances are
    exchangeable, so all unrelated Prize labels may be marginalized exactly.
    """
    if len(counts) != len(CATEGORIES) or any(type(x) is not int or x < 0 for x in counts):
        raise ValueError("expected eight nonnegative integer category counts")
    n = sum(counts)
    if (counts[0] != 1 or counts[4] != 1 or counts[5] < 1
            or opening < 1 or prizes < 0 or opening + prizes >= n):
        raise ValueError("invalid singleton, opening or Prize configuration")
    if active_policy not in ("preserve_giratina", "lead_giratina"):
        raise ValueError("unknown Active selection policy")
    accepted = _choose(n, opening) - _choose(n - counts[4] - counts[5], opening)
    if accepted == 0:
        raise ValueError("no valid opening")
    totals = {p: {e: Fraction() for e in EVENTS} for p in POLICIES}
    weight_sum = Fraction()
    ranges = (range(min(v, opening) + 1) for v in counts)
    for opener in product(*ranges):
        if sum(opener) != opening or opener[4] + opener[5] == 0:
            continue
        multiplier = 1
        for held, population in zip(opener, counts):
            multiplier *= _choose(population, held)
        opening_weight = Fraction(multiplier, accepted)
        active_g = bool(opener[4]) and (
            active_policy == "lead_giratina" or opener[5] == 0)
        active_index = 4 if active_g else 5
        after_open = tuple(pop - held for pop, held in zip(counts, opener))
        for drawn_index, available in enumerate(after_open):
            if not available:
                continue
            final_hand = list(opener)
            final_hand[active_index] -= 1
            final_hand[drawn_index] += 1
            final_hand = tuple(final_hand)
            remaining = list(after_open)
            remaining[drawn_index] -= 1
            remaining = tuple(remaining)
            unseen = sum(remaining)
            weight = opening_weight * Fraction(available, n - opening)
            prize_denominator = _choose(unseen, prizes)
            for t_prized in range(min(remaining[0], prizes) + 1):
                for l_prized in range(min(remaining[1], prizes - t_prized) + 1):
                    prize_ways = (_choose(remaining[0], t_prized)
                                  * _choose(remaining[1], l_prized)
                                  * _choose(unseen - remaining[0] - remaining[1],
                                            prizes - t_prized - l_prized))
                    if not prize_ways:
                        continue
                    state_weight = weight * Fraction(prize_ways, prize_denominator)
                    weight_sum += state_weight
                    for policy in POLICIES:
                        for event, success in state_flags(final_hand, remaining,
                                                          t_prized, l_prized,
                                                          policy).items():
                            if success:
                                totals[policy][event] += state_weight
    assert weight_sum == 1, weight_sum
    return totals


def brute_target_payment(*, counts: tuple[int, ...], opening: int, prizes: int,
                         active_policy: str) -> dict[str, dict[str, Fraction]]:
    """Independent identity-level exhaustive oracle, only for small decks."""
    labels = tuple(k for k, amount in enumerate(counts) for _ in range(amount))
    deck = set(range(len(labels)))
    totals = {p: {e: 0 for e in EVENTS} for p in POLICIES}
    worlds = 0
    for dealt in combinations(deck, opening):
        giratina = next((i for i in dealt if labels[i] == 4), None)
        other = next((i for i in dealt if labels[i] == 5), None)
        if giratina is None and other is None:
            continue
        active = (giratina if giratina is not None
                  and (active_policy == "lead_giratina" or other is None)
                  else other)
        hand = set(dealt) - {active}
        after_open = deck - set(dealt)
        for prize_ids in combinations(after_open, prizes):
            prize_set = set(prize_ids)
            for drawn in after_open - prize_set:
                current = hand | {drawn}
                rem = deck - set(dealt) - {drawn}
                histogram = tuple(sum(labels[i] == k for i in current)
                                  for k in range(len(CATEGORIES)))
                rest = tuple(sum(labels[i] == k for i in rem)
                             for k in range(len(CATEGORIES)))
                t_prized = sum(labels[i] == 0 for i in prize_set)
                l_prized = sum(labels[i] == 1 for i in prize_set)
                worlds += 1
                for p in POLICIES:
                    for e, yes in state_flags(histogram, rest, t_prized,
                                              l_prized, p).items():
                        totals[p][e] += yes
    return {p: {e: Fraction(v, worlds) for e, v in events.items()}
            for p, events in totals.items()}


if __name__ == "__main__":
    for name, row in raichu_target_payment_frontier().items():
        print(name, " ".join(f"{e}={float(row[e])*100:.9f}%"
                             for e in ("source_payable", "adaptive_access",
                                       "computer_prize_rescue")))
