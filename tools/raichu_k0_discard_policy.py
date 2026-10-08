"""Exact K0 Quick Ball discard policy for Harto Miki's Raichu list.

The player has not searched the deck yet. The observable branch requires:
- Alolan Raichu is not among the visible opening/draw cards;
- Quick Ball, at least one Gladion, and at least one conservative disposable
  card are in the action hand.

Two candidate Quick Ball payments are compared on the same hidden Prize worlds:
discard one visible Gladion, or discard one conservative disposable card.

Quick Ball then attempts to find Crobat V. If a Crobat V remains in deck, the
search establishes K1 and the model tries to put Alolan Raichu into hand in the
same turn through visible/drawn Gladion, Ultra Ball, Computer Search, Forest
Seal Stone, and one-card Dark Asset exposure.

The model deliberately keeps the pre-search payment policy observation
consistent. It also reports an information-privileged oracle for comparison.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from raichu_prize_access import (
    _bounded_compositions,
    _choose,
    _multivariate_probability,
    accepted_opening_probability,
)


@dataclass(frozen=True)
class K0DiscardPolicyResult:
    state_mass: float
    valid_opening_probability: float
    observable_branch_mass: float
    target_prized_mass: float
    crobat_search_failure_mass: float
    fixed_gladion_discard_success_mass: float
    fixed_disposable_discard_success_mass: float
    optimal_k0_success_mass: float
    hidden_state_oracle_success_mass: float
    k0_choose_gladion_mass: float
    k0_choose_disposable_mass: float
    k0_tie_mass: float
    observation_count: int
    choose_gladion_observations: int
    choose_disposable_observations: int
    tie_observations: int

    def _conditional(self, value: float) -> float:
        if self.observable_branch_mass == 0.0:
            return 0.0
        return value / self.observable_branch_mass

    @property
    def conditional_target_prized(self) -> float:
        return self._conditional(self.target_prized_mass)

    @property
    def conditional_crobat_search_failure(self) -> float:
        return self._conditional(self.crobat_search_failure_mass)

    @property
    def fixed_gladion_discard_success(self) -> float:
        return self._conditional(self.fixed_gladion_discard_success_mass)

    @property
    def fixed_disposable_discard_success(self) -> float:
        return self._conditional(self.fixed_disposable_discard_success_mass)

    @property
    def optimal_k0_success(self) -> float:
        return self._conditional(self.optimal_k0_success_mass)

    @property
    def hidden_state_oracle_success(self) -> float:
        return self._conditional(self.hidden_state_oracle_success_mass)

    @property
    def oracle_advantage(self) -> float:
        return self.hidden_state_oracle_success - self.optimal_k0_success

    @property
    def optimal_gain_over_fixed_gladion(self) -> float:
        return self.optimal_k0_success - self.fixed_gladion_discard_success

    @property
    def optimal_gain_over_fixed_disposable(self) -> float:
        return self.optimal_k0_success - self.fixed_disposable_discard_success

    @property
    def conditional_choice_mass(self) -> dict[str, float]:
        return {
            "discard_gladion": self._conditional(self.k0_choose_gladion_mass),
            "discard_disposable": self._conditional(self.k0_choose_disposable_mass),
            "tie": self._conditional(self.k0_tie_mass),
        }


def visible_policy_choice(hand: tuple[int, ...]) -> str:
    """Return the exact optimal K0 action for the modeled visible hand.

    Category order:
    target, Gladion, Ultra Ball, Computer Search, Forest Seal Stone,
    Crobat V, Quick Ball, disposable non-starter, disposable starter,
    other starter, other.

    The rule uses only information visible before Quick Ball searches the deck.
    """

    gladion = hand[1]
    ultra_ball = hand[2]
    computer_search = hand[3]
    forest_seal = hand[4]
    disposable = hand[7] + hand[8]

    if gladion >= 2:
        return "gladion"
    if forest_seal > 0:
        return "disposable"
    if disposable >= 3:
        return "disposable"
    if ultra_ball > 0 or computer_search > 0:
        return "gladion"
    return "disposable"


def _post_search_success_probability(
    *,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    discard_choice: str,
    deck_size: int,
    prize_count: int,
    opening_hand_size: int,
    computer_discard_cost: int,
) -> tuple[float, bool, bool]:
    """Execute the fixed Quick Ball -> Crobat line in one hidden physical state."""

    target_prized = deck[0] == 0
    target_in_deck = deck[0] > 0
    if not (target_prized ^ target_in_deck):
        raise AssertionError("singleton target must be in deck or Prizes")

    if deck[5] < 1:
        return 0.0, target_prized, False

    post_hand = list(hand)
    post_deck = list(deck)
    post_hand[6] -= 1

    if discard_choice == "gladion":
        post_hand[1] -= 1
    elif discard_choice == "disposable":
        if post_hand[7] > 0:
            post_hand[7] -= 1
        else:
            post_hand[8] -= 1
    else:
        raise ValueError("discard_choice must be 'gladion' or 'disposable'")

    post_deck[5] -= 1

    gladion_hand = post_hand[1]
    gladion_deck = post_deck[1]
    ultra_hand = post_hand[2]
    ultra_deck = post_deck[2]
    computer_hand = post_hand[3]
    computer_deck = post_deck[3]
    forest_hand = post_hand[4]
    forest_deck = post_deck[4]
    disposable = post_hand[7] + post_hand[8]
    disposable_deck = post_deck[7] + post_deck[8]
    two_card_payable = disposable >= computer_discard_cost

    if target_in_deck:
        immediate = forest_hand > 0 or (
            two_card_payable and (ultra_hand > 0 or computer_hand > 0)
        )
    else:
        immediate = gladion_hand > 0 or (
            gladion_deck > 0
            and (
                forest_hand > 0
                or (two_card_payable and computer_hand > 0)
            )
        )

    if immediate:
        return 1.0, target_prized, True

    post_search_deck_size = (
        deck_size - opening_hand_size - 1 - prize_count - 1
    )
    if post_search_deck_size <= 0:
        return 0.0, target_prized, True

    successful_top_cards = 0

    if target_in_deck:
        successful_top_cards += post_deck[0]
        successful_top_cards += forest_deck
        if two_card_payable:
            successful_top_cards += ultra_deck + computer_deck
        if (
            disposable == computer_discard_cost - 1
            and (ultra_hand > 0 or computer_hand > 0)
        ):
            successful_top_cards += disposable_deck
    else:
        successful_top_cards += gladion_deck
        if gladion_deck > 0:
            successful_top_cards += forest_deck
        if two_card_payable and gladion_deck > 0:
            successful_top_cards += computer_deck
        if (
            disposable == computer_discard_cost - 1
            and computer_hand > 0
            and gladion_deck > 0
        ):
            successful_top_cards += disposable_deck

    return (
        successful_top_cards / post_search_deck_size,
        target_prized,
        True,
    )


def k0_discard_policy_snapshot(
    *,
    deck_size: int = 60,
    prize_count: int = 6,
    opening_hand_size: int = 7,
    gladion_copies: int = 2,
    ultra_ball_copies: int = 3,
    computer_search_copies: int = 1,
    forest_seal_copies: int = 1,
    crobat_v_copies: int = 2,
    quick_ball_copies: int = 2,
    disposable_nonstarter_copies: int = 11,
    disposable_starter_copies: int = 1,
    other_starter_copies: int = 13,
    computer_discard_cost: int = 2,
) -> K0DiscardPolicyResult:
    """Compare K0-consistent Quick Ball payment policies exactly."""

    counts = (
        prize_count,
        opening_hand_size,
        gladion_copies,
        ultra_ball_copies,
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
    if opening_hand_size + prize_count + 2 > deck_size:
        raise ValueError("deck is too small for the requested zones")

    target_copies = 1
    starter_cards = (
        crobat_v_copies + disposable_starter_copies + other_starter_copies
    )
    used = (
        target_copies
        + gladion_copies
        + ultra_ball_copies
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
        ultra_ball_copies,
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

    observation_totals: dict[
        tuple[str, tuple[int, ...]], list[float]
    ] = defaultdict(lambda: [0.0, 0.0, 0.0])

    state_mass = 0.0
    branch_mass = 0.0
    target_prized_mass = 0.0
    crobat_failure_mass = 0.0
    oracle_success_mass = 0.0

    draw_pool_size = deck_size - opening_hand_size
    prize_pool_size = draw_pool_size - 1
    prize_denominator = _choose(prize_pool_size, prize_count)

    for opening in _bounded_compositions(opening_hand_size, sizes):
        if opening[5] + opening[8] + opening[9] == 0:
            continue

        opening_mass = _multivariate_probability(opening, sizes) / accepted
        remaining_after_opening = [
            size - count for size, count in zip(sizes, opening)
        ]

        action_opening = list(opening)
        if opening[5] > 0:
            action_opening[5] -= 1
            active_kind = "crobat_v"
        elif opening[9] > 0:
            action_opening[9] -= 1
            active_kind = "other_starter"
        else:
            action_opening[8] -= 1
            active_kind = "disposable_starter"

        for draw_category, draw_count in enumerate(remaining_after_opening):
            if draw_count == 0:
                continue

            draw_mass = draw_count / draw_pool_size
            hand = action_opening.copy()
            hand[draw_category] += 1
            prize_pool = remaining_after_opening.copy()
            prize_pool[draw_category] -= 1

            base_mass = opening_mass * draw_mass
            state_mass += base_mass

            if (
                hand[0] > 0
                or hand[6] < 1
                or hand[1] < 1
                or hand[7] + hand[8] < 1
            ):
                continue

            observation = (active_kind, tuple(hand))
            focused_pool = (
                prize_pool[0],
                prize_pool[1],
                prize_pool[2],
                prize_pool[3],
                prize_pool[4],
                prize_pool[5],
                prize_pool[7],
                prize_pool[8],
                prize_pool[6] + prize_pool[9] + prize_pool[10],
            )

            for prizes in _bounded_compositions(prize_count, focused_pool):
                ways = 1
                for size, count in zip(focused_pool, prizes):
                    ways *= _choose(size, count)
                if ways == 0:
                    continue

                mass = base_mass * ways / prize_denominator
                branch_mass += mass

                tp, gp, up, cp, fp, cvp, dnp, dsp, other_prized = prizes
                deck = prize_pool.copy()
                for index, count in zip(
                    (0, 1, 2, 3, 4, 5, 7, 8),
                    (tp, gp, up, cp, fp, cvp, dnp, dsp),
                ):
                    deck[index] -= count

                grouped_other = (
                    deck[6] + deck[9] + deck[10] - other_prized
                )
                if grouped_other < 0:
                    raise AssertionError("invalid grouped Prize count")
                deck[6] = 0
                deck[9] = 0
                deck[10] = grouped_other

                target_prized = tp > 0
                target_prized_mass += mass * target_prized
                if deck[5] < 1:
                    crobat_failure_mass += mass

                gladion_success, _, _ = _post_search_success_probability(
                    hand=tuple(hand),
                    deck=tuple(deck),
                    discard_choice="gladion",
                    deck_size=deck_size,
                    prize_count=prize_count,
                    opening_hand_size=opening_hand_size,
                    computer_discard_cost=computer_discard_cost,
                )
                disposable_success, _, _ = _post_search_success_probability(
                    hand=tuple(hand),
                    deck=tuple(deck),
                    discard_choice="disposable",
                    deck_size=deck_size,
                    prize_count=prize_count,
                    opening_hand_size=opening_hand_size,
                    computer_discard_cost=computer_discard_cost,
                )

                aggregate = observation_totals[observation]
                aggregate[0] += mass
                aggregate[1] += mass * gladion_success
                aggregate[2] += mass * disposable_success
                oracle_success_mass += mass * max(
                    gladion_success, disposable_success
                )

    fixed_gladion_mass = sum(row[1] for row in observation_totals.values())
    fixed_disposable_mass = sum(row[2] for row in observation_totals.values())

    optimal_k0_mass = 0.0
    choose_gladion_mass = 0.0
    choose_disposable_mass = 0.0
    tie_mass = 0.0
    choose_gladion_observations = 0
    choose_disposable_observations = 0
    tie_observations = 0

    for (_, hand), (mass, gladion_value, disposable_value) in observation_totals.items():
        optimal_k0_mass += max(gladion_value, disposable_value)

        if abs(gladion_value - disposable_value) < 1e-15:
            tie_mass += mass
            tie_observations += 1
        elif gladion_value > disposable_value:
            choose_gladion_mass += mass
            choose_gladion_observations += 1
        else:
            choose_disposable_mass += mass
            choose_disposable_observations += 1

        policy = visible_policy_choice(hand)
        policy_value = (
            gladion_value if policy == "gladion" else disposable_value
        )
        if abs(policy_value - max(gladion_value, disposable_value)) >= 1e-12:
            raise AssertionError(
                "visible_policy_choice is not optimal for an observation"
            )

    return K0DiscardPolicyResult(
        state_mass=state_mass,
        valid_opening_probability=accepted,
        observable_branch_mass=branch_mass,
        target_prized_mass=target_prized_mass,
        crobat_search_failure_mass=crobat_failure_mass,
        fixed_gladion_discard_success_mass=fixed_gladion_mass,
        fixed_disposable_discard_success_mass=fixed_disposable_mass,
        optimal_k0_success_mass=optimal_k0_mass,
        hidden_state_oracle_success_mass=oracle_success_mass,
        k0_choose_gladion_mass=choose_gladion_mass,
        k0_choose_disposable_mass=choose_disposable_mass,
        k0_tie_mass=tie_mass,
        observation_count=len(observation_totals),
        choose_gladion_observations=choose_gladion_observations,
        choose_disposable_observations=choose_disposable_observations,
        tie_observations=tie_observations,
    )
