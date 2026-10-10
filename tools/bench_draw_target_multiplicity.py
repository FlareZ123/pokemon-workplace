"""Exact multicopy target value and Bench debt under staged support draws.

No-effect cost model. A target set of k labeled copies is uniformly sampled
from N unseen positions partitioned into r earlier natural draws, p Prizes,
and n live deck cards. The opening hand retains Crobat and Dedenne; a card
of interest was absent from the opening seven. Goal: at least one copy in hand.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class Multiplicity:
    copies: int
    dedenne_success: Fraction
    staged_success: Fraction
    extra_access: Fraction
    dedenne_bench_k0: Fraction
    staged_bench_k0: Fraction
    dedenne_bench_k1: Fraction
    staged_bench_k1: Fraction
    all_prized: Fraction

    @property
    def extra_bench_k0(self) -> Fraction:
        return self.staged_bench_k0 - self.dedenne_bench_k0

    @property
    def extra_bench_k1(self) -> Fraction:
        return self.staged_bench_k1 - self.dedenne_bench_k1


def analyze(*, copies: int = 1, hand_size: int = 5,
            natural_draws: int = 1, prizes: int = 6,
            deck_cards: int = 46) -> Multiplicity:
    """Closed-form exact access and occupancy for K0 and K1 stop policies.

    K1 stops immediately on learning that every target copy is Prized.
    That is a paired-state information ablation; the cost of obtaining K1
    and any other utility of draw Abilities are deliberately omitted.
    """
    n = natural_draws + prizes + deck_cards
    a = max(0, 7 - hand_size)
    if not 1 <= copies <= n or min(natural_draws, prizes, deck_cards) < 0:
        raise ValueError("invalid card-count inputs")
    if hand_size < 2 + int(natural_draws > 0):
        raise ValueError("hand must hold both supports and any earlier target")
    if deck_cards < a + 6:
        raise ValueError("requires enough deck cards for the two draw stages")

    denominator = comb(n, copies)

    def none_seen(sampled: int) -> Fraction:
        return Fraction(comb(n - sampled, copies)
                        if copies <= n - sampled else 0, denominator)

    all_prized = Fraction(comb(prizes, copies)
                          if copies <= prizes else 0, denominator)
    no_early = none_seen(natural_draws)
    no_crobat = none_seen(natural_draws + a)
    dedenne_hit = 1 - none_seen(natural_draws + 6)
    stage_hit = 1 - none_seen(natural_draws + a + 6)
    return Multiplicity(
        copies=copies,
        dedenne_success=dedenne_hit,
        staged_success=stage_hit,
        extra_access=stage_hit - dedenne_hit,
        dedenne_bench_k0=no_early,
        staged_bench_k0=no_early + no_crobat,
        dedenne_bench_k1=no_early - all_prized,
        staged_bench_k1=no_early + no_crobat - 2 * all_prized,
        all_prized=all_prized,
    )


if __name__ == "__main__":
    for k in range(1, 7):
        x = analyze(copies=k)
        print(f"{k}: Dede={float(x.dedenne_success):.6%} "
              f"staged={float(x.staged_success):.6%} "
              f"gain={float(x.extra_access):.6%} "
              f"extra K0 Bench={float(x.extra_bench_k0):.6f} "
              f"all Prized={float(x.all_prized):.8%}")
