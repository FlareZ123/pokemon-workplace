"""Exact full-state backup-Gladion rescue after Quick Ball -> Crobat V.

This deck-specific component reconnects the clean post-search connector race to
Harto Miki's 2024 Aichi Raichu/Electrode state distribution.

The policy is deliberately specific:
- begin from a valid seven-card opening plus one ordinary random draw;
- one setup Basic has already moved from the opening hand to the Active Spot;
- Alolan Raichu is in the Prize cards, although that is not known yet;
- Quick Ball and at least one Gladion are in the action hand;
- pay Quick Ball by discarding one visible Gladion;
- Quick Ball finds a deck-resident Crobat V, establishing K1 and revealing that
  Alolan Raichu is Prized;
- ask whether the remaining Gladion can be reached in the same turn via a
  second visible Gladion, Forest Seal Stone, Computer Search, or one-card
  Dark Asset exposure.

Computer Search uses the same conservative disposable-card policy as the earlier
Raichu models. Forest Seal Stone is assumed mechanically live once the searched
Crobat V is benched: open Tool slot, no relevant lock, and unused VSTAR Power.
"""

from __future__ import annotations

from dataclasses import dataclass

from raichu_prize_access import (
    _bounded_compositions,
    _choose,
    _multivariate_probability,
    accepted_opening_probability,
)


@dataclass(frozen=True)
class FullBackupRescueResult:
    state_mass: float
    valid_opening_probability: float
    branch_mass: float
    backup_in_hand_mass: float
    backup_in_deck_mass: float
    backup_prized_mass: float
    forest_seal_in_hand_mass: float
    computer_search_in_hand_mass: float
    one_disposable_mass: float
    two_disposable_mass: float
    topology_ceiling_mass: float
    immediate_rescue_mass: float
    final_rescue_mass: float
    draw_increment_mass: float
    attr_backup_in_hand_mass: float
    attr_forest_seal_in_hand_mass: float
    attr_computer_search_in_hand_mass: float
    attr_draw_backup_mass: float
    attr_draw_forest_seal_mass: float
    attr_draw_computer_search_mass: float
    attr_draw_disposable_enable_mass: float

    def _conditional(self, value: float) -> float:
        if self.branch_mass == 0.0:
            return 0.0
        return value / self.branch_mass

    @property
    def conditional_backup_in_hand(self) -> float:
        return self._conditional(self.backup_in_hand_mass)

    @property
    def conditional_backup_in_deck(self) -> float:
        return self._conditional(self.backup_in_deck_mass)

    @property
    def conditional_backup_prized(self) -> float:
        return self._conditional(self.backup_prized_mass)

    @property
    def conditional_forest_seal_in_hand(self) -> float:
        return self._conditional(self.forest_seal_in_hand_mass)

    @property
    def conditional_computer_search_in_hand(self) -> float:
        return self._conditional(self.computer_search_in_hand_mass)

    @property
    def conditional_one_disposable(self) -> float:
        return self._conditional(self.one_disposable_mass)

    @property
    def conditional_two_disposable(self) -> float:
        return self._conditional(self.two_disposable_mass)

    @property
    def conditional_topology_ceiling(self) -> float:
        return self._conditional(self.topology_ceiling_mass)

    @property
    def conditional_immediate_rescue(self) -> float:
        return self._conditional(self.immediate_rescue_mass)

    @property
    def conditional_final_rescue(self) -> float:
        return self._conditional(self.final_rescue_mass)

    @property
    def conditional_draw_increment(self) -> float:
        return self._conditional(self.draw_increment_mass)

    @property
    def conditional_topology_gap(self) -> float:
        return self.conditional_topology_ceiling - self.conditional_final_rescue

    @property
    def conditional_attributions(self) -> dict[str, float]:
        return {
            "backup_in_hand": self._conditional(self.attr_backup_in_hand_mass),
            "forest_seal_in_hand": self._conditional(self.attr_forest_seal_in_hand_mass),
            "computer_search_in_hand": self._conditional(
                self.attr_computer_search_in_hand_mass
            ),
            "draw_backup": self._conditional(self.attr_draw_backup_mass),
            "draw_forest_seal": self._conditional(self.attr_draw_forest_seal_mass),
            "draw_computer_search": self._conditional(
                self.attr_draw_computer_search_mass
            ),
            "draw_disposable_enable": self._conditional(
                self.attr_draw_disposable_enable_mass
            ),
        }


def full_backup_rescue_snapshot(
    *,
    deck_size: int = 60,
    prize_count: int = 6,
    opening_hand_size: int = 7,
    gladion_copies: int = 2,
    computer_search_copies: int = 1,
    forest_seal_copies: int = 1,
    crobat_v_copies: int = 2,
    quick_ball_copies: int = 2,
    disposable_nonstarter_copies: int = 11,
    disposable_starter_copies: int = 1,
    other_starter_copies: int = 13,
    computer_discard_cost: int = 2,
    computer_search_live: bool = True,
    forest_seal_live: bool = True,
    dark_asset_live: bool = True,
) -> FullBackupRescueResult:
    """Return exact same-turn backup rescue in the specified Quick Ball branch."""

    counts = (
        prize_count,
        opening_hand_size,
        gladion_copies,
        computer_search_copies,
        forest_seal_copies,
        crobat_v_copies,
        quick_ball_copies,
        disposable_nonstarter_copies,
        disposable_starter_copies,
        other_starter_copies,
        computer_discard_cost,
    )
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if min(counts) < 0:
        raise ValueError("counts and costs must be non-negative")
    if gladion_copies != 2:
        raise ValueError("this Harto-specific backup model requires exactly two Gladion")
    if computer_search_copies > 1 or forest_seal_copies > 1:
        raise ValueError("Computer Search and Forest Seal Stone support at most one copy")
    if crobat_v_copies < 1 or quick_ball_copies < 1:
        raise ValueError("at least one Crobat V and Quick Ball are required")
    if opening_hand_size + prize_count + 2 > deck_size:
        raise ValueError("deck is too small for setup, draw, Prizes, and Crobat search")

    target_copies = 1
    starter_cards = (
        crobat_v_copies + disposable_starter_copies + other_starter_copies
    )
    if starter_cards <= 0:
        raise ValueError("at least one setup-eligible Basic is required")

    used = (
        target_copies
        + gladion_copies
        + computer_search_copies
        + forest_seal_copies
        + crobat_v_copies
        + quick_ball_copies
        + disposable_nonstarter_copies
        + disposable_starter_copies
        + other_starter_copies
    )
    if used > deck_size:
        raise ValueError("modeled categories exceed deck size")

    sizes = (
        target_copies,
        gladion_copies,
        computer_search_copies,
        forest_seal_copies,
        crobat_v_copies,
        quick_ball_copies,
        disposable_nonstarter_copies,
        disposable_starter_copies,
        other_starter_copies,
        deck_size - used,
    )

    accepted = accepted_opening_probability(
        deck_size, starter_cards, opening_hand_size
    )
    if accepted == 0.0:
        raise ValueError("valid-opening conditioning event has zero probability")

    names = (
        "state_mass",
        "branch_mass",
        "backup_in_hand_mass",
        "backup_in_deck_mass",
        "backup_prized_mass",
        "forest_seal_in_hand_mass",
        "computer_search_in_hand_mass",
        "one_disposable_mass",
        "two_disposable_mass",
        "topology_ceiling_mass",
        "immediate_rescue_mass",
        "final_rescue_mass",
        "draw_increment_mass",
        "attr_backup_in_hand_mass",
        "attr_forest_seal_in_hand_mass",
        "attr_computer_search_in_hand_mass",
        "attr_draw_backup_mass",
        "attr_draw_forest_seal_mass",
        "attr_draw_computer_search_mass",
        "attr_draw_disposable_enable_mass",
    )
    metrics = {name: 0.0 for name in names}

    draw_pool_size = deck_size - opening_hand_size
    prize_pool_size = draw_pool_size - 1
    prize_denominator = _choose(prize_pool_size, prize_count)

    for opening in _bounded_compositions(opening_hand_size, sizes):
        if opening[4] + opening[7] + opening[8] == 0:
            continue
        opening_mass = _multivariate_probability(opening, sizes) / accepted
        remaining_after_opening = [
            size - count for size, count in zip(sizes, opening)
        ]

        action_hand = list(opening)
        if opening[4] > 0:
            action_hand[4] -= 1
        elif opening[8] > 0:
            action_hand[8] -= 1
        else:
            action_hand[7] -= 1

        for draw_category, draw_count in enumerate(remaining_after_opening):
            if draw_count == 0:
                continue
            draw_mass = draw_count / draw_pool_size
            hand = action_hand.copy()
            hand[draw_category] += 1
            prize_pool = remaining_after_opening.copy()
            prize_pool[draw_category] -= 1

            focused_pool = (
                prize_pool[0],
                prize_pool[1],
                prize_pool[2],
                prize_pool[3],
                prize_pool[4],
                prize_pool[6],
                prize_pool[7],
                prize_pool[5] + prize_pool[8] + prize_pool[9],
            )

            for focused_prizes in _bounded_compositions(prize_count, focused_pool):
                ways = 1
                for size, count in zip(focused_pool, focused_prizes):
                    ways *= _choose(size, count)
                if ways == 0:
                    continue
                mass = opening_mass * draw_mass * ways / prize_denominator
                metrics["state_mass"] += mass

                tp, gp, cp, fp, cvp, dnp, dsp, _ = focused_prizes
                if tp != 1 or hand[5] < 1 or hand[1] < 1:
                    continue

                deck = prize_pool.copy()
                deck[0] -= tp
                deck[1] -= gp
                deck[2] -= cp
                deck[3] -= fp
                deck[4] -= cvp
                deck[6] -= dnp
                deck[7] -= dsp

                filler_prized = focused_prizes[7]
                filler_deck = (
                    deck[5] + deck[8] + deck[9] - filler_prized
                )
                if filler_deck < 0:
                    raise AssertionError("invalid marginalized filler Prize count")
                deck[5] = 0
                deck[8] = 0
                deck[9] = filler_deck

                if deck[4] < 1:
                    continue

                metrics["branch_mass"] += mass

                post_hand = hand.copy()
                post_hand[5] -= 1
                post_hand[1] -= 1
                deck[4] -= 1

                if sum(post_hand) != opening_hand_size - 2:
                    raise AssertionError("post-Quick-Ball hand should contain five cards")
                if sum(deck) != (
                    deck_size - opening_hand_size - 1 - prize_count - 1
                ):
                    raise AssertionError("post-search deck size mismatch")

                backup_in_hand = post_hand[1] > 0
                backup_in_deck = deck[1] > 0
                backup_prized = not backup_in_hand and not backup_in_deck
                if sum((backup_in_hand, backup_in_deck, backup_prized)) != 1:
                    raise AssertionError("backup Gladion must occupy exactly one zone")

                disposable = post_hand[6] + post_hand[7]
                forest_in_hand = post_hand[3] > 0
                computer_in_hand = post_hand[2] > 0

                metrics["backup_in_hand_mass"] += mass * backup_in_hand
                metrics["backup_in_deck_mass"] += mass * backup_in_deck
                metrics["backup_prized_mass"] += mass * backup_prized
                metrics["forest_seal_in_hand_mass"] += mass * forest_in_hand
                metrics["computer_search_in_hand_mass"] += mass * computer_in_hand
                metrics["one_disposable_mass"] += mass * (disposable >= 1)
                metrics["two_disposable_mass"] += mass * (
                    disposable >= computer_discard_cost
                )
                metrics["topology_ceiling_mass"] += mass * (
                    backup_in_hand or backup_in_deck
                )

                immediate = False
                if backup_in_hand:
                    immediate = True
                    metrics["attr_backup_in_hand_mass"] += mass
                elif backup_in_deck and forest_seal_live and forest_in_hand:
                    immediate = True
                    metrics["attr_forest_seal_in_hand_mass"] += mass
                elif (
                    backup_in_deck
                    and computer_search_live
                    and computer_in_hand
                    and disposable >= computer_discard_cost
                ):
                    immediate = True
                    metrics["attr_computer_search_in_hand_mass"] += mass

                metrics["immediate_rescue_mass"] += mass * immediate
                if immediate:
                    metrics["final_rescue_mass"] += mass
                    continue
                if not backup_in_deck or not dark_asset_live:
                    continue

                post_search_deck_size = sum(deck)
                draw_success = 0.0
                for category, count in enumerate(deck):
                    if count == 0:
                        continue
                    probability = count / post_search_deck_size
                    disposable_after = disposable + int(category in (6, 7))
                    backup_after = deck[1] - int(category == 1)

                    if category == 1:
                        draw_success += probability
                        metrics["attr_draw_backup_mass"] += mass * probability
                    elif category == 3 and backup_after > 0 and forest_seal_live:
                        draw_success += probability
                        metrics["attr_draw_forest_seal_mass"] += mass * probability
                    elif (
                        category == 2
                        and computer_search_live
                        and backup_after > 0
                        and disposable_after >= computer_discard_cost
                    ):
                        draw_success += probability
                        metrics["attr_draw_computer_search_mass"] += mass * probability
                    elif (
                        category in (6, 7)
                        and computer_search_live
                        and backup_after > 0
                        and computer_in_hand
                        and disposable + 1 >= computer_discard_cost
                    ):
                        draw_success += probability
                        metrics["attr_draw_disposable_enable_mass"] += (
                            mass * probability
                        )

                metrics["draw_increment_mass"] += mass * draw_success
                metrics["final_rescue_mass"] += mass * draw_success

    return FullBackupRescueResult(
        valid_opening_probability=accepted,
        **metrics,
    )
