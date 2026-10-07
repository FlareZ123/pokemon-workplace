# Board-derived continuous source-scoped restrictions

## Question

The continuous restriction evaluator accepts an `ability_enabled` flag and other
geometry fields. Those fields are useful as a semantic boundary, but a live
simulator should not ask callers to reconstruct them manually when canonical
board objects and causal Ability-lock state already exist.

Implementation: `tools/board_derived_continuous_restrictions.py`

Regression: `results/board_derived_continuous_restrictions/reproduce.py`

## Bridge

The bridge derives each continuous restriction source from exact in-play
`BoardPokemon` objects:

- source presence comes from membership in the canonical board;
- Active Spot state comes from `BoardState.active_id`;
- Tool attachment comes from the physical attached Tool;
- Stadium presence comes from the current Stadium input;
- relative Pokémon counts come from the two canonical boards;
- effective Ability state is the card's base `abilities_enabled` state combined
  with the resolved causal Ability-lock suppression overlay.

The causal lock state remains the authority for precedence. The bridge validates
that its source graph and materialized suppression targets still match the
supplied boards and Stadium. An unresolved suppression cycle is rejected rather
than guessed.

## Regression witnesses

An opposing Tool-attached Garbodor suppresses Vileplume's Irritating Pollen, so
the derived Vileplume source exists but is inactive. Stealthy Hood on Vileplume
blocks that opposing Ability effect and restores the Item lock. Adding Jamming
Tower makes the old suppression overlay stale; after the causal lock state is
recomputed, Garbotoxin suppresses Vileplume again while the physical Tool remains
attached.

The regression also derives Team Rocket's Arbok's Active-Spot requirement,
Genesect's Tool-attached requirement, Barbaracle's Stadium requirement, and
Omastar's relative Pokémon-count requirement directly from board state.

A history-free Empoleon V / Wobbuffet reciprocal Ability-lock cycle is rejected
while unresolved. The same board is accepted once the verified setup
first-player precedence resolver supplies a resolved causal state.

## Finding

Continuous hand-denial permissions can now consume the same canonical physical
board and causal Ability-suppression overlay used elsewhere in the repository.
Caller-supplied lock booleans are no longer required at this integration
boundary.

This also makes stale-state failure explicit. Moving a source, changing a
Stadium, changing Tool protection, or otherwise changing the Ability-lock graph
requires the causal lock state to be advanced or recomputed before continuous
restriction permissions are derived.
