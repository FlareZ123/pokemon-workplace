# Knock Out zone routing and recovery

## Question

Can the Knock Out conservation layer support triggered effects that send removed
physical cards somewhere other than the discard pile?

Implementation: `tools/knockout_zone_routing.py`  
Regression: `results/knockout_zone_routing/reproduce.py`

## Concrete card basis

Expanded-legal `sv10-55` Huntail has Diver's Catch:

When one of its player's Water Pokémon is Knocked Out by damage from an
opponent's attack, the player may put all Basic Water Energy attached to that
Pokémon into hand instead of the discard pile.

This effect occurs in the rulebook's Knock Out trigger window before the normal
step that discards the Knocked Out Pokémon and its attached cards.

## Representation

The existing `PendingKnockOutBatch` is the trigger-phase snapshot. Its board
still contains the Knocked Out Pokémon and all physical attachments.

After card-specific trigger logic resolves, `discard_pending_with_zone_routes()`
accepts a mapping from removed physical `instance_id` to a relation-free
destination zone. Instances without an override use the normal `discard`
destination.

Every removed card then:

1. leaves its board relation;
2. moves to its resolved destination;
3. dematerializes into the exchangeable count for that card class and zone.

Per-card-class totals remain invariant.

## Regression

The regression uses a Water Active with:

- two materialized Basic Water Energy cards;
- one materialized Double Colorless Energy;
- a surviving Benched Bidoof.

The Active is prepared as Knocked Out. During the pending trigger phase all three
Energy cards are still attached and inspectable.

A Huntail-like resolved route sends the two Basic Water Energy instances to hand.
The Double Colorless Energy has no override, so normal Knock Out disposal sends
it to discard.

After disposal:

- Basic Water Energy hand count is 2;
- Double Colorless Energy discard count is 1;
- the Knocked Out Pokémon card is in discard;
- the promoted Bidoof is the only materialized in-play instance;
- all card-class totals exactly match the initial state.

The adapter rejects a route back to `attached` or `in_play`, because this
specific disposal layer dematerializes cards after they leave the Knocked Out
board object.

## Finding

"Knock Out" does not imply one fixed destination for every physical card being
removed.

The conservation invariant should own copy counts, while trigger/effect semantics
choose the destination zone. Hardcoding all KO members to discard loses legal
recovery lines and makes later state probabilities wrong.

## Limits

The adapter consumes already-resolved destination choices. It does not determine
whether Diver's Catch or another trigger is active, whether an Energy is Basic
Water, or whether the player chooses to use an optional effect.

Effects that move a removed card directly into another board relation require a
different transition because this adapter deliberately dematerializes all routed
cards. Cross-player KO triggers and competing replacement effects are also open.
