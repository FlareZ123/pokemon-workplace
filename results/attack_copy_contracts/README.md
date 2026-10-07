# Typed execution contracts for the Expanded attack-copy family

## Question

Can the current attack-copy findings be compiled into one auditable contract layer that separates static reachability from execution requirements?

Yes. The current legal Expanded snapshot contains 30 distinct attack-copy signatures. A contract compiler now attaches source geometry, filters, recursion hazards, and the extra execution phases discovered by the companion analyses.

Implementation: `tools/attack_copy_contracts.py`  
Regression: `results/attack_copy_contracts/reproduce.py`

## Inventory

The compiler joins the existing copy-signature catalog with the execution-phase classifier.

Of the **30** distinct signatures:

- **24** have no currently recognized non-tail execution phase;
- **6** require at least one extra phase beyond source selection plus nested body execution.

The six are:

| Attack | Extra semantic requirement |
| --- | --- |
| Copy Anything | selected-attack Energy gate |
| Imittack | selected-attack Energy gate |
| Hypnotic Reign | selected hand source is discarded before body |
| Seek Inspiration | top card is discarded before eligibility and body |
| Haughty Order | outer post-copy continuation |
| Trickster-GX | outer GX-use resource rule |

Across those signatures the compiler records two selected-Energy gates, one selected-source commit, one preselection source commit, one post-copy continuation, and one outer GX-use rule.

## Why this matters

The static composition graph intentionally answers an existential question: can one copy signature select another under some compatible state?

An executable planner needs more information. The same pairwise edge may additionally require:

- a particular live source zone;
- an exact physical source instance;
- a non-GX predicate;
- enough Energy on the copying Pokémon;
- a source-zone mutation before nested execution;
- a player-global GX-use budget;
- a return to outer text after the selected body;
- cycle-aware execution state.

The contract layer keeps those facts adjacent to the same signature instead of asking later planners to recover them from raw card text.

## Simple-tail classification is deliberately narrow

The 24 currently simple-tail signatures are only simple relative to the semantic families recognized here.

They can still depend on dynamic source availability, hidden information, board positions, optional choices, matchup state, or recursive copy structure. The label therefore means:

`no extra phase currently identified by this compiler`

It does not mean strategically simple or universally executable.

## Architectural synthesis

A useful attack-copy pipeline now has four separable layers:

1. **catalog**: identify legal copy signatures and source classes;
2. **composition graph**: establish existential pairwise compatibility and source-variable correlation;
3. **execution contract**: preserve gates, physical source commitments, global resources, and continuations;
4. **copy kernel**: execute a concrete nested line against typed state.

This mirrors the repository's broader methodological theme that access edges are weaker than executable state transitions.

## Limitations

The contract compiler is text-pattern based and intentionally conservative. New wording can add semantic categories.

It also does not yet compile full attack damage/effect semantics, complete hidden-information procedures, dynamic attack-cost modification, or every global resource. Those can be layered onto the contract without collapsing the distinctions already identified.
