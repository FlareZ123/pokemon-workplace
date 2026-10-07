# Beginning-of-turn deck loss and draw now form one physical phase

## Question

Can a turn-start resolver enforce the timing rule that an empty deck loses
before any draw transition, while a nonempty deck performs exactly one physical
draw?

Yes.

Implementation: tools/turn_start_phase.py
Regression: results/turn_start_phase/reproduce.py

## Phase order

The phase is:

1. project canonical physical deck emptiness into the existing game-resolution
   deck-out rule;
2. stop immediately if the result is terminal;
3. otherwise perform one physical draw.

Two draw representations are supported.

- An exact materialized deck top uses the exact-top draw transition.
- An unordered deck requires a caller-supplied sampled class, then materializes
  and draws exactly one copy.

Both successful paths end in SearchableDeckPhysicalState.

## Regression

Three states are compared.

### Exact one-card top

The only deck card exists as top-1 in deck_top. The loss check continues, the
card is drawn, physical deck size becomes zero, and the card reaches hand.

### Unordered two-card deck

The caller samples A from A + filler. The game continues and drawn-a reaches
hand, leaving one physical deck card.

### Empty unordered deck

The current-turn player loses during the loss check. The phase returns no
after-draw state and no drawn instance.

No sample information is required for the terminal branch because no draw is
allowed to occur.

## Finding

Turn-start deck-out and turn-start drawing should share one phase boundary.

Separating them into unrelated caller steps makes it possible to draw from a
state that should already be terminal or to declare a loss from a deck whose
only card is represented as an exact top instance.

The phase keeps stochastic sampling outside the mechanics layer while making
the timing relation explicit.

## Limits

This module models only the mandatory beginning-of-turn deck-loss check and one
draw. It does not reset the full turn action budget or process other beginning-
of-turn effects.

A future canonical turn sequence owner can call this phase before exposing
ordinary turn actions.
