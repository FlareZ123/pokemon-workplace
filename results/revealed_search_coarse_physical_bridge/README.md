# Exact physical Quick Ball with an intentionally name-coarsened observation

## Question

Can a search simulator physically execute one exact-print revealed search, pay the correct discard cost, resolve a physically sampled post-shuffle deck top, and give two observers different information states, without leaking the actor's selected print identity into a name-only opponent model?

Yes, in the conservative one-target Quick Ball semantic island.

## Execution layers

`tools/revealed_search_coarse_physical_bridge.py` composes the existing physical `execute_hidden_trainer_search_transaction` (whose actor-only observation is checked against the exact materialized print) with `resolve_coarse_revealed_search_for_observers` (whose opponent latent selected target depends on a deliberately coarsened public label).

The two layers use the same pre-action physical state, Prize pool counts, typed search target, and target policy. The exact materialized movement remains the authority for which card moved. Every observer's joint (top, Prize positions, latent selected target) distribution is required to give positive support to the sampled exact world.

A searched target's group must agree with its `exact_print:<ID>` material class. The currently supported fine group labels are therefore print IDs. This explicitly narrows the semantic island; other identity namespaces need an equivalent trusted mapping.

## Controlled physical Quick Ball witness

The six-card pre-search hidden pool has A, two distinct legal Pikachu printings (old `xy1-42`, new `swsh7-49`), and three fillers. Two Prizes are dealt. The exact world sets A and a filler in Prizes, and contains both Pikachu prints and two fillers in deck. The synthetic policy chooses the old print in this world.

The player also has a Quick Ball and one fodder card in hand. `swsh1-179` Quick Ball's profile is compiled from the bundled card text. A typed Basic Pokémon selection takes exactly the old Pikachu.

The physical sequence is:

1. Quick Ball hand -> resolving -> discard; fodder hand -> discard.
2. Old Pikachu `exact_print:xy1-42` deck -> known hand instance, publicly displayed name Pikachu.
3. New Pikachu `exact_print:swsh7-49` becomes the sampled exact shuffled deck top.
4. All materialized and aggregate card-class totals remain conserved, and the Supporter budget remains available.

The actor's exact K1 belief assigns P(top=new print)=1/3 and P(A Prized)=1. The opponent's intentionally name-coarsened observation gives:

- P(selected old print)=1/2;
- P(selected new print)=1/2;
- P(A Prized)=5/14;
- P(top=A)=3/14.

Later identifying the selected old print yields P(A Prized)=4/7 and P(top=A)=1/7; identifying the new print yields 1/7 and 2/7. These match the independent 84-branch enumeration from `results/revealed_print_information/`.

The scenario also rejects a caller claiming that the searched card publicly appeared as Porygon when the materialized target is Pikachu.

## Modeling scope

In actual play, a player revealing a card normally shows the physical printing. The coarsened channel is a model-selection experiment, useful for studying loss of information when a card database or opponent policy compresses revealed targets to deck-building names.

The bridge intentionally delegates physical search to the actor-only existing transaction and emits observer-relative latent target beliefs as a separate result. It has not been generalized to arbitrary multiple revealed targets, unconstrained card semantics, heterogeneous observer visibility, private searches, or all card-fingerprint namespaces. If the opponent really observes the print, the print-aware original bridge should be used instead of the coarsened channel.

## Reproduction and validation

- Adapter: `tools/revealed_search_coarse_physical_bridge.py`.
- Coarse Bayesian kernel: `tools/revealed_target_coarsening.py`.
- Physical exact-search kernel: `tools/trainer_search_hidden_state_bridge.py`.
- Regression: `results/revealed_search_coarse_physical_bridge/reproduce.py`.
- CI: `.github/workflows/validate-revealed-search-coarse-physical-bridge.yml`, run [37989316792](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37989316792), passed.

## Next research

A broader observer layer should allow each observer's *actual* observation channel to be computed from the public physical event, preserving fine classes where the player can visually distinguish them and using latent-state mixtures only when a declared abstraction merges otherwise distinct prints. In a real competitive turn, the next task is to attach legal counter-actions to these posterior states to measure decision-value rather than entropy alone.
