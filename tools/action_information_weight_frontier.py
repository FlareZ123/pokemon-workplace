"""Exact rational finite-action reward-minus-weighted-cost frontiers."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Iterable, Mapping

from multi_action_information_envelope import ActionEnvelope, action_information_envelope


@dataclass(frozen=True)
class LinearFrontier:
    candidates: tuple[Fraction, ...]
    peak_weight: Fraction
    peak_information_value: Fraction
    peak_envelope: ActionEnvelope


def _canonical(
    states: Iterable[tuple[Fraction, Mapping[str, tuple[Fraction, Fraction]]]],
) -> tuple[tuple[Fraction, dict[str, tuple[Fraction, Fraction]]], ...]:
    rows=tuple((Fraction(p), {str(a):(Fraction(r),Fraction(c))
                              for a,(r,c) in actions.items()})
               for p,actions in states)
    if (not rows or not rows[0][1]
            or any(p<0 or set(actions)!=set(rows[0][1]) for p,actions in rows)
            or sum((p for p,_ in rows),Fraction())!=1):
        raise ValueError("normalized prior and nonempty common action set required")
    return rows


def evaluate_linear_choice(
    states: Iterable[tuple[Fraction, Mapping[str, tuple[Fraction, Fraction]]]],
    weight: Fraction,
) -> ActionEnvelope:
    """Reward intercept minus weight times action/state cost."""
    w=Fraction(weight)
    if w<0:
        raise ValueError("negative weights are out of scope")
    rows=_canonical(states)
    return action_information_envelope(
        (p,{a:r-w*c for a,(r,c) in actions.items()}) for p,actions in rows
    )


def exact_linear_frontier(
    states: Iterable[tuple[Fraction, Mapping[str, tuple[Fraction, Fraction]]]],
) -> LinearFrontier:
    """Enumerate every nonnegative potentially policy-changing weight.

    Each line is affine in weight, so the observation premium is continuous
    piecewise affine. Maximal information value occurs at an intersection;
    beyond the final one, all optimal actions minimize cost and the premium
    is constant. The enumerated superset may include irrelevant crossings.

    The cost assigned to each action must be state independent. With
    state-dependent costs the information premium may grow without bound as
    weight grows, so a finite global maximum need not exist.
    """
    rows=_canonical(states)
    actions=tuple(rows[0][1])
    if any(lines[a][1] != rows[0][1][a][1]
           for _,lines in rows[1:] for a in actions):
        raise ValueError("global peak requires state-independent action costs")
    means={a:tuple(sum((p*lines[a][i] for p,lines in rows),Fraction())
                   for i in (0,1)) for a in actions}
    candidates={Fraction(0)}
    for payoffs in [means]+[lines for _,lines in rows]:
        for a,b in combinations(actions,2):
            ra,ca=payoffs[a]
            rb,cb=payoffs[b]
            if ca!=cb:
                t=(ra-rb)/(ca-cb)
                if t>=0:
                    candidates.add(t)
    thresholds=tuple(sorted(candidates))
    results=((w,evaluate_linear_choice(rows,w)) for w in thresholds)
    best_weight,best=max(results,key=lambda row:row[1].information_value)
    return LinearFrontier(thresholds,best_weight,best.information_value,best)
