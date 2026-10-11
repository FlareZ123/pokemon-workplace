"""Exact willingness-to-pay frontier for early Ultra Ball K1 information.

For each physically payable Basic-valid early-hand class s, let b_s be the
expected optimal late response utility after paid U+F+F information search
minus the utility without playing it, integrating over unknown future r,
reply draw and first Beheeyem tutor route. Paying exogenous cost tau is
optimal exactly when b_s > tau (strict tie means decline).

Thus the globally attainable improvement and source selection probability
are exactly:
  G(tau) = sum_{s: b_s>tau} mass_s*(b_s-tau)
  R(tau) = sum_{s: b_s>tau} mass_s

The breakpoints are only the finite, rational realized b_s values.
Between them G is affine with slope -R. Independent direct policy solver
is checked by regressions.
"""
from fractions import Fraction
from functools import lru_cache

from beheeyem_paid_k1_reward_prior import uncertain_reward_early_search


@lru_cache(maxsize=None)
def early_source_cost_frontier(
    prior:tuple[Fraction,Fraction,Fraction],
    lambda_weight:Fraction=Fraction(10),
    k_pre:int=2,k_reply:int=1
) -> dict:
    seed=uncertain_reward_early_search(
        prior,lambda_weight,Fraction(),k_pre,k_reply
    )
    source=seed["payable_source_benefit_distribution"]
    assert sum(weight for value,weight in source)==(
        seed["prelock_paid_search_available"]
    )
    assert all(value>=0 and weight>=0 for value,weight in source)
    assert all(source[i][0]<source[i+1][0] for i in range(len(source)-1))

    positive=[(value,weight) for value,weight in source if value>0]
    boundaries=[Fraction(0)]+[value for value,weight in positive]
    boundaries=sorted(set(boundaries))
    segments=[]
    for i,start in enumerate(boundaries):
        next_start=boundaries[i+1] if i+1<len(boundaries) else None
        probe=((start+next_start)/2 if next_start is not None
               else start+Fraction(1))
        active=tuple((value,weight) for value,weight in source if value>probe)
        if not active and next_start is not None:
            raise AssertionError("Inactive pre-final frontier interval")
        mass=sum((w for b,w in active),Fraction())
        gross=sum((b*w for b,w in active),Fraction())
        gain=gross-mass*probe
        assert gain>=0
        segments.append({
            "from_tau":start,
            "to_tau":next_start,
            "search_probability_on_interior":mass,
            "gross_source_utility_on_interior":gross,
            "net_gain_at_probe":gain,
            "probe_tau":probe
        })
    assert segments[0]["from_tau"]==0
    assert segments[-1]["search_probability_on_interior"]==0
    if len(segments)>1:
        assert segments[-1]["from_tau"]==max(b for b,w in positive)
    return {
        "total_physical_payable_mass":seed["prelock_paid_search_available"],
        "num_distinct_payable_benefits":len(source),
        "num_positive_benefits":len(positive),
        "max_positive_benefit":max((b for b,w in positive),default=Fraction()),
        "segments":tuple(segments),
        "gross_neutral_thinning":seed["unconditionally_paid_thinning_component"],
        "pure_k1_information":seed["unconditionally_paid_K1_component"]
    }


def evaluate_frontier(frontier:dict,tau:Fraction):
    if tau<0:
        raise ValueError("Source penalty cannot be negative")
    segment=next(x for x in frontier["segments"]
                 if x["from_tau"]<=tau and
                 (x["to_tau"] is None or tau<x["to_tau"]))
    # At an exact threshold ties choose "do not play"; segment to the right.
    return {
        "use_probability":segment["search_probability_on_interior"],
        "gain":(segment["gross_source_utility_on_interior"]-
                segment["search_probability_on_interior"]*tau)
    }
