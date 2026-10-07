# Prize-origin Items and hand-scoped Item locks

## Question

Do direct Expanded Item-play prohibition effects automatically block Dream Ball or Greedy Dice when those Items are played in the E-31 before-hand window?

For the direct prohibition wording present in the bundled effectively legal English Expanded card pool, the answer follows the source-zone scope: those effects prohibit Item cards played **from hand**.

Implementation: `tools/item_play_source_scope.py`  
Regression: `results/prize_origin_item_lock_scope/reproduce.py`

## Rule structure

Ordinary Item procedure begins with choosing the Item from hand.

The card-text priority rule allows a card to create an exception to a basic rule.

Dream Ball and Greedy Dice each say they can be played only after being taken as a face-down Prize and before entering hand. E-31 defines that timing point as after the formerly face-down card is seen and before it is put into hand.

The resulting play therefore has a different source zone from ordinary Item play.

## Card-pool audit

The scanner finds **42** effectively legal effect rows in Expanded-marked sets that directly prohibit Item play with "can't play" wording.

Those rows collapse to **15** distinct text variants.

Every one of the 42 rows explicitly scopes the prohibition to Item cards played from the affected player's hand.

Representative sources include:

- Vileplume `xy7-3`, Irritating Pollen;
- Trevenant `xy1-55`, Forest's Curse;
- Seismitoad-EX `xy3-20`, Quaking Punch;
- Budew `sv8pt5-4`, Itchy Pollen.

The audit fails closed if it encounters a direct "can't play ... Item" row whose source-zone wording it cannot recognize.

## Consequence for the E-31 Item family

The before-hand profile catalog identifies exactly two Prize-origin Item-play profiles:

- Dream Ball `swsh7-146`;
- Greedy Dice `xy11-102`.

They are played while the taken card is still in the E-31 before-hand window, represented by `prize_pending` in the state kernel.

A hand-scoped prohibition matches source zone `hand` and does not match source zone `prize_pending`.

This is a mechanically useful distinction for lock modeling. An Item lock edge should carry its prohibited source zone rather than reducing the entire Item action class to one boolean.

## Scope

This result audits direct "can't play" Item prohibitions in the supplied English Expanded pool.

It does not claim that every conceivable effect affecting Items has the same scope. Effects that prevent an Item's effects, alter a card after it is played, or use different wording belong to separate semantic families.

The result also does not imply that Dream Ball or Greedy Dice is always usable. Their own timing conditions still apply, and their effects can have additional legality or usefulness constraints.

## Modeling implication

A lock representation should include at least the action class and the card's source zone.

For ordinary Item play, the source is hand.

For Dream Ball and Greedy Dice in their special Prize-origin timing window, the source is the pending Prize transition.

This adds a source-zone dimension to the existing lock geometry work.
