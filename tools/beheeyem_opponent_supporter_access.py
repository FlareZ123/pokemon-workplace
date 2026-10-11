"""Physical opposing-Supporter reachability and conditional Beheeyem response.

Opposing deck: 60 cards with disjoint Basic, Ace Trainer, Judge and filler
categories. Condition a seven-card opening hand on containing a Basic.
Set six uniformly random Prizes; subsequently draw k cards from the deck
and earn s random original Prizes. Held named Supporters are not spent.
Uniformity makes the union of k deck draws and s Prize awards an unlabelled
(k+s)-subset of the 53 cards outside the opening hand.

Beheeyem's side is independent and uses the prior exact first/second-packet
models. Compare a supporter-access-aware policy with or without observing
whether Beheeyem publicly used its tutor on the first attack.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import exact_prize_take
from beheeyem_supporter_reset import exact_supporter_reset


@lru_cache(maxsize=None)
def probability_not_seen(
    basic_count: int, named_count: int, deck_draws: int, prizes_earned: int,
    deck_size: int = 60, opener: int = 7, starting_prizes: int = 6
) -> Fraction:
    """Exact probability a non-Basic named category has not reached hand.

    Condition on a valid initial Basic opener. Named Supporters and Basic
    Pokemon are disjoint. A uniformly earned Prize becomes a held card.
    Draws occur after six Prizes are laid down; for category presence the
    union of draws and Prize awards is a uniform remaining-card subset.
    """
    if not (0 <= basic_count <= deck_size
            and 0 <= named_count <= deck_size-basic_count):
        raise ValueError("Invalid disjoint category counts")
    if not (1 <= opener <= deck_size-starting_prizes
            and 0 <= prizes_earned <= starting_prizes
            and 0 <= deck_draws <= deck_size-opener-starting_prizes):
        raise ValueError("Invalid opening, Prize, or draw counts")
    extra = deck_draws + prizes_earned
    total_valid = choose(deck_size,opener)-choose(deck_size-basic_count,opener)
    if not total_valid:
        raise ValueError("An opening Basic is impossible")

    valid_no_named = (
        choose(deck_size-named_count,opener)
        - choose(deck_size-named_count-basic_count,opener)
    )
    return Fraction(
        valid_no_named * choose(deck_size-opener-named_count,extra),
        total_valid * choose(deck_size-opener,extra)
    )


@lru_cache(maxsize=None)
def opponent_supporter_access(
    basic_count: int, ace_count: int, judge_count: int,
    deck_draws: int, prizes_earned: int
) -> dict[str,Fraction]:
    """Joint physical chances of seeing each non-Basic Supporter class."""
    if not (0 <= ace_count <= 4 and 0 <= judge_count <= 4
            and basic_count+ace_count+judge_count <= 60):
        raise ValueError("Unsupported deck composition or copy count")
    none_a = probability_not_seen(basic_count,ace_count,deck_draws,prizes_earned)
    none_j = probability_not_seen(basic_count,judge_count,deck_draws,prizes_earned)
    none_both = probability_not_seen(
        basic_count,ace_count+judge_count,deck_draws,prizes_earned
    )
    p = {
        "neither": none_both,
        "ace_only": none_j-none_both,
        "judge_only": none_a-none_both,
        "both": 1-none_a-none_j+none_both
    }
    assert all(v>=0 for v in p.values()) and sum(p.values())==1
    return p


@lru_cache(maxsize=None)
def optimal_reply_with_access(
    B: int,T: int,d: int,tutor: str,r: int,
    opponent_prizes_left: int,opponent_basics: int,
    ace_count: int,judge_count: int,opponent_deck_draws: int
) -> dict[str,Fraction]:
    """Return event masses under aggregate-only and public-tutor-use policies.

    The opponent has 6-r Beheeyem Prize cards to compare against its own
    remaining Prize count. When Ace Trainer is legal, its owner draws 6
    and Beheeyem draws 3. Judge gives Beheeyem 4. At most one Supporter
    can be played; preserving the hand is always an available choice.

    Aggregate policy sees only the prior distribution of direct vs tutor-
    rescued first attacks; public-route policy sees which route occurred.
    Neither policy observes hidden exact hand/Prize card identities.
    """
    if not (1 <= B <= 4 and 1 <= T <= 4 and tutor in MODES
            and 0 <= d <= 5 and 0 <= r <= 2):
        raise ValueError("Invalid Beheeyem packet configuration")
    if not 0 <= opponent_prizes_left <= 6:
        raise ValueError("Opponent Prize count must be 0..6")
    earned = 6-opponent_prizes_left
    access = opponent_supporter_access(
        opponent_basics,ace_count,judge_count,opponent_deck_draws,earned
    )
    intact = exact_prize_take(B,T,d,tutor,r)
    judge = exact_supporter_reset(B,T,d,tutor,r,"Judge")
    ace_legal = opponent_prizes_left > 6-r
    ace = (exact_supporter_reset(B,T,d,tutor,r,"Ace Trainer")
           if ace_legal else None)
    assert intact[0] == judge[0] == (ace[0] if ace else intact[0])

    total = public_route = Fraction()
    for visibility,weight in access.items():
        candidates = [intact]
        if visibility in ("judge_only","both"):
            candidates.append(judge)
        if ace is not None and visibility in ("ace_only","both"):
            candidates.append(ace)
        total += weight * min(v[3] for v in candidates)
        public_route += weight * sum(min(v[j] for v in candidates) for j in (1,2))

    assert public_route <= total <= intact[3]
    return {
        "chance_seen_ace":access["ace_only"]+access["both"],
        "chance_seen_judge":access["judge_only"]+access["both"],
        "no_hand_reset_joint":intact[3],
        "optimal_aggregate_joint":total,
        "optimal_public_tutor_signal_joint":public_route,
        "signal_value":total-public_route
    }
