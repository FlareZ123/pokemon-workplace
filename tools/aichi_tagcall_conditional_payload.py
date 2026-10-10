"""Stratified Aichi Bellelba-first-search comparison at exact target counts.

Samples physical 60-card permutations conditional on:
Jirachi in opener; naturally visible G&H and Tag Call by turn draw;
Bellelba searchable; and exactly g=0 or g=1 G&H remain searchable.

The sample strata have exact combinatorial probabilities, so an average
within each stratum can be weighted back to accepted Basic-valid starts.
This is a fixed-seed, conditional Monte Carlo access estimate. Existing
Aichi endpoint and payment approximations remain intact.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from math import comb, sqrt
import random

from tools.aichi_post_gnh_prize_reset import DECK, protect_gnh_outputs
from tools.aichi_jirachi_ticket_search import (
    prepare_with_deferred_stellar, stellar_available,
)
from tools.aichi_jirachi_payment_frontier import prior_full_deck_search
from tools.aichi_tagcall_payment_reachability import additional_tag_call
from tools.aichi_tagcall_bellelba_payload import (
    GNH, BELLELBA, OBJECTIVES, PACKAGES_USED, PROTECTED_OUTPUTS,
    supplement_with_bellelba, endpoint_paths, chance,
)
from tools.aichi_repeated_ticket_access import PACKAGES
from tools.aichi_tagcall_target_availability import exact_tagcall_target_partition


def choose(n: int, k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


J = tuple(i for i,c in enumerate(DECK) if c=="Jirachi")
G = tuple(i for i,c in enumerate(DECK) if c==GNH)
T = tuple(i for i,c in enumerate(DECK) if c=="Tag Call")
B = tuple(i for i,c in enumerate(DECK) if c==BELLELBA)
O = tuple(i for i in range(len(DECK)) if i not in set(J+G+T+B))
assert len(J)==len(B)==1 and len(G)==len(T)==4 and len(O)==50


def category_weights(g_left: int) -> tuple[tuple[int,int,int], ...]:
    """Integer relative weights for visible G&H/Tag Call multiplicities."""
    if g_left not in (0,1):
        raise ValueError("this model studies the two material-benefit strata")
    results=[]
    for held_g in range(1,5):
        for held_t in range(1,5):
            prized_g=4-held_g-g_left
            n_other_visible=7-held_g-held_t
            w=(choose(4,held_g)*choose(4,held_t)*
               choose(50,n_other_visible)*
               choose(4-held_g,prized_g)*
               choose(47+held_g,6-prized_g))
            if w:
                results.append((held_g,held_t,w))
    return tuple(results)


def sample_conditioned_order(rng: random.Random, g_left: int) -> tuple[int,...]:
    """A truly physical uniformly random deal conditioned on a target stratum."""
    weights=category_weights(g_left)
    ticket=rng.randrange(sum(w for _,_,w in weights))
    held_g=held_t=0
    for k,t,w in weights:
        if ticket<w:
            held_g,held_t=k,t
            break
        ticket-=w
    assert held_g and held_t

    observed = (
        rng.sample(G,held_g) + rng.sample(T,held_t) +
        rng.sample(O,7-held_g-held_t)
    )
    rng.shuffle(observed)
    used=set(observed)
    unobserved_g=[i for i in G if i not in used]
    prize_g=rng.sample(unobserved_g,4-held_g-g_left)
    filler=[i for i in T+O if i not in used]
    prize_other=rng.sample(filler,6-len(prize_g))
    prizes=prize_g+prize_other
    rng.shuffle(prizes)

    opener=observed[:6]+[J[0]]
    rng.shuffle(opener)
    consumed=set(opener+prizes+[observed[6]])
    deck=[i for i in range(len(DECK)) if i not in consumed]
    rng.shuffle(deck)
    order=tuple(opener+prizes+[observed[6]]+deck)
    assert len(order)==60 and len(set(order))==60
    return order


@dataclass
class Stratum:
    g_left: int
    mass: Fraction
    samples: int
    eligible: int
    mean_gain: dict[tuple[str,str],float]
    mean_protected_gain: dict[tuple[str,str],float]
    mean_payment_premium: dict[tuple[str,str],float]
    variance_gain: dict[tuple[str,str],float]
    improved_counts: Counter[tuple[str,str]]
    material_only: Counter[tuple[str,str]]
    payment_helped: Counter[tuple[str,str]]
    first_payment_witness: tuple | None


@dataclass
class StratifiedResult:
    strata: tuple[Stratum,...]
    uplift: dict[tuple[str,str],float]
    protected_uplift: dict[tuple[str,str],float]
    payment_premium: dict[tuple[str,str],float]
    ci_halfwidth: dict[tuple[str,str],float]


def sample_stratified(*, zero_g_samples: int=1_000, one_g_samples: int=3_000,
                      seed: int=20261010) -> StratifiedResult:
    natural=exact_tagcall_target_partition()
    strata=[]
    for g_left,samples in ((0,zero_g_samples),(1,one_g_samples)):
        if samples<=0:
            raise ValueError("positive stratum sample count required")
        rng=random.Random(seed+g_left*1009)
        p=natural.count_probability(gnh_count=g_left,bellelba_count=1)
        gain=defaultdict(float)
        protected=defaultdict(float)
        payment=defaultdict(float)
        squares=defaultdict(float)
        improved=Counter()
        material_only=Counter()
        payment_helped=Counter()
        first_payment_witness=None
        eligible=0
        for trial_index in range(samples):
            order=sample_conditioned_order(rng,g_left)
            state,deferred=prepare_with_deferred_stellar(list(order))
            assert state is not None and state.gnh_access
            late=deferred or stellar_available(list(order),state.active)
            if not late or prior_full_deck_search(list(order),state.active,deferred):
                continue
            if protect_gnh_outputs(state) is None:
                continue
            eligible+=1
            named=supplement_with_bellelba(state)
            assert named is not None
            with_g=additional_tag_call(state)
            for objective in OBJECTIVES:
                original=endpoint_paths(state,objective,PROTECTED_OUTPUTS)
                g_only=endpoint_paths(with_g,objective,frozenset())
                g_plus_b=endpoint_paths(named,objective,frozenset())
                b_protected=endpoint_paths(named,objective,frozenset((BELLELBA,)))
                for package in PACKAGES_USED:
                    key=(objective,package)
                    assignment=PACKAGES[package]
                    old=max(chance(original,assignment,late),
                            chance(g_only,assignment,late))
                    upgraded=max(old,chance(g_plus_b,assignment,late))
                    guarded=max(old,chance(b_protected,assignment,late))
                    assert upgraded+1e-12>=guarded>=old-1e-12
                    delta=upgraded-old
                    safe=guarded-old
                    bonus=upgraded-guarded
                    if bonus>1e-12:
                        payment_helped[key]+=1
                        funding_paths=[
                            p for p in g_plus_b
                            if p.paid_with is not None
                            and BELLELBA in p.paid_with
                            and chance((p,),assignment,late)>guarded+1e-12
                        ]
                        assert funding_paths, (g_left,trial_index,key,bonus)
                        if first_payment_witness is None:
                            first_payment_witness=(
                                trial_index,key,tuple(order),
                                old,guarded,upgraded,
                                funding_paths[0].paid_with,
                            )
                    gain[key]+=delta
                    protected[key]+=safe
                    payment[key]+=bonus
                    squares[key]+=delta*delta
                    improved[key]+=int(delta>1e-12)
                    material_only[key]+=int(
                        bool(g_plus_b) and not bool(g_only)
                    )
        means={key:gain[key]/samples for key in gain}
        variance={key:max(0,squares[key]/samples-means[key]**2)
                  for key in gain}
        strata.append(Stratum(
            g_left=g_left,mass=p,samples=samples,eligible=eligible,
            mean_gain=means,
            mean_protected_gain={key:protected[key]/samples for key in gain},
            mean_payment_premium={key:payment[key]/samples for key in gain},
            variance_gain=variance,improved_counts=improved,
            material_only=material_only,payment_helped=payment_helped,
            first_payment_witness=first_payment_witness,
        ))
    keys=tuple((objective,package) for objective in OBJECTIVES
               for package in PACKAGES_USED)
    def mixture(field,key):
        return sum(float(s.mass)*getattr(s,field).get(key,0.0) for s in strata)
    return StratifiedResult(
        strata=tuple(strata),
        uplift={key:mixture("mean_gain",key) for key in keys},
        protected_uplift={key:mixture("mean_protected_gain",key) for key in keys},
        payment_premium={key:mixture("mean_payment_premium",key) for key in keys},
        ci_halfwidth={
            key:1.96*sqrt(sum(
                float(s.mass)**2*s.variance_gain.get(key,0.0)/s.samples
                for s in strata
            ))
            for key in keys
        },
    )


def report(result: StratifiedResult) -> str:
    lines=[]
    for s in result.strata:
        lines.append(
            f"stratum g={s.g_left}, Bellelba deck=1, "
            f"accepted mass={float(s.mass)*100:.12f}% "
            f"sampled={s.samples}, G&H core/late={s.eligible}, "
            f"Bellelba_payment_helped={dict(s.payment_helped)}"
        )
        if s.first_payment_witness is not None:
            lines.append(f"first physical Bellelba payment witness: {s.first_payment_witness}")
    lines.append(
        "objective | package | weighted uplift pp ± paired 95% halfCI | "
        "with Bellelba protected uplift pp | Bellelba discard premium pp"
    )
    for key in result.uplift:
        obj,pkg=key
        lines.append(
            f"{obj} | {pkg} | "
            f"{100*result.uplift[key]:+.9f} +/- "
            f"{100*result.ci_halfwidth[key]:.9f} | "
            f"{100*result.protected_uplift[key]:+.9f} | "
            f"{100*result.payment_premium[key]:+.9f}"
        )
    return "\n".join(lines)
