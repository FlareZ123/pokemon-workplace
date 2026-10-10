"""Exact Quick Ball -> Crobat V -> conditional Dedenne-GX target retention.

Crobat V is guaranteed in the live deck, Quick Ball / Dedenne-GX / one
expendable payment card are retained in hand, and a non-Basic singleton K
is absent from the opening seven. K is among the other unseen positions.

This bounded 60-card thought experiment prices search *physical payment*
and pool thinning but not broader action opportunity costs or match utility.
"""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QBComparison:
    hand_size: int
    crobat_draw: int
    dedenne_success: Fraction
    qb_staged_success: Fraction
    qb_staged_k0_bench: Fraction
    qb_staged_k1_bench: Fraction
    dedenne_bench: Fraction
    qb_uses: Fraction
    qb_staged_k1_dedenne: Fraction

    @property
    def access_gain(self) -> Fraction:
        return self.qb_staged_success - self.dedenne_success


def analyze(*, hand_size: int = 5, prize_count: int = 6,
            natural_draws: int = 1, other_live_cards: int = 45) -> QBComparison:
    """Expected exact final-hand singleton K and persistent Bench occupants.

    Normal draw occurs before the comparison. Crobat is guaranteed live and
    removed by QB's deck search. K is uniform among the r+p+n other unseen
    positions. The Dedenne-only branch sees the n+1 live deck incl. Crobat;
    the QB-staged branch searches Crobat, pays F, and draws from n cards.
    """
    r, p, n = natural_draws, prize_count, other_live_cards
    N = r + p + n
    if hand_size < 3 + int(r > 0) or min(r, p, n) < 0 or not N:
        raise ValueError("invalid hand or deck counts")
    a = max(0, 8 - hand_size)
    if n < a + 6:
        raise ValueError("live deck cannot furnish staged draw sequence")

    # Early seen K is retained without drawing; K otherwise may be Prized.
    dedenne_success = Fraction(r, N) + Fraction(n * 6, N * (n + 1))
    stage_success = Fraction(r + a + 6, N)
    no_early = Fraction(N - r, N)
    stage_k0 = no_early + Fraction(N - r - a, N)
    stage_k1 = Fraction(n, N) + Fraction(n - a, N)
    return QBComparison(
        hand_size=hand_size,
        crobat_draw=a,
        dedenne_success=dedenne_success,
        qb_staged_success=stage_success,
        qb_staged_k0_bench=stage_k0,
        qb_staged_k1_bench=stage_k1,
        dedenne_bench=no_early,
        qb_uses=no_early,
        qb_staged_k1_dedenne=Fraction(n - a, N),
    )


if __name__ == "__main__":
    for h in (4, 5, 6, 7, 8):
        x = analyze(hand_size=h)
        print(f"h={h} crobat-draw={x.crobat_draw} "
              f"Dede={float(x.dedenne_success):.6%} "
              f"QB-staged={float(x.qb_staged_success):.6%} "
              f"extra K1 Bench={float(x.qb_staged_k1_bench-x.dedenne_bench):.6f}")
