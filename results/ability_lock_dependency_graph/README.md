# Dependency graph for multiple continuous Ability locks

## Question

Can several continuous Ability-lock sources be composed safely once the single-source geometry is known?

Sometimes. If the source-to-source suppression graph is acyclic, the active source set can be derived deterministically from the existing predicates. If the graph contains a directed cycle, this result refuses to guess.

Implementation: `tools/ability_lock_dependency_graph.py`  
Regression: `results/ability_lock_dependency_graph/reproduce.py`

## Graph construction

A source is a candidate when:

- its print belongs to a supported Ability-lock profile;
- its non-suppression activation condition is met, such as Active position, Bench position, or Tool attachment;
- its upstream `abilities_enabled` input is true.

For each candidate source, the single-source geometry computes which physical Pokémon it would suppress. If one of those targets is another candidate source, the model records a directed source-suppression edge.

## Acyclic case

The regression uses Active Wobbuffet / Bide Barricade on one side and Tool-attached Garbodor / Garbotoxin on the other.

Garbodor is Psychic, so Bide Barricade's Psychic exemption prevents Wobbuffet from suppressing Garbotoxin. Garbotoxin does suppress Wobbuffet.

The dependency graph is therefore:

`Garbotoxin -> Bide Barricade`

The resolver can determine that Garbotoxin is active and Wobbuffet is inactive. Ordinary targets suppressed by the active source are then materialized as the final suppression overlay.

This is stronger than unioning all individually legal sources, because inactive lock sources no longer keep suppressing downstream targets.

## Cyclic case

The regression also places Active Galarian Weezing / Neutralizing Gas opposite Active Slaking / Lazy.

Each Ability suppresses the opponent's Pokémon in play. In the single-source predicates:

`Neutralizing Gas -> Lazy`

and

`Lazy -> Neutralizing Gas`

This is a directed cycle. The resolver reports the strongly connected component and returns no active-source set or final suppression overlay.

It does not arbitrarily choose one source, apply both, or invent a simultaneous fixed point.

A later setup-specific result at `results/ability_lock_setup_precedence/` supplies official first-player precedence for a reciprocal two-Active cycle at game setup. This graph remains a history-free snapshot layer, so unrelated cyclic states still remain unresolved here.

## Protection changes the dependency graph

Stealthy Hood on Weezing blocks the opponent-sourced Lazy effect. That removes one edge from the graph, leaving Neutralizing Gas as the active suppressor.

Jamming Tower then blanks Hood's Tool effect. The removed edge returns and the cycle becomes unresolved again without either lock source changing position.

This demonstrates that protection state can alter the dependency topology itself.

## Rules-source caution

A targeted scan of the bundled Advanced Player's Rulebook found general priority rules such as card text overriding basic rules and "can't" taking priority over "do", plus several context-specific simultaneous-effect ordering rules. The scan did not identify a general rule that resolves a cycle where continuous "has no Abilities" effects remove each other's source Abilities.

That absence is not proof that no authoritative ruling exists. It is the reason this implementation marks the state unresolved instead of converting a community convention into simulator law.

## Architectural implication

Multi-lock resolution should be decomposed into:

1. source activation geometry;
2. source-to-target suppression predicates;
3. source dependency graph;
4. dependency resolution;
5. final ordinary-target suppression overlay.

Acyclic graphs can already be executed. Cyclic components are explicit research objects that can later accept authoritative timing/history semantics without rewriting the single-source predicate layer.
