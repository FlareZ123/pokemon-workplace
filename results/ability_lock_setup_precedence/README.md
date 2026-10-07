# Setup precedence for mutually suppressing continuous Abilities

## Question

Does a physical board snapshot determine the outcome when both starting Active
Pokemon have continuous Abilities that suppress each other?

No. Official Japanese Pokemon Card Q&A supplies an additional setup-order fact:
the first player's Ability is applied first.

## Official evidence

The official Q&A asks about a game beginning with the first player's Active
Empoleon V using **Emperor's Eyes** and the second player's Active Wobbuffet
using **Bide Barricade**. Its answer says the first player's Ability works first,
so Emperor's Eyes removes Bide Barricade.

Official Q&A search page:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%81%8C%E3%81%BE%E3%82%93%E3%81%AE%E3%81%8B%E3%81%B9&page=3&regulation=all&regulation_faq_main_item1=all

A parallel official setup ruling for Empoleon V and Klefki's Mischievous Lock
uses the same first-player priority principle.

A separate official Q&A involving Garbotoxin and Ting-Lu ex's Cursed Land also
shows that an already-functioning suppressor can prevent a later suppression
condition from becoming effective. That supports retaining causal history for
midgame continuous-effect changes rather than deriving every state from an
unordered fixed point.

## Implementation

`tools/ability_lock_setup_precedence.py` wraps the existing dependency graph.

It only resolves a narrow cyclic shape:

- exactly two candidate suppression sources;
- opposite owners;
- reciprocal source-suppression edges;
- both sources are Active-dependent Ability locks;
- the caller supplies which owner is the first player.

The first-player-owned source becomes the active source and its ordinary target
suppression is materialized through the existing single-source geometry.

All other cyclic dependency shapes remain unresolved.

The source-profile layer now includes all four bundled Expanded Empoleon V
prints for Emperor's Eyes. Its target selector is opponent Basic Pokemon, with
Rule Box Pokemon excluded.

## Regression

`reproduce.py` uses Empoleon V `swsh5-40` versus Wobbuffet `xy4-36`.

The timeless dependency graph contains the reciprocal cycle:

`Emperor's Eyes -> Bide Barricade`

`Bide Barricade -> Emperor's Eyes`

With the player marked as first player, Empoleon V remains active and Wobbuffet
is suppressed. With the opponent marked as first player on the identical board,
Wobbuffet remains active and Empoleon V is suppressed.

This proves that physical board state alone is insufficient for this setup
interaction. Turn-order precedence is mechanically relevant state.

## Scope and limitations

This result does not claim a general solver for arbitrary continuous-effect
cycles. The official setup ruling supplies a precise precedence rule for this
two-Active starting-game case. Dynamic midgame changes, larger strongly
connected components, and other continuous-effect families still require
event-history or additional authoritative timing evidence.
