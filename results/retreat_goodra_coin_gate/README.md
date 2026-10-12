# Goodra's Slimy Sliding: an exact stochastic normal-Retreat gate

## Finding

Goodra from *Chaos Rising* `me4-68` has **Slimy Sliding**, an Ability
that changes an opponent's attempted ordinary Retreat into a coin-flip
action. Heads allows Retreat normally. Tails leaves the Active Pokémon
in place, retains its Retreat Energy, and spends that turn's ordinary
Retreat opportunity. Multiple active copies of Slimy Sliding do not
stack. A zero-cost Retreat still faces the coin flip. Switching through
a card effect is not ordinary Retreat and bypasses Slimy Sliding.

Official printed source:
https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/me04/68/

Official Japanese rulings explain the failed action, free Retreat,
Dashing Pouch and effect-based switching:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%8C%E3%83%A1%E3%83%AB%E3%82%B4%E3%83%B3&regulation_faq_main_item1=all

## Implementation

`tools/retreat_goodra_coin_gate.py` adds a narrow stochastic transition
overlay to the already-tested canonical physical Retreat implementation.
It accepts a legal, deterministic `LegalRetreatAction` from the
`retreat_action_enumerator` and builds outcome branches:

| Outcome | Exact probability | Board move | Energy paid | Retreat quota |
| --- | ---: | --- | --- | --- |
| Heads | 1/2 | Executes selected Retreat | Normal payment/destination | Consumed |
| Tails | 1/2 | No movement | None | Consumed |

With no effective Goodra Ability in the opponent board, there is one
probability-one ordinary Retreat outcome. Source detection uses exact
print ID and card name, across Active and Bench. The existing causal
Ability-lock projection can disable a source. Two copies still cause
one coin flip, consistent with non-stacking printed text.

The tail transition calls the canonical turn budget directly, preserves
the entire physical board including Energy and Tool attachments, and
preserves every zone-count and instance-class entry. It never executes
a partial payment before deciding the coin flip. If a source's Ability
state is causally unresolved, the wrapper raises rather than choosing
an unsupported branch.

## Executable physical examples

The `reproduce.py` fixture starts with an Active Pokémon holding
one Psychic Energy and a Dashing Pouch Tool. It has one Benched Pivot,
and the opponent has two live Goodra with Slimy Sliding.

A cost-one ordinary Retreat to Pivot is executable without Goodra,
and its Dashing Pouch would return the paid Psychic Energy to hand.
With Goodra, the *heads* branch does so; the *tails* branch retains the
original Active, attached Energy, Tool and exact zone/instance data.
The tails branch spends Retreat quota, so no second normal Retreat is
available in the same turn. The companion fixture verifies that the
same coin gate applies to a zero-Energy, zero-cost Retreat; suppressing
the Goodra Ability restores the deterministic route.

An independent `switch_active` mechanical transition succeeds from
the exact same starting board, without consuming the normal Retreat
quota or discarding Energy. The fixture deliberately does not claim
the user has drawn or played any particular Switch card.

## Evidence and scope

- The source regression validates print `me4-68`, the exact Ability
  name, its no-stacking language and its failed-payment rule against
  the bundled English card corpus.
- The physical regression validates probability conservation,
  destination handling, identity conservation, Retreat quota and
  effect-based switching.
- `.github/workflows/validate-retreat-goodra-coin-gate.yml` reruns
  this result alongside existing Retreat transaction and action
  enumeration regressions.

This is a **mechanics regression for a constructed state**. It is not
a complete stochastic Pokémon game engine, tournament meta estimate,
or evidence of Goodra's deck performance. Effects that manipulate the
coin flip, full-game access to Goodra, cards in hand and other opponent
responses remain external. Source effectiveness depends on the caller's
accurate current board and Ability suppression information.

## Strategic consequence

A reachable Retreat line can now have a probability distribution of
continuations with a distinct failure resource cost. A planner that
treats the existence of a legal Retreat action as guaranteed board
movement will overstate escape against Goodra. A switch-based line
can be worth more than an apparently cheap ordinary Retreat, even
when the latter costs zero Energy.
