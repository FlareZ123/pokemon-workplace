"""Aichi first-turn access: optional Bellelba as Tag Call's second payload.

Supplements an extra held Tag Call's existing G&H-only fetch with
Bellelba & Brycen-Man when fewer than two G&H remain searchable.
The new Item line is searched before playing the already-obtained G&H
but the Prepared state records G&H as already consumed. The added
Bellelba is physical in hand and may fund G&H's two-card payment,
unless explicitly protected as strategically important.

This preserves the existing Aichi preparer's other abstractions,
including endpoint-conditioned post-K1 payment and late Jirachi's
hypergeometric first-reset access calculation.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from math import sqrt
import random

from tools.aichi_post_gnh_prize_reset import DECK, Prepared, endpoint_success, protect_gnh_outputs
from tools.aichi_jirachi_ticket_search import prepare_with_deferred_stellar, stellar_available
from tools.aichi_jirachi_payment_frontier import (
    accessible_probability, prior_full_deck_search,
)
from tools.aichi_gnh_discard_frontier import paid_gnh_states
from tools.aichi_tagcall_payment_reachability import additional_tag_call
from tools.aichi_repeated_ticket_access import PACKAGES


PROTECTED_OUTPUTS = frozenset((
    "Technical Machine: Evolution", "Jet Energy", "Artazon",
))
BELLELBA = "Bellelba & Brycen-Man"
GNH = "Guzma & Hala"
OBJECTIVES = ("dual_stage2", "item_lock", "item_plus_pidgeot")
PACKAGES_USED = ("one_ticket", "two_tickets_one_map", "three_tickets_one_map")


def supplement_with_bellelba(state: Prepared) -> Prepared | None:
    """Play held Tag Call for G&H copies plus one searchable Bellelba.

    Returns None unless Bellelba fills a slot that would otherwise be
    unfilled by the original additional G&H-only search.
    """
    if not state.gnh_access or state.hand["Tag Call"] <= 0:
        return None
    g = min(2, state.remaining[GNH])
    b = min(2-g, state.remaining[BELLELBA])
    if b <= 0:
        return None
    held = state.hand.copy()
    remaining = state.remaining.copy()
    held["Tag Call"] -= 1
    if not held["Tag Call"]:
        del held["Tag Call"]
    for name, number in ((GNH,g),(BELLELBA,b)):
        if number:
            held[name] += number
            remaining[name] -= number
            if not remaining[name]:
                del remaining[name]
    return Prepared(held, remaining, state.active, state.prizes, True)


def endpoint_paths(state: Prepared | None, objective: str, protection: frozenset[str]):
    if state is None:
        return ()
    return tuple(
        path for path in paid_gnh_states(state, protection)
        if endpoint_success(objective, path.hand, path.remaining, state.active)
    )


def chance(paths, assignment, late: bool) -> float:
    return max((
        accessible_probability(p.hand,p.remaining,assignment,late,"first")
        for p in paths
    ), default=0.0)


@dataclass
class Summary:
    raw: int = 0
    accepted: int = 0
    eligible: int = 0
    candidate_bellelba: int = 0
    already_gnh_target_count: Counter[int] = field(default_factory=Counter)
    baseline: Counter[tuple[str,str]] = field(default_factory=Counter)
    extended: Counter[tuple[str,str]] = field(default_factory=Counter)
    protected: Counter[tuple[str,str]] = field(default_factory=Counter)
    uplift_square: Counter[tuple[str,str]] = field(default_factory=Counter)
    improved: Counter[tuple[str,str]] = field(default_factory=Counter)
    protected_improved: Counter[tuple[str,str]] = field(default_factory=Counter)
    extra_material_payment: Counter[tuple[str,str]] = field(default_factory=Counter)


def simulate(raw_trials: int = 40_000, seed: int = 20261010) -> Summary:
    rng = random.Random(seed)
    out = Summary(raw=raw_trials)
    for _ in range(raw_trials):
        order = rng.sample(range(len(DECK)), len(DECK))
        state, deferred = prepare_with_deferred_stellar(order)
        if state is None:
            continue
        out.accepted += 1
        if not state.gnh_access or protect_gnh_outputs(state) is None:
            continue
        late = deferred or stellar_available(order,state.active)
        if not late or prior_full_deck_search(order,state.active,deferred):
            continue
        out.eligible += 1
        augmented = supplement_with_bellelba(state)
        if augmented is None:
            continue
        out.candidate_bellelba += 1
        out.already_gnh_target_count[min(2,state.remaining[GNH])] += 1
        baseline_tag = additional_tag_call(state)

        for objective in OBJECTIVES:
            original = endpoint_paths(state,objective,PROTECTED_OUTPUTS)
            with_g = endpoint_paths(baseline_tag,objective,frozenset())
            with_b = endpoint_paths(augmented,objective,frozenset())
            with_b_protected = endpoint_paths(
                augmented,objective,frozenset((BELLELBA,))
            )
            for package in PACKAGES_USED:
                key = (objective,package)
                assignment = PACKAGES[package]
                old = max(chance(original,assignment,late),
                          chance(with_g,assignment,late))
                new = max(old,chance(with_b,assignment,late))
                protected = max(old,chance(with_b_protected,assignment,late))
                assert new+1e-12 >= protected >= old-1e-12
                assert new >= old-1e-12
                out.baseline[key] += old
                out.extended[key] += new
                out.protected[key] += protected
                diff = new-old
                out.uplift_square[key] += diff*diff
                out.improved[key] += int(diff>1e-12)
                out.protected_improved[key] += int(protected>old+1e-12)
                out.extra_material_payment[key] += max(0, int(
                    bool(with_b) and not bool(with_g)
                ))
    return out


def report(s: Summary) -> str:
    out = [
        f"raw={s.raw} accepted={s.accepted} pre_K1_late={s.eligible} "
        f"early_Bellelba_TagCall_candidate={s.candidate_bellelba} "
        f"G&H_targets_by_fetch_slot={dict(s.already_gnh_target_count)}",
        "objective | item_package | baseline first reset % accepted | "
        "Bellelba allowed % | Bellelba protected % | uplift ± 95% half CI pp "
        "| helped / protected helped states | new paid endpoint without G-only",
    ]
    for objective in OBJECTIVES:
        for package in PACKAGES_USED:
            key = (objective,package)
            n = s.accepted
            delta = (s.extended[key]-s.baseline[key])/n
            ex2 = s.uplift_square[key]/n
            ci = 100*1.96*sqrt(max(0,(ex2-delta*delta)/(n-1)))
            out.append(
                f"{objective} | {package} | {100*s.baseline[key]/n:.9f}% | "
                f"{100*s.extended[key]/n:.9f}% | {100*s.protected[key]/n:.9f}% "
                f"| {100*delta:+.9f} +/- {ci:.9f} "
                f"| {s.improved[key]}/{s.protected_improved[key]} "
                f"| {s.extra_material_payment[key]}"
            )
    return "\n".join(out)
