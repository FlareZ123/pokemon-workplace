"""Exact K0/K1 information value of discarding a held Tool to thin a deck.

Toy channel:
- U unseen, exchangeable cards, of which P will be Prized.
- 1 backup Tool and 1 desired Ticket/Map target among those U.
- The player also holds one Tool (a guaranteed setup resource).
- G&H can fetch the backup only by first discarding the held Tool.
- If no replacement is fetched, the intended attack setup fails.
- A later Jirachi Stellar Wish inspects s uniformly sampled deck cards.
- All other prerequisites, including the optional two-card discard, are
  assumed to be available and have no opportunity cost.

This isolates first-full-search information, not an entire Aichi turn.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations


@dataclass(frozen=True)
class Values:
    k0_keep_setup: Fraction
    k0_replace_setup: Fraction
    k0_keep_joint: Fraction
    k0_replace_joint: Fraction
    k1_oracle_setup: Fraction
    k1_oracle_joint: Fraction
    k1_information_premium: Fraction


def exact(unseen: int, prizes: int, stellar_cards: int) -> Values:
    """Return exact unconditional probabilities over Prize placements and Wish."""
    if not (unseen >= 3 and 0 <= prizes <= unseen - 2):
        raise ValueError("Require at least two physically distinct unseen resources")
    d = unseen - prizes
    if not (1 <= stellar_cards <= d - 1):
        raise ValueError("Wish sample must fit even after backup Tool search")
    keep = Fraction(stellar_cards, unseen)
    replace = Fraction(stellar_cards * d, unseen * (unseen - 1))
    extra = Fraction(stellar_cards, unseen * (unseen - 1))
    return Values(
        k0_keep_setup=Fraction(1),
        k0_replace_setup=Fraction(d, unseen),
        k0_keep_joint=keep,
        k0_replace_joint=replace,
        k1_oracle_setup=Fraction(1),
        k1_oracle_joint=keep + extra,
        k1_information_premium=extra,
    )


def brute_force(unseen: int, prizes: int, stellar_cards: int) -> Values:
    """Independent labeled-Prize enumeration, averaging conditional Wish hits.

    Physical labels: 0=backup Tool, 1=Ticket/Map target, >=2=filler.
    """
    d = unseen - prizes
    if not 1 <= stellar_cards <= d - 1:
        raise ValueError("Invalid sample")
    sums = [Fraction(0) for _ in range(6)]
    worlds = 0
    for prized in combinations(range(unseen), prizes):
        ps = set(prized)
        backup = 0 not in ps
        ticket = 1 not in ps
        keep_hit = Fraction(stellar_cards, d) if ticket else Fraction(0)
        replace_hit = (Fraction(stellar_cards, d - 1)
                       if backup and ticket else Fraction(0))
        # Informed player only replaces the held Tool when both resources
        # are known to be in the deck and doing so improves Ticket access.
        informed_hit = replace_hit if backup and ticket else keep_hit
        row = (
            Fraction(1),
            Fraction(int(backup)),
            keep_hit,
            replace_hit,
            Fraction(1),
            informed_hit,
        )
        sums = [a + b for a, b in zip(sums, row)]
        worlds += 1
    result = [value / worlds for value in sums]
    return Values(*result, result[5] - result[2])



@dataclass(frozen=True)
class MultipleBackupValues:
    keep_joint: Fraction
    blindly_replace_setup: Fraction
    blindly_replace_joint: Fraction
    k1_adaptive_joint: Fraction
    backup_failure_and_target_available: Fraction
    k0_best_joint: Fraction


def exact_multiple(
    unseen: int, prizes: int, stellar_cards: int, backup_copies: int,
) -> MultipleBackupValues:
    """Exact Prize risk and hit probability with B exchangeable backup Tools.

    A held necessary Tool is safe. Blind replacement searches one of B backups.
    A target must remain in the deck to be hit by a subsequent Stellar Wish.
    """
    if not (2 <= unseen and 1 <= backup_copies <= unseen - 1
            and 0 <= prizes <= unseen - 2):
        raise ValueError("Invalid hidden-card or backup counts")
    d = unseen - prizes
    if not 1 <= stellar_cards <= d - 1:
        raise ValueError("Wish sample must fit the thinned deck")

    def probability_all_backups_prized(*, ticket_searchable: bool) -> Fraction:
        b = backup_copies
        if prizes < b:
            return Fraction(0)
        if ticket_searchable:
            return Fraction(comb(unseen - b - 1, prizes - b), comb(unseen, prizes))
        return Fraction(comb(unseen - b, prizes - b), comb(unseen, prizes))

    p_all = probability_all_backups_prized(ticket_searchable=False)
    r = probability_all_backups_prized(ticket_searchable=True)
    hit_kept = Fraction(stellar_cards, unseen)
    hit_replaced = Fraction(stellar_cards, d - 1) * (Fraction(d, unseen) - r)
    hit_informed = hit_replaced + Fraction(stellar_cards, d) * r
    return MultipleBackupValues(
        keep_joint=hit_kept,
        blindly_replace_setup=Fraction(1) - p_all,
        blindly_replace_joint=hit_replaced,
        k1_adaptive_joint=hit_informed,
        backup_failure_and_target_available=r,
        k0_best_joint=max(hit_kept, hit_replaced),
    )


def brute_force_multiple(
    unseen: int, prizes: int, stellar_cards: int, backup_copies: int,
) -> MultipleBackupValues:
    """Independent physical Prize-set enumeration for multiple backups."""
    d = unseen - prizes
    sums = [Fraction(0)] * 5
    worlds = 0
    for selected in combinations(range(unseen), prizes):
        ps = set(selected)
        available_backups = sum(i not in ps for i in range(backup_copies))
        target_available = int(backup_copies not in ps)
        all_prized_and_target = int(not available_backups and target_available)
        keep_hit = Fraction(stellar_cards, d) * target_available
        replace_hit = (
            Fraction(stellar_cards, d - 1)
            if available_backups > 0 and target_available else Fraction(0)
        )
        informed_hit = replace_hit if available_backups else keep_hit
        v = (keep_hit, Fraction(int(available_backups > 0)), replace_hit,
             informed_hit, Fraction(all_prized_and_target))
        sums = [a + b for a, b in zip(sums, v)]
        worlds += 1
    keep, setup, blind, informed, r = (value / worlds for value in sums)
    return MultipleBackupValues(keep, setup, blind, informed, r, max(keep, blind))


def multiple_summary(unseen: int = 52, prizes: int = 6,
                     stellar_cards: int = 5, max_backups: int = 4) -> str:
    lines = [
        f"U={unseen} P={prizes} s={stellar_cards} backups=1..{max_backups}",
        "backups | keep_joint% | blind_joint% | K1_joint% | "
        "blind_setup% | K0 optimal policy",
    ]
    for b in range(1, max_backups + 1):
        x = exact_multiple(unseen, prizes, stellar_cards, b)
        policy = "replace" if x.blindly_replace_joint > x.keep_joint else (
            "keep" if x.blindly_replace_joint < x.keep_joint else "tie"
        )
        lines.append(
            f"{b} | {100 * float(x.keep_joint):.9f} | "
            f"{100 * float(x.blindly_replace_joint):.9f} | "
            f"{100 * float(x.k1_adaptive_joint):.9f} | "
            f"{100 * float(x.blindly_replace_setup):.9f} | {policy}"
        )
    return "\n".join(lines)


def describe(unseen: int = 52, prizes: int = 6, stellar_cards: int = 5) -> str:
    x = exact(unseen, prizes, stellar_cards)
    pairs = (
        ("Keep held Tool: setup", x.k0_keep_setup),
        ("Replace Tool blindly: setup", x.k0_replace_setup),
        ("Keep Tool: setup AND Ticket hit", x.k0_keep_joint),
        ("Replace Tool blindly: setup AND Ticket hit", x.k0_replace_joint),
        ("K1-adaptive: setup AND Ticket hit", x.k1_oracle_joint),
        ("K1 information premium", x.k1_information_premium),
    )
    return (f"U={unseen} P={prizes} s={stellar_cards} D={unseen-prizes}\n"
            + "\n".join(f"{name}: {value} = {100*float(value):.9f}%"
                        for name, value in pairs))


if __name__ == "__main__":
    print(describe())
    print(multiple_summary())
