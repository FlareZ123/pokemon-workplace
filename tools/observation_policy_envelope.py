"""Exact observation-consistent deterministic policy envelope for finite states.

Every action in the common action menu must be legally attemptable from the
available public state. Latent failure outcomes belong in the state payoffs.
This prevents hidden-state hindsight leakage into a purported K0 policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable


@dataclass(frozen=True)
class BeliefState:
    state_id: str
    probability: Fraction
    observation: str
    # same ordered common action menu in every state; payoffs may be negative.
    payoffs: tuple[tuple[str, Fraction], ...]


@dataclass(frozen=True)
class PolicyEnvelope:
    expected_payoff: Fraction
    chosen_by_observation: tuple[tuple[str, str], ...]


def observation_policy_envelope(states: Iterable[BeliefState]) -> PolicyEnvelope:
    rows=tuple(states)
    if not rows or any(row.probability<0 for row in rows):
        raise ValueError("nonempty distribution with nonnegative mass required")
    if sum((row.probability for row in rows),Fraction(0))!=1:
        raise ValueError("prior masses must sum to one")
    if len({row.state_id for row in rows})!=len(rows):
        raise ValueError("state identifiers must be unique")
    actions=tuple(name for name,v in rows[0].payoffs)
    if not actions or len(set(actions))!=len(actions):
        raise ValueError("common nonempty action menu required")
    if any(tuple(name for name,v in row.payoffs)!=actions for row in rows):
        raise ValueError("all states must use identical observable action menu/order")
    if any(not row.observation for row in rows):
        raise ValueError("observation labels must be nonempty")
    groups={}
    for row in rows:
        outcomes=groups.setdefault(row.observation,[Fraction(0)]*len(actions))
        for i,(_,v) in enumerate(row.payoffs):
            outcomes[i]+=row.probability*Fraction(v)
    choices=[]
    total=Fraction(0)
    for label,values in sorted(groups.items()):
        idx=max(range(len(values)),key=lambda i:values[i])
        total+=values[idx]
        choices.append((label,actions[idx]))
    return PolicyEnvelope(total,tuple(choices))
