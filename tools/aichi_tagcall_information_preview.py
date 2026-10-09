"""Optional Tag Call preview before G&H for late Jirachi Ticket access.

The represented optional action spends a held Tag Call, retrieves up to two
additional G&H copies, and searches the deck before the pending G&H payment.
It can therefore establish K1 at the payment deadline. Quantities are
hindsight-existence access bounds; the K0-safe guard only prevents sacrificing
already-held Tool, Special Energy, and Stadium outputs.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from math import sqrt
import random

from tools.aichi_gnh_discard_frontier import paid_gnh_states
from tools.aichi_jirachi_payment_frontier import (
    accessible_probability, prior_full_deck_search,
)
from tools.aichi_jirachi_ticket_search import (
    prepare_with_deferred_stellar, stellar_available,
)
from tools.aichi_post_gnh_prize_reset import (
    DECK, TECH_SLOTS, endpoint_success, protect_gnh_outputs,
)
from tools.aichi_tagcall_payment_reachability import additional_tag_call
from tools.aichi_repeated_ticket_access import PACKAGES


SAFE_OUTPUTS = frozenset((
    "Technical Machine: Evolution", "Jet Energy", "Artazon",
))
OBJECTIVES = ("dual_stage2", "item_lock", "item_plus_pidgeot")
PACKAGES_OF_INTEREST = (
    "one_ticket", "two_tickets_one_map", "three_tickets_one_map",
)


def paths_for_endpoint(state, objective: str, protected=frozenset()):
    return tuple(
        path for path in paid_gnh_states(state, protected)
        if endpoint_success(objective, path.hand, path.remaining, state.active)
    )


def best_access(paths, assignment, *, eligible: bool) -> float:
    return max((
        accessible_probability(path.hand, path.remaining, assignment,
                               eligible, "first")
        for path in paths
    ), default=0.0)


@dataclass
class Summary:
    raw: int = 0
    accepted: int = 0
    core: int = 0
    eligible: int = 0
    pre_k1_eligible: int = 0
    optional_preview_available: int = 0
    affected_endpoint: Counter[str] = field(default_factory=Counter)
    guard: Counter[tuple[str,str]] = field(default_factory=Counter)
    preview: Counter[tuple[str,str]] = field(default_factory=Counter)
    material_only: Counter[tuple[str,str]] = field(default_factory=Counter)
    material_benefit: Counter[tuple[str,str]] = field(default_factory=Counter)
    guard_relaxation_benefit: Counter[tuple[str,str]] = field(default_factory=Counter)
    material_helped: Counter[tuple[str,str]] = field(default_factory=Counter)
    relaxation_helped: Counter[tuple[str,str]] = field(default_factory=Counter)
    benefit: Counter[tuple[str,str]] = field(default_factory=Counter)
    benefit_squares: Counter[tuple[str,str]] = field(default_factory=Counter)
    positive: Counter[tuple[str,str]] = field(default_factory=Counter)
    harm_if_forced: Counter[tuple[str,str]] = field(default_factory=Counter)


def simulate(raw_trials: int = 100_000, seed: int = 20261009) -> Summary:
    rng = random.Random(seed)
    out = Summary(raw=raw_trials)
    for _ in range(raw_trials):
        order = rng.sample(range(len(DECK)), len(DECK))
        state, deferred = prepare_with_deferred_stellar(order)
        if state is None:
            continue
        out.accepted += 1
        if protect_gnh_outputs(state) is None:
            continue
        out.core += 1
        late = deferred or stellar_available(order, state.active)
        out.eligible += int(late)
        if not late or prior_full_deck_search(order, state.active, deferred):
            continue
        out.pre_k1_eligible += 1

        boosted = additional_tag_call(state)
        if boosted is None:
            continue
        out.optional_preview_available += 1

        for objective in OBJECTIVES:
            regular = paths_for_endpoint(state, objective, SAFE_OUTPUTS)
            if not regular:
                continue
            out.affected_endpoint[objective] += 1
            after = paths_for_endpoint(boosted, objective)
            after_guarded = paths_for_endpoint(boosted, objective, SAFE_OUTPUTS)
            for package in PACKAGES_OF_INTEREST:
                assignment = PACKAGES[package]
                conservative = best_access(regular, assignment, eligible=late)
                guarded_material = best_access(after_guarded, assignment, eligible=late)
                material = max(conservative, guarded_material)
                optional = best_access(after, assignment, eligible=late)
                improved = max(material, optional)
                key = (objective, package)
                out.guard[key] += conservative
                out.material_only[key] += material
                out.preview[key] += improved
                out.material_benefit[key] += material - conservative
                out.guard_relaxation_benefit[key] += improved - material
                out.material_helped[key] += int(material > conservative + 1e-12)
                out.relaxation_helped[key] += int(improved > material + 1e-12)
                diff = improved - conservative
                out.benefit[key] += diff
                out.benefit_squares[key] += diff * diff
                out.positive[key] += int(diff > 1e-12)
                out.harm_if_forced[key] += int(optional < conservative - 1e-12)
                assert diff >= -1e-12
    return out


def output(s: Summary) -> str:
    lines = [
        f"raw={s.raw} accepted={s.accepted} core={s.core} "
        f"eligible_late={s.eligible} pre_K1_late={s.pre_k1_eligible} "
        f"optional_TagCall_K1_preview={s.optional_preview_available}",
        "endpoint | applicable endpoint-preserving states",
    ]
    for ep in OBJECTIVES:
        lines.append(f"{ep} | {s.affected_endpoint[ep]}")
    lines.append(
        "endpoint | package | safety-guarded first-reset% | optional "
        "TagCall preview first-reset% | benefit +/- paired 95% CI (pp) | "
        "material / guard-relaxation benefit pp | "
        "material / guard-relaxation helped states | forced-TagCall harmed states"
    )
    for ep in OBJECTIVES:
        for package in PACKAGES_OF_INTEREST:
            key = (ep, package)
            n = s.accepted
            mean = s.benefit[key] / n
            variance = max(0.0, s.benefit_squares[key]/n - mean*mean)
            ci = 100 * 1.96 * sqrt(variance / (n-1))
            lines.append(
                f"{ep} | {package} | {100*s.guard[key]/n:.9f}% | "
                f"{100*s.preview[key]/n:.9f}% | "
                f"{100*mean:+.9f} +/- {ci:.9f} | "
                f"{100*s.material_benefit[key]/n:+.9f}/"
                f"{100*s.guard_relaxation_benefit[key]/n:+.9f} | "
                f"{s.material_helped[key]}/{s.relaxation_helped[key]} | "
                f"{s.harm_if_forced[key]}"
            )
    return "\n".join(lines)


if __name__ == "__main__":
    print(output(simulate()))
