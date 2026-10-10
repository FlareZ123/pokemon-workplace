"""Exact optional Energy+Tool hand-reduction enablement for QB-Crobat staging.

Seven-card opener contains Dedenne, QB, a disposable F, and a distinct O Basic
chosen Active; singleton target K and Crobat C are absent. One later draw may
supply a Basic Energy E or attachable Tool T, but both must be on-hand after
that draw to lower hand seven -> five before paying QB. Both C and K must
remain live after the six face-down Prize cards and later draw for the
single-target policy difference to be possible.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class EnergyToolAccess:
    valid_open: Fraction
    enabling_k_live_given_valid: Fraction
    bootstrapped_access_gain_given_valid: Fraction
    conditional_k_live_gain: Fraction


def analyze(*, deck_size: int = 60, opening_size: int = 7,
            prize_count: int = 6, other_basics: int = 4,
            quick_balls: int = 4, discardable: int = 4,
            energies: int = 4, tools: int = 4) -> EnergyToolAccess:
    if min(deck_size, opening_size, prize_count, other_basics, quick_balls,
           discardable, energies, tools) < 0:
        raise ValueError("negative deck class")
    filler = deck_size - (3 + other_basics + quick_balls
                          + discardable + energies + tools)
    if filler < 0 or deck_size - opening_size - 1 < prize_count:
        raise ValueError("invalid deck size")
    if opening_size < 4:
        raise ValueError("opening cannot contain required D/Q/F/O roles")
    # Choose one O Active, draw once, then attach one E and one T from hand.
    h = opening_size - 2
    a = max(0, 8 - h)
    live_after_setup = deck_size - opening_size - prize_count - 1
    if live_after_setup - 1 < a + 6:
        raise ValueError("not enough live deck cards for two support draws")

    accepted_basic = 2 + other_basics
    valid = Fraction(choose(deck_size, opening_size)
                     - choose(deck_size - accepted_basic, opening_size),
                     choose(deck_size, opening_size))
    remaining_before_draw = deck_size - opening_size
    remaining_after_draw = remaining_before_draw - 1
    double_live_probability = Fraction(
        choose(remaining_after_draw-2, prize_count),
        choose(remaining_after_draw, prize_count))

    eligible_open_draw_ways = 0
    for q in range(1, quick_balls+1):
        for f in range(1, discardable+1):
            for o in range(1, other_basics+1):
                for e in range(energies+1):
                    for t in range(tools+1):
                        remaining_filler = opening_size - 1-q-f-o-e-t
                        ways = (choose(quick_balls,q)*choose(discardable,f)
                                *choose(other_basics,o)*choose(energies,e)
                                *choose(tools,t)*choose(filler,remaining_filler))
                        if e and t:
                            valid_draw_choices = remaining_before_draw-2
                        elif e:
                            valid_draw_choices = tools-t
                        elif t:
                            valid_draw_choices = energies-e
                        else:
                            valid_draw_choices = 0
                        eligible_open_draw_ways += ways*valid_draw_choices

    no_prize_or_draw_violations = Fraction(
        eligible_open_draw_ways,
        choose(deck_size,opening_size)*remaining_before_draw)
    eligible = no_prize_or_draw_violations * double_live_probability / valid
    conditional_delta = Fraction(a+6,live_after_setup-1) - Fraction(6,live_after_setup)
    return EnergyToolAccess(valid,eligible,eligible*conditional_delta,conditional_delta)


if __name__ == "__main__":
    x=analyze()
    print("Valid opening:",float(x.valid_open)*100,"%")
    print("Energy+Tool setup; C/K live | valid opener:",
          float(x.enabling_k_live_given_valid)*100,"%")
    print("Stage delta conditioned on K and C live:",
          float(x.conditional_k_live_gain)*100,"%")
    print("Material-weighted executable gain:",
          float(x.bootstrapped_access_gain_given_valid)*100,"percentage points")
