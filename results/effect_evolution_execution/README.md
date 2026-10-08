# C-12 evolution timing reaches physical execution

## Question

Can the rulebook distinction between ordinary evolution and effect-based evolution be carried into the repository's conserved physical Pokémon state without weakening evolution-chain checks or source-action legality?

## Result

Yes. tools/effect_evolution_execution.py adds a narrow execution bridge over the existing board_position_state and IdentityLedger layers.

The bridge treats the two ordinary evolution timing gates separately:

- BoardState.evolution_allowed represents the player's ordinary first-turn evolution gate;
- BoardPokemon.evolution_eligible represents the target Pokémon's ordinary entry-turn gate.

For a C-12 effect, either gate may be bypassed when the compiled card policy is c12_default_permitted or explicit_permitted. A card-text blocked policy still enforces that gate. Source-action legality stays external through source_available, so the evolution rule cannot accidentally legalize an attack, Supporter, Ability, or other source action that is unavailable.

## Regression cases

The reproducer checks five boundaries with actual compiled card profiles:

- ordinary evolution fails on the player's first turn;
- Eevee Energy Evolution (sm1-101) succeeds through C-12 on the first turn even though its text has no explicit first-turn sentence;
- Salvatore (sv5-160) succeeds only when the caller marks its Supporter source available, preserving the first-player Supporter restriction;
- Phantump Spiteful Evolution (me4-38) fails on the player's first turn yet succeeds on a later turn when Phantump itself entered play that turn, because its first-turn and entry-turn policies differ;
- Rare Candy (sv1-191) remains blocked on both timing axes.

The regression then materializes an Eevee and a Vaporeon as physical card instances. Vaporeon is moved from the exchangeable hand count into the same persistent Pokémon object's evolution stack. The identity ledger and board stack agree after the transition, and total card-class counts remain conserved.

A failed evolution-chain match returns no transition. Since the staged ledger is immutable and is returned only after a successful board transition, the caller's ledger remains unchanged on failure.

## Modeling consequence

The repository can now distinguish three questions at execution time:

1. Is the source action legal in the current state?
2. Does the effect's first-turn or entry-turn policy permit bypassing the corresponding ordinary evolution gate?
3. Does the physical Evolution card actually evolve from the current top Pokémon card?

This prevents a coarse can_evolve flag from rejecting legal C-12 lines. It also prevents C-12 from granting permissions that belong to the source action.

## Scope and limitations

The executor is a mechanics adapter for already-compiled direct-evolution effects. It does not search the deck, pay attack costs, consume Supporter bandwidth, resolve locks, choose targets, or infer source legality from card text. Those responsibilities remain in their existing layers.

The bridge also assumes the caller supplies the resulting Retreat Cost and the exact physical Evolution card. More complete card-semantic execution would derive those values from canonical card metadata.

## Reproduction

    python results/effect_evolution_execution/reproduce.py

## Confidence

High for the represented timing and conservation boundaries. The adapter delegates board-stack validation and physical-card conservation to existing repository authorities rather than creating another identity model.
