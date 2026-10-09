"""Fixed-slot optimal allocation with actual repeated Rotom and Pokédex effects."""
from fractions import Fraction

from tools.repeated_topfive_information import exact_opening
from tools.arc_peonia_slot_frontier import candidates as single_probe_candidates


def candidates(slots):
    """Max four of each distinct named card: Arc, Peonia, Rotom, Pokédex."""
    options=[]
    for arcs in range(1,5):
        for peonias in range(1,5):
            for rotoms in range(5):
                pokedex=slots-arcs-peonias-rotoms
                if not 0 <= pokedex <= 4:
                    continue
                probability=exact_opening(
                    starters=12,arcs=arcs,peonias=peonias,
                    rotoms=rotoms,pokedex=pokedex,
                    disposable=47-slots,total=60,opening=7,prizes=6,
                )
                options.append((probability,arcs,peonias,rotoms,pokedex))
    return sorted(options,reverse=True)


def run():
    # (K, A, P, Rotom, Pokédex, optimized exact probability)
    expected=(
        (2,1,1,0,0,Fraction(1594523,6526246584)),
        (3,2,1,0,0,Fraction(9106961,19578739752)),
        (4,2,2,0,0,Fraction(21180725,23929570808)),
        (5,3,2,0,0,Fraction(90706637,71788712424)),
        (6,3,3,0,0,Fraction(129423757,71788712424)),
        (7,3,3,1,0,Fraction(90498637,35894356212)),
        (8,3,3,2,0,Fraction(89284999,27611043240)),
        (9,4,3,2,0,Fraction(4433912941,1076830686360)),
        (10,4,4,2,0,Fraction(6348660059,1211434522155)),
        (11,4,4,3,0,Fraction(860675209,134603835795)),
        (12,4,4,4,0,Fraction(1232347544617,163543660490925)),
        (13,4,4,4,1,Fraction(257590655653,29735210998350)),
        (14,4,4,4,2,Fraction(26678650231,2753260277625)),
        (15,4,4,4,3,Fraction(789588110536,74338027495875)),
        (16,4,4,4,4,Fraction(9373429031237,817718302454625)),
    )
    for slots,a,p,r,d,prob in expected:
        options=candidates(slots)
        assert options[0]==(prob,a,p,r,d),(slots,options[0])
        assert all(value <= prob for value,*_ in options)
        single_probe_best=single_probe_candidates(slots)[0][0]
        assert prob >= single_probe_best
        print(f"K={slots:2d} A={a} P={p} R={r} D={d}: "
              f"{float(prob):.9%}; single-probe {float(single_probe_best):.9%}")

    # The first copy of Pokédex is optimal only once four Rotom are filled.
    assert all(candidates(k)[0][4]==0 for k in range(2,13))
    assert candidates(13)[0][4]==1
    # A policy model that merges names into a one-shot top-five class
    # changes which exact eight-slot deck allocation wins.
    assert candidates(8)[0][1:]==(3,3,2,0)
    assert single_probe_candidates(8)[0][1:]==(4,3,1)
    print("All 15 repeated-observation slot frontiers passed.")


if __name__ == "__main__":
    run()
