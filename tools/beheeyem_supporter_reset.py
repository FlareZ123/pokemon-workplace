"""Exact opposing Iono, N, or Marnie reset of Beheeyem recurring packet.

Condition on three mature-board Basics, six T2 residual hand cards, six
face-down Prizes, and first Beheeyem + TAE Mysterious Noise attack through
direct packet or a legal held one-copy paid tutor. Recycle attacker, base
Elgyem and TAE to 48-/47-card randomized deck, then award r=0..2 face-down
Prize cards from the original six as an exogenous KO outcome.

Opponent Supporter responses:
- Iono: shuffle current hand and BOTTOM it, then draw 6-r top-deck cards.
- Marnie: shuffle and BOTTOM our hand, draw 4 top-deck cards (opponent of
  the player who used Marnie).
- N: shuffle current hand INTO the deck, then draw 6-r cards from the
  newly shuffled entire physical deck.

All three are followed by d extra T3 top-deck draws. The exact next-packet
event accepts B+TAE directly, or one missing type searched by one physical
tutor with sufficient disposable neutral cards. No opponent tactical or
matchup policy is inferred from the Supporter comparison.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import second_draw_success


@lru_cache(maxsize=None)
def exact_supporter_reset(
    B: int, T: int, T3_draws: int, tutor: str,
    prizes_awarded: int, supporter: str
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Return first packet, direct-both, rescued-both, total two-packet rates."""
    if not (1 <= B <= 4 and 1 <= T <= 4):
        raise ValueError("Packet copy counts must be 1..4")
    if not (0 <= T3_draws <= 5 and 0 <= prizes_awarded <= 2):
        raise ValueError("T3 draws 0..5 and Prize awards 0..2")
    if tutor not in MODES or supporter not in ("N","Iono","Marnie"):
        raise ValueError("Unknown tutor or opposing hand-reset Supporter")

    target, payment = MODES[tutor]
    F = 56-B-T
    first = direct_both = rescued_both = Fraction()
    hp_space = comb(57,6)*comb(51,6)
    prize_draw_space = comb(6,prizes_awarded)

    for b in range(B+1):
        for t in range(T+1):
            for c in range(2):
                f = 6-b-t-c
                hand_ways = choose(B,b)*choose(T,t)*choose(1,c)*choose(F,f)
                if not hand_ways:
                    continue
                direct = b > 0 and t > 0
                missing_b, missing_t = b == 0, t == 0
                rescue = not direct and c and f >= payment and (
                    (missing_b and t > 0 and target in ("pokemon","either"))
                    or (missing_t and b > 0 and target in ("energy","either"))
                )
                if not (direct or rescue):
                    continue
                for pb in range(B-b+1):
                    for pt in range(T-t+1):
                        for pc in range(2-c):
                            pf = 6-pb-pt-pc
                            prize_ways = (choose(B-b,pb)*choose(T-t,pt)*
                                          choose(1-c,pc)*choose(F-f,pf))
                            if not prize_ways:
                                continue
                            if rescue and (
                                (missing_b and B-b-pb == 0) or
                                (missing_t and T-t-pt == 0)
                            ):
                                continue
                            weight = Fraction(hand_ways*prize_ways,hp_space)
                            first += weight
                            if direct:
                                hand = (b-1,t-1,c,f)
                                deck = (B-b-pb+1,T-t-pt+1,1-c-pc,F-f-pf+1)
                                assert sum(deck) == 48
                            else:
                                hand = (max(b-1,0),max(t-1,0),0,f-payment)
                                deck = (
                                    B-b-pb+1-int(missing_b),
                                    T-t-pt+1-int(missing_t),
                                    0,F-f-pf+1
                                )
                                assert sum(deck) == 47

                            if supporter == "Iono":
                                probability = second_draw_success(
                                    0,0,0,0,*deck,6-prizes_awarded+T3_draws,tutor
                                )
                            elif supporter == "Marnie":
                                probability = second_draw_success(
                                    0,0,0,0,*deck,4+T3_draws,tutor
                                )
                            else:
                                probability = Fraction()
                                # N shuffles the awarded Prizes AND every
                                # remaining held card into the full deck.
                                for xb in range(min(pb,prizes_awarded)+1):
                                    for xt in range(min(pt,prizes_awarded-xb)+1):
                                        for xc in range(min(pc,prizes_awarded-xb-xt)+1):
                                            xf = prizes_awarded-xb-xt-xc
                                            ways = (choose(pb,xb)*choose(pt,xt)*
                                                    choose(pc,xc)*choose(pf,xf))
                                            if not ways:
                                                continue
                                            joined = tuple(
                                                x+y+z for x,y,z in zip(
                                                    deck,hand,(xb,xt,xc,xf)
                                                )
                                            )
                                            probability += Fraction(
                                                ways,prize_draw_space
                                            ) * second_draw_success(
                                                0,0,0,0,*joined,
                                                6-prizes_awarded+T3_draws,tutor
                                            )
                            if direct:
                                direct_both += weight*probability
                            else:
                                rescued_both += weight*probability
    return first,direct_both,rescued_both,direct_both+rescued_both
