# Knock Out phase routing and cross-player ordering

## Question

What additional state boundaries are needed after simultaneous Knock Out has been represented as a batch, so a simulator can handle pre-discard recovery effects and the ordering rules that span both players?

Implementation: `tools/knockout_phase_resolution.py`  
Regression: `results/knockout_phase_resolution/reproduce.py`

## Rule-derived phase structure

The Advanced Player's Rulebook separates several steps that should remain distinct in a state engine:

1. effects activated by the Knock Outs are applied before the Knocked Out Pokémon are discarded;
2. all Knocked Out Pokémon are then discarded together;
3. both players take Prize cards from those Knock Outs;
4. if both Active Pokémon were Knocked Out, the player whose turn would be next promotes first.

When several Knock Out-triggered effects activate at the same time, the player whose turn is currently being played chooses their order.

The rulebook's Huntail example gives a concrete reason the pre-discard state must still contain attached cards: Diver's Catch can put all Basic Water Energy attached to the Knocked Out Water Pokémon into hand instead of the discard pile.

## Representation

This result builds on `results/simultaneous_knockout_conservation/` rather than replacing it.

`AttachmentRoute` represents one already-semanticized redirect of a physical attached card from a doomed Pokémon to an off-board zone. `route_pending_attachments()` applies a set of such redirects atomically to the same pending Knock Out snapshot. It updates both:

- the board attachment relation;
- the identity ledger / exchangeable zone count.

The adapter deliberately does not decide which cards satisfy a card-specific condition such as "Basic Water Energy". That classification remains the responsibility of the card-text / typed-semantic layer.

`TwoPlayerKnockOutPhase` then binds one pending batch for each player together with the current-turn and next-turn identities. Two pure ordering functions expose separate rule authorities:

- `choose_knock_out_trigger_order()`: only the current-turn player can choose the global order of simultaneous KO-triggered effects;
- `promotion_choice_order()`: if both sides need a replacement Active, the next-turn player chooses first.

## Regression

Player A's doomed Active has both:

- one Basic Water Energy;
- one Double Colorless Energy.

The regression routes only the Basic Water Energy to hand before disposal, matching the mechanical consequence of a Diver's Catch-like effect after the semantic layer has identified the eligible attachment. The Double Colorless Energy remains attached until batch disposal and then enters discard.

Player B's doomed Active carries a Muscle Band. It is discarded normally.

Both players have a surviving Benched Pokémon, so both need to promote. With A as the current-turn player and B as the next-turn player:

- B cannot choose the KO-trigger order;
- A can choose either exact trigger permutation;
- the promotion-choice order is B, then A.

A second case removes both of B's Pokémon in the same batch. B then has no legal promotion to make, so only A appears in the promotion sequence.

Every card-class total remains invariant through the routing and disposal transitions.

## Findings

A Knock Out replacement effect should redirect a physical card before the ordinary batch-discard sink consumes it. Hard-coding every attachment on a Knocked Out Pokémon to discard loses valid recovery lines.

The global ordering rules also belong above a single-player board kernel. Trigger ordering is controlled by the current-turn player, while simultaneous Active replacement ordering is controlled by the next-turn player. Treating either rule as a property of the individual card controller or of one board gives the wrong authority.

## Limits

This adapter validates routing and ordering mechanics. It does not yet:

- infer card-specific eligibility such as Basic Water Energy from card text;
- execute arbitrary trigger effects;
- move specific Prize cards after Knock Outs;
- represent the temporary between-disposal-and-promotion game state because the existing board kernel requires an Active whenever Pokémon remain;
- resolve win/loss conditions when a player has no Pokémon left;
- model replacement effects that redirect Pokémon stack cards rather than attachments.

A stronger full-game Knock Out state machine should preserve the same phase separation while adding Prize movement and win/loss resolution.
