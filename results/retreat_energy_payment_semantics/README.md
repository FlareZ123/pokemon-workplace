# Retreat Energy payment semantics

## Question

The shared board-position kernel required Retreat Cost payments to be a
minimal sufficient subset of attached Energy cards. Is that restriction
supported by the rules?

## Finding

No. That restriction rejects an explicitly legal official ruling.

The official Japanese Pokemon Card Q&A for Dashing Pouch asks about a Pokemon
with Retreat Cost 2, two Double Colorless Energy cards attached, and Dashing
Pouch attached. The answer says the player may return both Double Colorless
Energy cards to hand and retreat.

Official search page:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%80%E3%83%83%E3%82%B7%E3%83%A5%E3%83%9D%E3%83%BC%E3%83%81

That state provides four Energy units across two physical cards for a numeric
Retreat Cost of two. The old `_minimal_payment()` predicate rejected it
because either DCE alone still supplied enough Energy.

Additional official Q&A supports the same physical-card versus Energy-unit
distinction:

- FAQ 9597 permits a two-Energy discard to choose one Basic Energy plus one
  Double Colorless Energy, even though those cards jointly provide three
  Energy units.
- FAQ 8814 permits a one-Energy discard to select a Double Colorless Energy,
  causing both Energy units to leave play.
- The Advanced Player's Rulebook Ignition Energy ruling says one multi-unit
  Energy card can count as three Energy for a three-Energy discard and may
  also be selected for a one-Energy discard.

## Corrected conservative predicate

For the ordinary numeric Retreat Cost represented by
`BoardPokemon.retreat_cost`, the kernel accepts an exact selected-card witness
when:

1. Retreat Cost 0 selects no Energy cards.
2. A positive cost selects at least one physical Energy card.
3. Every selected card currently provides at least one Energy unit.
4. The number of selected physical Energy cards is no greater than the numeric
   Retreat Cost.
5. The selected cards jointly provide at least the numeric Retreat Cost.

This accepts the directly witnessed two-DCE case while still rejecting an
obvious extra-card payment such as three one-unit Basic Energy cards for a
Retreat Cost of two.

The physical-card-count bound is a conservative formalization of the basic rule
that the player discards the amount of Energy shown in the Retreat Cost. The
Dashing Pouch ruling directly falsifies minimal sufficiency, but it does not
enumerate every possible legacy multi-unit provider interaction.

## Regression

`results/retreat_energy_payment_semantics/reproduce.py` checks:

- one DCE pays Retreat Cost 2;
- two DCE cards can both pay Retreat Cost 2;
- DCE plus one one-unit Energy can pay Retreat Cost 2;
- one DCE can pay Retreat Cost 1;
- three one-unit Energy cards cannot all be selected for Retreat Cost 2;
- a selected Energy card that currently provides zero Energy cannot be added
  to an otherwise sufficient payment;
- free retreat selects no Energy.

The existing board-position regression is also updated so its
DCE-plus-Lightning witness is accepted.

## Strategic implication

Retreat payment can remain a resource-allocation decision after the numeric
cost is already satisfiable. Dashing Pouch can make a larger legal payment
return more physical Energy cards to hand. Other destination replacements can
likewise make two legal payment witnesses produce different future resources.

A planner should therefore preserve the exact Retreat Cost payment witness
through execution instead of canonicalizing immediately to a minimum-card
payment.
