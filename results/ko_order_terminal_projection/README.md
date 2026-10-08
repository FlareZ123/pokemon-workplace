# Exchangeable end states of ordered Knock Out effects

## Research question

Can two distinct physical-instance destination vectors produce the same final conserved game state once knocked-out Pokémon and attached cards have left play?

**Yes.** `tools/ko_order_terminal_projection.py` composes the exact effect-order outcome-space solver with the existing `knockout_zone_routing.discard_pending_with_zone_routes` transition. It groups results by equality of the *complete* `StackBoardMaterialState`: remaining board, surviving materialized card identities, and exchangeable card-class zone counts.

This builds on `results/ko_order_outcome_space/`, which counts distinct per-instance assignments under supplied precedence constraints. The new projection identifies when two such assignments are strategically equivalent under the repository's materialization model.

## Reproducible witnesses

The integration test imports the existing conserved Honedge -> Doublade -> Aegislash Knock Out board from `results/knockout_redirection_routes/reproduce.py`, retaining two Basic Water Energy, one Double Colorless Energy, one Muscle Band, and a surviving Bidoof.

First, two already-defined effect signatures, return-to-hand and Lost City-like redirection, yield two different physical terminal states. Each is cross-checked against the existing fixed-order executor and against the original physical card-class totals.

Next, an *abstract* three-program fixture adds recovery of both Water Energy cards. It reproduces all four instance-level physical outcomes across six unrestricted orders from the parent result, and all four stay distinct at the exchangeable terminal-state level.

The new counterexample uses two **equivalent copies of Basic Water Energy**, both attached to the KO'd Pokémon:

- Program A explicitly sends water-1 to hand and water-2 to discard.
- Program B explicitly sends water-1 to discard and water-2 to hand.

A-first and B-first produce two distinct **instance-level** route vectors. The physical KO executor dematerializes cards once their board relations end. Both ordered outcomes then have the same conserved terminal representation: exactly one Basic Water Energy in hand, exactly one in discard, and identical remaining board and other zones.

Thus **two instance-different outcomes collapse to one exchangeable endpoint**, with exact order count two. This demonstrates a further optimization of state-space size that remains sound only when the instance histories no longer influence future legal actions.

## Methods and limitations

For every destination-vector outcome, the adapter independently executes the existing KO disposal transition from the same pending pre-disposal batch, refuses invalid destinations/promotions, and groups equal final states while summing exact order multiplicities. Witness orders are retained per instance-route class.

The `reproduce.py` harness also checks conservation, promotion, no-redirection defaults, and precedence-restricted outcomes. The underlying first-assignment semantics and the order-count exactness are described in the parent result.

The two competing Water-routing effects are deliberately *synthetic input programs*. The test establishes a representation-level equivalence theorem rather than asserting an actual pair of cards generates precisely those effects in the same game. Effect activation, real card-specific predicates, ordering chooser authority, and outcome utility remain upstream. Exchangeable aggregation is unsafe while per-copy attached relationships, identity-specific history, or player-visible distinctions remain relevant.
