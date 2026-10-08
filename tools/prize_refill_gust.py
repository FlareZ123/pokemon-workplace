"""Exact opening deal, hidden Prize recovery and Boss timing endgame.

Deck: 60 cards, with K Boss-like gusts and 60-K inert fillers. Opening hand:
7; Prizes: 6; draw pile: 47. We enumerate the joint hypergeometric deal.

Conditional on (hand, Prizes, deck) gust counts, the attacker is assumed to
have reached K1 knowledge by inspecting their deck before the first modeled
attack turn. An attacker turn draws one deck card, optionally spends at most
one Boss, and KOs one opposing Pokemon. KOs take 1/2/3 random Prize cards,
which may provide future Boss gusts. Opponent picks the next Active after KO.

The opponent may choose promotion with knowledge of public board and the
distribution of newly taken Prize cards, but by default does NOT see those
specific prize identities. Other older hand/deck information is treated as
known to the adversary, so the model is a conservative partial-information
abstraction rather than a full belief-state POMDP.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb
from typing import Iterator


def initial_partitions(
    boss_copies: int, deck_size: int = 60,
    opening_hand: int = 7, initial_prizes: int = 6,
) -> Iterator[tuple[int, int, int, Fraction]]:
    """Yield hand Boss, prized Boss, deck Boss, exact partition probability."""
    other_copies = deck_size - boss_copies
    for hand in range(max(0, opening_hand - other_copies), min(boss_copies, opening_hand) + 1):
        p_hand = Fraction(
            comb(boss_copies, hand) * comb(other_copies, opening_hand - hand),
            comb(deck_size, opening_hand)
        )
        prizes_after_hand = deck_size - opening_hand
        other_after_hand = other_copies - (opening_hand - hand)
        for prized in range(
            max(0, initial_prizes - other_after_hand),
            min(boss_copies - hand, initial_prizes) + 1,
        ):
            p_prized = Fraction(
                comb(boss_copies - hand, prized)
                * comb(other_after_hand, initial_prizes - prized),
                comb(prizes_after_hand, initial_prizes)
            )
            yield hand, prized, boss_copies - hand - prized, p_hand * p_prized


@lru_cache(None)
def expected_attacks(
    active: int,
    bench: tuple[int, ...],
    hand_boss: int,
    deck_boss: int,
    deck_fillers: int,
    prized_boss: int,
    prizes_left: int,
    recover_prize_cards: bool = True,
    opponent_sees_prize_identity: bool = False,
) -> Fraction:
    """Expected minimum attacks, before the current turn's natural draw."""
    n = deck_boss + deck_fillers
    if n == 0:
        raise ValueError("Insufficient deck cards for another required turn draw")
    expectation = Fraction(0)
    if deck_boss:
        expectation += Fraction(deck_boss, n) * _after_draw(
            active, bench, hand_boss + 1, deck_boss - 1, deck_fillers,
            prized_boss, prizes_left, recover_prize_cards, opponent_sees_prize_identity,
        )
    if deck_fillers:
        expectation += Fraction(deck_fillers, n) * _after_draw(
            active, bench, hand_boss, deck_boss, deck_fillers - 1,
            prized_boss, prizes_left, recover_prize_cards, opponent_sees_prize_identity,
        )
    return expectation


@lru_cache(None)
def _after_draw(
    active: int,
    bench: tuple[int, ...],
    hand_boss: int,
    deck_boss: int,
    deck_fillers: int,
    prized_boss: int,
    prizes_left: int,
    recover_prize_cards: bool,
    opponent_sees_prize_identity: bool,
) -> Fraction:
    if not bench:
        return Fraction(1)
    candidates = [(active, bench, hand_boss)]
    if hand_boss:
        for i, target in enumerate(bench):
            remainder = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
            candidates.append((target, remainder, hand_boss - 1))

    scores = []
    for reward, survivors, hand_after_supporter in candidates:
        if reward >= prizes_left or not survivors:
            scores.append(Fraction(1))
            continue

        prize_outcomes = []
        for hits in range(
            max(0, reward - (prizes_left - prized_boss)),
            min(prized_boss, reward) + 1,
        ):
            chance = Fraction(
                comb(prized_boss, hits)
                * comb(prizes_left - prized_boss, reward - hits),
                comb(prizes_left, reward)
            )
            next_hand = hand_after_supporter + (hits if recover_prize_cards else 0)
            possible_promotions = [
                expected_attacks(
                    promoted,
                    survivors[:j] + survivors[j + 1:],
                    next_hand, deck_boss, deck_fillers,
                    prized_boss - hits, prizes_left - reward,
                    recover_prize_cards, opponent_sees_prize_identity,
                )
                for j, promoted in enumerate(survivors)
            ]
            prize_outcomes.append((chance, possible_promotions))

        if opponent_sees_prize_identity:
            future = sum(
                chance * max(values) for chance, values in prize_outcomes
            )
        else:
            future = max(
                sum(chance * values[j] for chance, values in prize_outcomes)
                for j in range(len(survivors))
            )
        scores.append(1 + future)
    return min(scores)


def expected_opening_deal_attacks(
    boss_copies: int,
    active: int,
    bench: tuple[int, ...],
    recover_prize_cards: bool = True,
    opponent_sees_prize_identity: bool = False,
) -> Fraction:
    """Expectation across opening hand7, 6 Prizes, and 47-card draw-pile deal."""
    expected = Fraction(0)
    for hand, prized, deck_boss, chance in initial_partitions(boss_copies):
        expected += chance * expected_attacks(
            active, bench, hand, deck_boss, 47 - deck_boss,
            prized, 6, recover_prize_cards, opponent_sees_prize_identity,
        )
    return expected


def two_attack_boss_probability(
    boss_copies: int, recover_first_three_prizes: bool = True,
) -> Fraction:
    """Probability of two 3-Prize gust KOs in the 1/1,3,3 witness board.

    An initial 7-card hand plus the first natural draw expose 8 uniformly
    selected cards. Need >=1 Boss in those 8; if exactly one, the second must
    appear in next natural draw, or in one of 3 first-KO Prize cards if the
    latter are being recovered. This closed form is independent of the DP.
    """
    N, exposed = 60, 8
    looked_after_first_ko = 4 if recover_first_three_prizes else 1
    result = Fraction(0)
    for h in range(0, min(boss_copies, exposed) + 1):
        chance = Fraction(
            comb(boss_copies, h) * comb(N - boss_copies, exposed - h),
            comb(N, exposed)
        )
        if h >= 2:
            result += chance
        elif h == 1:
            no_second = Fraction(
                comb(N - exposed - (boss_copies - 1), looked_after_first_ko),
                comb(N - exposed, looked_after_first_ko)
            )
            result += chance * (1 - no_second)
    return result
