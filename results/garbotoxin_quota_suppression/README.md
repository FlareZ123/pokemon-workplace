# Garbotoxin suppression as a causal quota overlay

## Question

Can a concrete lock interaction determine whether physical Dual Brains contributes a Supporter quota without directly mutating the base board's Ability state?

Yes, for the verified Garbotoxin / Stealthy Hood / Jamming Tower interaction.

Implementation:

- `tools/garbotoxin_suppression.py`
- `tools/board_action_quota_derivation.py`

Regression: `results/garbotoxin_quota_suppression/reproduce.py`

## Why an overlay

The physical board stores source identity, attachments, and an upstream effective-Ability flag. Garbotoxin is represented as a derived suppression set over that board rather than by permanently flipping the target's base field.

This matters because a lock can disappear. Recomputing an overlay from current sources restores downstream Abilities without reconstructing what their unsuppressed state used to be.

## Verified source family

The bundled Expanded card pool contains four legal Garbotoxin prints with the same relevant wording:

- `bw6-54`
- `bw9-119`
- `bw11-68`
- `xy9-57`

The source is live when the exact Garbodor has a Pokémon Tool attached. The condition checks attachment, not whether that Tool's own effect functions.

## Dual Brains interaction

With Magnezone `bw8-46` in play and one Supporter already used:

- Garbodor without a Tool leaves Dual Brains active, so the limit stays 2;
- opposing Garbotoxin with a Tool suppresses Dual Brains, reducing the live limit to 1;
- Stealthy Hood on Magnezone blocks the opposing Ability effect, restoring limit 2;
- Jamming Tower makes the Hood have no effect, so Garbotoxin suppresses Dual Brains again;
- the Tool on Garbodor remains attached under Jamming Tower, so Garbotoxin's own condition stays satisfied.

A same-side Garbotoxin suppresses the player's other Pokémon even if they hold Stealthy Hood, because Hood protects from the opponent's Abilities. Garbotoxin itself remains exempt from Garbotoxin.

## State layering

The composed path is:

`physical boards -> Garbotoxin suppression overlay -> board quota derivation -> canonical TurnActionBudget`

This leaves several mechanisms distinct:

- physical Tool attachment;
- Tool-effect operation;
- Ability-effect protection;
- Ability suppression;
- quota derivation;
- already-consumed Supporter history.

That distinction is required for the Jamming Tower case, where the Tool is still attached but Hood's text is inactive.

## Scope

This is intentionally one causal lock family, not a complete Ability-suppression engine. Neutralizing Gas, Silent Lab, Alolan Muk, Iron Thorns ex, Garbotoxin-versus-Garbotoxin dependencies, and source-specific target scopes still need a more general resolution model. The result establishes an overlay architecture that can be extended without overwriting base physical state.
