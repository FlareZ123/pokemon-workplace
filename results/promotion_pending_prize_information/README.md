# Prize-before-promotion physical state

## Question

Can the post-Knock-Out state commit replacement Active choices before Prize cards have been physically taken and observed?

The rule sequence used here says no. The Advanced Player's Rulebook orders Knock Out resolution so that Knocked Out Pokémon are discarded, Prize cards are taken, and only then are replacement Active choices made when both Active Pokémon were Knocked Out. E-31 adds a further timing boundary for a face-down Prize: its identity is seen before it reaches hand, and a before-hand effect can resolve in that interval.

Implementation: `tools/promotion_pending_conservation.py`  
Regression: `results/promotion_pending_prize_information/reproduce.py`

## Representation gap

The existing ordinary `BoardState` requires an `active_id` that identifies a Pokémon still in play. That is correct for an ordinary stable board and too strong for the middle of Knock Out resolution.

The earlier `cross_player_knockout_resolution` adapter therefore records replacement choices while the Knocked Out Active cards are still physically present in `PendingKnockOutBatch`, then disposes those cards after both choices are known.

This loses a rules-visible information boundary. A player can receive and privately identify a face-down Prize before choosing the replacement Active.

## Promotion-pending physical state

`PromotionPendingState` represents the state after physical Knock Out disposal.

It keeps the canonical `IdentityLedger`, every surviving physical Pokémon object, board metadata needed to reconstruct an ordinary `BoardState`, and `active_id=None` when the prior Active was Knocked Out and survivors await a replacement choice.

The state validates that every surviving evolution-stack card and attachment still agrees with the same identity ledger. Knocked Out stack cards and attachments are dematerialized into their destination zone before this state is constructed.

This creates a material state that the ordinary board model could not express: surviving former Bench Pokémon exist while no replacement Active has yet been selected.

## Prize sequencing gate

`PostKnockOutPromotionContext` adds a small phase machine:

`PRIZES -> PROMOTION`

or

`PRIZES -> TERMINAL`

The promotion phase cannot open while any exact or exchangeable card remains in the `prize_pending` zone. The caller also supplies whether the game continues after the relevant terminal-state evaluation. The module delegates win/loss authority to the existing game-resolution layer.

Once promotion opens, the player whose turn would be next chooses first when both players require a replacement. That first choice mutates the visible state before the second player chooses.

## Canonical-ledger composition

The regression uses one ledger for Player B's board cards, top-deck card, and physical Prize card.

The sequence is:

1. both Active Pokémon are prepared as Knocked Out;
2. both Knocked Out Active cards are physically removed;
3. B still has two surviving former Bench Pokémon and no Active;
4. B's face-down Prize moves into `prize_pending`;
5. B privately learns that the Prize is `Switch`;
6. promotion remains blocked while that card is pending;
7. the same physical `Switch` instance enters B's hand;
8. the Prize phase closes after a caller-supplied continuing-game result;
9. B chooses a replacement Active using the newly observed information;
10. A then chooses after B's visible promotion.

Card-class totals remain conserved from the initial state through the final ordinary board states.

## Authoritative full-Bench counterexample

The Japanese official Pokémon Card Game Expanded Q&A supplies a concrete sequencing witness.

It asks about a state where the player has five Benched Pokémon and a Great Tusk ex at 50 remaining HP. Great Tusk ex uses Gigant Tusk, Knocks Out the opponent's Active, and is also Knocked Out. The Prize taken is Chansey with Lucky Bonus. The official answer says Lucky Bonus cannot be used.

Source: https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%A9%E3%83%83%E3%82%AD%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%8A%E3%82%B9&regulation_faq_main_item1=BW

This distinguishes the phase order mechanically. Before replacement Active selection, all five surviving Pokémon still occupy the Bench, so Lucky Bonus has no open Bench slot. If promotion had already occurred, one of those five Pokémon would occupy the Active Spot and the Bench would have one open slot.

The regression mirrors that geometry: immediately after Active disposal, `bench_occupancy == 5` and `open_bench_slots == 0`; after the later promotion, occupancy falls to four and one slot opens. The later slot does not retroactively make Lucky Bonus usable.

## Information-value witness

The regression includes a deliberately small decision illustration.

Suppose the hidden Prize is equally likely to be `Switch` or `Other`, and each observation favors a different one of two replacement choices.

A fixed promotion committed before the Prize is observed can match the favorable choice in one half of states:

`best fixed utility = 50%`

A state-contingent promotion after the Prize observation can choose correctly in both states:

`post-observation utility = 100%`

These percentages are values of the toy decision objective, not match win rates. Their role is to prove that the sequencing difference can have decision value even when all card access and board geometry are otherwise unchanged.

## Finding

Replacement-Active choice is an information-sensitive phase boundary.

A simulator that requires an Active at every intermediate instant can retain the Knocked Out Active too long or invent the replacement Active too early. An explicit promotion-pending state avoids those errors.

The same physical ledger can span board disposal and Prize observation. This lets hidden-zone information affect the later policy while preserving exact card conservation.

## Scope

This result does not decide which Prize cards are awarded, which Prize positions a player selects, or how before-hand card text is compiled. Those semantics remain upstream.

It does not claim a universal answer for the edge case where a loss condition might arise during the Knock Out process and a before-hand Prize effect could later put a Pokémon into play. The regression keeps surviving Pokémon on both sides, so the game is continuing throughout the tested interval.

It also leaves turn-budget reset timing to the existing turn-sequence work.

## Relationship to earlier work

This fills the promotion-pending physical-state gap identified in `results/README.md` and composes directly with:

- `simultaneous_knockout_conservation`;
- `cross_player_knockout_resolution`;
- `post_knockout_game_resolution`;
- `prize_pending_take`;
- `observer_top_prize_beliefs`;
- `top_prize_physical_bridge`.

The older cross-player adapter remains useful as a narrow ordering witness. The stronger representation here places that ordering after physical disposal and the Prize timing window.
