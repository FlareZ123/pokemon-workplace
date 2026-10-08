"""Exact event-family geometry for pre-observation resource commitments.

A fixed initial action (e.g. a three-card payment) creates a success
event over hidden worlds. Optimizing the action before and after
observation gives a gap determined by event overlap and dominance.

This is a generic finite, binary-objective evaluator. Every world has
a positive integer multiplicity; each initial action has a boolean
success vector over the same ordered worlds.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Hashable, Mapping, Sequence


@dataclass(frozen=True)
class PolicyGeometry:
    uninformed_success: Fraction
    clairvoyant_success: Fraction
    best_actions: tuple[Hashable,...]
    nondominated_actions: tuple[Hashable,...]
    minimum_union_cover: int
    action_count: int
    world_count: int

    @property
    def information_gap(self) -> Fraction:
        return self.clairvoyant_success-self.uninformed_success


def evaluate_binary_policy_events(
    world_weights: Sequence[int],
    action_success: Mapping[Hashable,Sequence[bool]],
) -> PolicyGeometry:
    """Compute exact K0/K1 and minimum event-cover size.

    Actions are **commitments made before** the hidden world is
    observed. After action selection, each boolean reports success
    following an optimal world-informed continuation.

    For a finite world set, K0=max_a P(E_a), K1=P(union_a E_a).
    The minimum cover is the fewest distinct action events needed to
    equal the union; equivalent event masks are deduplicated.
    """
    weights=tuple(world_weights)
    if not weights or any(not isinstance(w,int) or w<=0 for w in weights):
        raise ValueError("world weights must be positive integers")
    if not action_success:
        raise ValueError("at least one admissible initial action required")

    # Bit masks are more concise and cheaper than storing sets of world IDs.
    entries=[]
    for action,values in action_success.items():
        flags=tuple(values)
        if len(flags)!=len(weights):
            raise ValueError("action outcome length mismatch")
        if any(type(v) is not bool for v in flags):
            raise ValueError("binary policy requires boolean outcomes")
        bits=sum((1<<j) for j,ok in enumerate(flags) if ok)
        mass=sum(w for w,ok in zip(weights,flags) if ok)
        entries.append((action,bits,mass))

    denom=sum(weights)
    best_mass=max(item[2] for item in entries)
    best=tuple(a for a,mask,mass in entries if mass==best_mass)
    all_mask=0
    for _,bits,_ in entries:
        all_mask|=bits
    union_mass=sum(w for i,w in enumerate(weights) if all_mask & (1<<i))

    nondominated=[]
    seen_bits=set()
    for action,bits,mass in entries:
        if bits in seen_bits:
            continue
        seen_bits.add(bits)
        if any(bits != other and bits & other == bits
               for _,other,_ in entries):
            continue
        nondominated.append((action,bits))
    non_actions=tuple(a for a,_ in nondominated)
    masks=tuple(bits for _,bits in nondominated)

    if all_mask==0:
        min_cover=0
    else:
        min_cover=len(masks)
        for k in range(1,len(masks)+1):
            if any(
                _combine(select)==all_mask
                for select in combinations(masks,k)
            ):
                min_cover=k
                break

    return PolicyGeometry(
        uninformed_success=Fraction(best_mass,denom),
        clairvoyant_success=Fraction(union_mass,denom),
        best_actions=best,
        nondominated_actions=non_actions,
        minimum_union_cover=min_cover,
        action_count=len(entries),
        world_count=len(weights),
    )


def _combine(bitmasks: tuple[int,...]) -> int:
    combined=0
    for bits in bitmasks:
        combined|=bits
    return combined
