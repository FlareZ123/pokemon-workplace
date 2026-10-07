# Dream Ball typed Bench execution

## Question

Can Dream Ball's Prize-origin E-31 Item effect carry the typed search allocator's exact target witness all the way into conserved Bench topology?

Yes for the direct deck-to-Bench search modeled here.

Implementation: `tools/dream_ball_typed_bench_execution.py`  
Regression: `results/dream_ball_typed_bench_execution/reproduce.py`

## Source semantics

The bundled Expanded card pool gives Dream Ball (`swsh7-146`) the special Prize-origin play condition and the effect:

`Search your deck for a Pokémon and put it onto your Bench. Then, shuffle your deck.`

The existing before-hand Prize executor already represents Dream Ball itself as a materialized card in `resolving_trainer` until that secondary search effect has completed.

The Advanced Player's Rulebook defines E-31 as the interval after a previously face-down card is seen and before it enters the hand. This result keeps the search inside that already-modeled timing window.

## Exact target witness

A low-dimensional search result such as "one Pokémon found" is insufficient for state mutation.

The regression gives Dream Ball two exact legal Pokémon targets compiled from database metadata:

- Tapu Lele-GX `sm2-60`, a Basic Pokémon with Retreat Cost 1;
- Pidgeot ex `sv3-164`, a Stage 2 Pokémon evolving from Pidgeotto with Retreat Cost 0.

Both satisfy the same one-unit strategic demand profile `(1,)`, while the typed allocator retains two exact physical witnesses:

- `target_cost=(1, 0, 0)`;
- `target_cost=(0, 1, 0)`.

An Item decoy occupies the third target axis and is rejected as a Dream Ball target even when supplied through a dimensionally valid action created for an Item selector.

## Conserved direct-to-Bench transition

The executor requires Dream Ball's resolving physical ledger and the promotion-pending board to be identical before mutation. Exact Pokémon metadata is loaded from the bundled legal Expanded card pool by `tools/pokemon_board_metadata.py`, which reuses the repository's legality classifier and conservative search-tag compiler.

For the selected exact target it then:

1. validates that exactly one current deck target was selected;
2. validates that the selected target is a Pokémon;
3. uses the shared typed search transition to move that exact exchangeable class into a temporary selected zone;
4. materializes one physical instance only at the boundary where it becomes board topology;
5. binds that instance to a new `BoardPokemon`;
6. keeps Dream Ball itself in `resolving_trainer` until the existing before-hand Item executor confirms the secondary effect is complete;
7. discards the same Dream Ball instance afterward.

The selected Pokémon never enters hand.

## Direct Stage 2 placement

The Pidgeot ex witness demonstrates an important topology distinction.

Dream Ball can put the selected Stage 2 Pokémon directly onto the Bench as a one-card Pokémon stack. The model does not invent Basic or Stage 1 cards underneath it and marks the new Pokémon as ineligible to evolve again that turn.

This is materially different from an ordinary evolution transition even though the final visible card is a Stage 2 Pokémon.

## Rejected states

The regression rejects three ways a graph-style execution could become physically wrong:

- the Bench is full;
- the exact target witness is stale because its selected Pokémon has already left the deck;
- a non-Pokémon exact witness is supplied to Dream Ball.

Per-card-class totals remain conserved through the successful Basic and Stage 2 branches.

## Finding

Typed search allocation and board materialization should meet at the exact target witness.

Dream Ball is a useful boundary case because its searched card skips the hand and immediately acquires board identity. Keeping only the strategic demand vector would lose which Pokémon was selected. Materializing every deck copy earlier would add unnecessary physical identity. The exact target-cost witness provides the bridge between those representations.

## Limits

This result does not model deck order or the post-search shuffle because the surrounding deck-count state is exchangeable.

The metadata adapter covers exact effectively legal Pokémon prints in Expanded-marked sets and deliberately excludes currently banned prints through the shared legality overlay. The regression checks that Medicham V `swsh7-83` is absent.

The executor covers the one-card successful-search branch. Search failure or voluntarily selecting fewer cards should remain an explicit branch of a higher-level Dream Ball action model.

The existing before-hand Item state and the board state still have to be synchronized by their caller after Dream Ball is discarded. A broader unified action transaction could own both views atomically.

This result does not decide the separate unresolved win/loss-precedence question for a player whose final Pokémon was Knocked Out before a Prize-origin Bench-entry effect resolves.
