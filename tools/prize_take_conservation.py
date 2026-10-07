"""Conserve physical Prize takes and update grouped Prize beliefs.

The physical ledger owns the exact hidden-zone truth. PrizeBelief owns one
player's uncertainty about the current Prize composition. This adapter advances
both when a face-down Prize card is taken into hand and its identity becomes
known to that player.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from identity_materialization import IdentityLedger, assert_conserved
from prize_belief_kernel import PrizeBelief

PRIZE = "prize"
HAND = "hand"


@dataclass(frozen=True)
class PrizeTakeResult:
    ledger: IdentityLedger
    belief: PrizeBelief


def observation_probability(
    belief: PrizeBelief,
    observed_group: str | None,
) -> float:
    """Probability that one exchangeable Prize position has this group."""

    if belief.prize_count <= 0:
        raise ValueError("cannot take a Prize card when prize_count is zero")

    group_index = {group: index for index, group in enumerate(belief.groups)}
    if observed_group is not None and observed_group not in group_index:
        raise ValueError("observed_group must be modeled or None")
    observed_index = (
        group_index[observed_group]
        if observed_group is not None
        else None
    )

    probability = 0.0
    for state, mass in belief.masses:
        count = (
            state[observed_index]
            if observed_index is not None
            else belief.prize_count - sum(state)
        )
        probability += mass * count / belief.prize_count
    return probability


def take_observed_random_prize(
    belief: PrizeBelief,
    observed_group: str | None,
) -> PrizeBelief:
    """Condition on an observed Prize identity and remove that Prize card.

    Prize positions are exchangeable in this grouped model. observed_group=None
    means the taken card belongs to the implicit filler category.
    """

    probability = observation_probability(belief, observed_group)
    if probability == 0.0:
        raise ValueError("observation has zero probability under this belief")

    group_index = {group: index for index, group in enumerate(belief.groups)}
    observed_index = (
        group_index[observed_group]
        if observed_group is not None
        else None
    )
    output: dict[tuple[int, ...], float] = {}

    for state, mass in belief.masses:
        count = (
            state[observed_index]
            if observed_index is not None
            else belief.prize_count - sum(state)
        )
        weight = mass * count / belief.prize_count
        if weight == 0.0:
            continue

        next_state = list(state)
        if observed_index is not None:
            next_state[observed_index] -= 1
        key = tuple(next_state)
        output[key] = output.get(key, 0.0) + weight / probability

    return PrizeBelief(
        belief.groups,
        belief.prize_count - 1,
        tuple(sorted(output.items())),
    )


def take_observed_prizes(
    belief: PrizeBelief,
    observed_groups: Iterable[str | None],
) -> PrizeBelief:
    """Apply several observed Prize removals in draw order."""

    current = belief
    for observed_group in observed_groups:
        current = take_observed_random_prize(current, observed_group)
    return current


def exchangeable_prize_count(ledger: IdentityLedger) -> int:
    return sum(
        count
        for _card_class, zone, count in ledger.exchangeable.counts
        if zone == PRIZE
    )


def take_exact_prize_cards(
    ledger: IdentityLedger,
    card_classes: Iterable[str],
) -> IdentityLedger:
    """Move exact underlying Prize card classes into hand."""

    exchangeable = ledger.exchangeable
    for card_class in card_classes:
        exchangeable = exchangeable.move(
            card_class,
            PRIZE,
            HAND,
        )

    next_ledger = IdentityLedger(exchangeable, ledger.instances)
    assert_conserved(ledger, next_ledger)
    return next_ledger


def take_prizes_and_update_belief(
    ledger: IdentityLedger,
    belief: PrizeBelief,
    observations: Iterable[tuple[str, str | None]],
) -> PrizeTakeResult:
    """Advance exact Prize truth and the taker's grouped belief together.

    Each observation is (physical_card_class, observed_belief_group). The caller
    owns the semantic mapping from an exact card class into the research groups.
    """

    rows = tuple(observations)
    if exchangeable_prize_count(ledger) != belief.prize_count:
        raise ValueError(
            "physical exchangeable Prize count must match belief.prize_count"
        )

    next_ledger = take_exact_prize_cards(
        ledger,
        (card_class for card_class, _group in rows),
    )
    next_belief = take_observed_prizes(
        belief,
        (group for _card_class, group in rows),
    )

    if exchangeable_prize_count(next_ledger) != next_belief.prize_count:
        raise AssertionError("physical Prize count and belief diverged")

    return PrizeTakeResult(next_ledger, next_belief)
