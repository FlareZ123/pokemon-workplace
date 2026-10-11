"""Exact Basic-valid physical Supporter menu and K0/K1 Prize-information value.

The constructed deck uses disjoint card classes B, I, N, R, T, F:
Basic starters, Iono, N, Professor's Research, target outs, filler.
This is a conditional one-step card-access model, not a match simulator.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from hand_return_payment_frontier import hit_probability
from multi_action_information_envelope import action_information_envelope

CLASSES = ("B", "I", "N", "R", "T", "F")


@dataclass(frozen=True)
class MenuResult:
    accepted_opening: Fraction
    hand_distribution: tuple[tuple[tuple[int, ...], Fraction], ...]
    k1_information_gain: Fraction
    fixed_policy_value: Fraction
    observed_policy_value: Fraction
    any_supporter: Fraction
    multiple_supporter: Fraction
    target_held: Fraction
    contribution_by_hand: tuple[tuple[tuple[int, ...], Fraction], ...]


def opening_hand_distribution(
    counts: tuple[int, ...], *, opening_size: int = 7, prize_count: int = 6,
) -> tuple[Fraction, dict[tuple[int, ...], Fraction]]:
    """Exactly condition on valid Basic opening and draw once after prizes.

    Opening of length opening_size, at least one Basic. Pick exactly one
    Basic as Active and leave other Basics in hand. Set prize_count random
    Prizes from the unseen remainder, then draw one natural turn card. No
    opponent mulligan-draw bonus, Bench action or other draw is included.
    The distribution over the drawn category marginalizes the intervening
    unknown Prizes by exchangeability.
    """
    if (len(counts) != 6 or any(type(n) is not int or n<0 for n in counts)
            or type(opening_size) is not int or type(prize_count) is not int):
        raise ValueError("six nonnegative integer category counts required")
    total = sum(counts)
    if not 0 < opening_size < total-prize_count or counts[0] < 1:
        raise ValueError("opening/Prize/Basic configuration invalid")
    denominator=comb(total,opening_size)
    accepted=Fraction(denominator-comb(total-counts[0],opening_size),denominator)
    hands:dict[tuple[int,...],Fraction]={}
    ranges=[range(min(n,opening_size)+1) for n in counts]
    for opening in product(*ranges):
        if opening[0]<1 or sum(opening)!=opening_size:
            continue
        prior=Fraction(1,denominator)
        for n,c in zip(counts,opening):
            prior*=comb(n,c)
        for draw_class in range(6):
            remaining=counts[draw_class]-opening[draw_class]
            if remaining==0:
                continue
            hand=list(opening)
            hand[0]-=1
            hand[draw_class]+=1
            key=tuple(hand)
            p=prior*Fraction(remaining,total-opening_size)/accepted
            hands[key]=hands.get(key,Fraction())+p
    assert sum(hands.values(),Fraction())==1
    return accepted,hands


def k_prior(*,deck_size:int, prize_count:int, unknown_outs:int
           ) -> tuple[tuple[int,Fraction],...]:
    """Deck-outs uncertainty after observed final hand but before deck search."""
    total=deck_size+prize_count
    assert 0<=unknown_outs<=total
    denominator=comb(total,unknown_outs)
    return tuple((k,Fraction(comb(deck_size,k)*comb(prize_count,unknown_outs-k),
                             denominator))
                 for k in range(max(0,unknown_outs-prize_count),
                                min(deck_size,unknown_outs)+1))


def physical_supporter_information(
    counts: tuple[int,...] = (12,4,4,4,4,32),
    *, opening_size:int=7, prize_count:int=6,
    opponent_penalties: tuple[Fraction,...],
    weight:Fraction,
) -> MenuResult:
    """Observe own hand; Supporter actions require a physical card in it.

    K0 and K1 both condition on the observed seven-card hand. K1 also learns
    the actual number of own useful outs remaining in the deck. 'Pass' is
    always legal. Opponent penalties are already averaged over their hidden
    Prizes, and hence reveal no opponent hidden state.
    """
    if len(opponent_penalties)!=4 or any(p<0 or p>1 for p in opponent_penalties):
        raise ValueError("expected four opponent target access probabilities")
    weight=Fraction(weight)
    if weight<0:
        raise ValueError("weight must be nonnegative")
    accepted,hands=opening_hand_distribution(counts,
        opening_size=opening_size,prize_count=prize_count)
    deck_size=sum(counts)-opening_size-prize_count-1
    if deck_size<=0:
        raise ValueError("no deck left after opening, prizes and turn draw")
    # The old hand has opening_size cards after the mandatory Active and
    # natural draw, before one Supporter card gets removed for play.
    fixed=observed=Fraction()
    supporter_mass=multiple_mass=target_mass=Fraction()
    per_hand=[]
    names=("Iono","N","Professor's Research","Pass")
    q=tuple(Fraction(x) for x in opponent_penalties)
    for hand,mass in sorted(hands.items()):
        b,i,n,r,t,f=hand
        available=[name for idx,name in enumerate(names[:3]) if hand[idx+1]]
        available.append("Pass")
        supporter_copies=i+n+r
        supporter_mass+=mass*bool(supporter_copies)
        multiple_mass+=mass*(supporter_copies>=2)
        target_mass+=mass*bool(t)
        unknown_outs=counts[4]-t
        rows=[]
        for k,p in k_prior(deck_size=deck_size,prize_count=prize_count,
                           unknown_outs=unknown_outs):
            own=(hit_probability(deck_size,k,prize_count),
                 hit_probability(deck_size+opening_size-1,k+t,prize_count),
                 hit_probability(deck_size,k,7),Fraction(int(t>0)))
            rows.append((p,{name:own[idx]-weight*q[idx]
                            for idx,name in enumerate(names) if name in available}))
        envelope=action_information_envelope(rows)
        fixed+=mass*envelope.best_fixed_value
        observed+=mass*envelope.observed_value
        per_hand.append((hand,mass*envelope.information_value))
    return MenuResult(accepted,tuple(sorted(hands.items())),observed-fixed,
                      fixed,observed,supporter_mass,multiple_mass,target_mass,
                      tuple(per_hand))
