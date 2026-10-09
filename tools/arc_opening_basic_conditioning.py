"""Exact accepted-opening Basic conditioning for Prize rescue access."""
from dataclasses import dataclass
from fractions import Fraction
from math import comb

from tools.arc_phone_chain_access import _state_value


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class OpeningResult:
    acceptance: Fraction
    access_given_accepted: Fraction


def exact_accepted(*, other=(1, 4, 4, 8, 42), prize_count=6,
                   opening_size=7, chained=True):
    """Target is Prized; remaining counts are Peonia, Arc, Shoes, Basic, filler.

    One Basic in an accepted opening goes Active and is unusable as payment.
    Other Basics are treated as expendable filler for this narrow objective.
    """
    p, a, s, b, f = other
    size = sum(other) + 1
    if b < 1 or min(other) < 0 or prize_count < 1 or opening_size < 1 or prize_count + opening_size > size:
        raise ValueError("invalid deck size or Basic count")
    nprize = prize_count - 1
    den = comb(size - 1, nprize) * comb(size - prize_count, opening_size)
    accepted = Fraction()
    retrieved = Fraction()
    for pp in range(min(p, nprize) + 1):
     for pa in range(min(a, nprize - pp) + 1):
      for ps in range(min(s, nprize - pp - pa) + 1):
       for pb in range(min(b, nprize - pp - pa - ps) + 1):
        pf = nprize - pp - pa - ps - pb
        wp = choose(p,pp)*choose(a,pa)*choose(s,ps)*choose(b,pb)*choose(f,pf)
        if wp == 0:
            continue
        r = (p-pp, a-pa, s-ps, b-pb, f-pf)
        for hp in range(min(r[0], opening_size) + 1):
         for ha in range(min(r[1], opening_size-hp) + 1):
          for hs in range(min(r[2], opening_size-hp-ha) + 1):
           for hb in range(1, min(r[3], opening_size-hp-ha-hs) + 1):
            hf = opening_size-hp-ha-hs-hb
            wh = choose(r[0],hp)*choose(r[1],ha)*choose(r[2],hs)*choose(r[3],hb)*choose(r[4],hf)
            if wh == 0:
                continue
            weight = Fraction(wp*wh, den)
            accepted += weight
            prizes = (1,pp,pa,ps,pb+pf)
            hand = (0,hp,ha,hs,hb+hf-1)
            retrieved += weight*_state_value(prizes,hand,chained,min(3,prize_count),True)
    closed = 1-Fraction(choose(size-1-b,opening_size),choose(size-1,opening_size))
    assert accepted == closed
    return OpeningResult(accepted,retrieved/accepted)
