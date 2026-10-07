# Post-damage reaction surface in paper Expanded

## Question

How broad is the current legal card-text surface for effects that explicitly trigger after a Pokemon is damaged by an attack and remain relevant even if that Pokemon is Knocked Out?

Implementation: `tools/damage_reaction_catalog.py`  
Regression: `results/damage_reaction_catalog/reproduce.py`

## Conservative scope

The catalog keeps only text that contains all three signals:

- "is damaged by an attack";
- "even if";
- "Knocked Out".

This deliberately excludes "would be damaged" prevention text and "was damaged during your opponent's last turn" retrospective attack conditions.

The result is a conservative semantic island around the rulebook's post-damage reaction timing.

## Current corpus

The effectively legal English paper-Expanded snapshot contains **89 print-level reaction rows across 40 distinct category/text signatures**.

| Reaction body | Print rows | Distinct signatures |
| --- | ---: | ---: |
| Fixed damage counters on attacker | 50 | 20 |
| Mirror damage as counters | 12 | 5 |
| Special Condition on attacker | 12 | 4 |
| Scaled damage counters | 5 | 3 |
| Draw | 3 | 3 |
| Discard attacker Energy | 2 | 1 |
| Return attacker Energy | 2 | 1 |
| Move attacker Energy | 1 | 1 |
| Discard opponent hand card | 1 | 1 |
| Search | 1 | 1 |

Every row is classified by this current catalog.

## Execution coverage

The `damage_reaction_kernel` implements three counter-placement body families:

- fixed counters;
- counters scaled by an upstream live count;
- counters equal to final damage done.

Those families account for **67 of 89 print rows** and **28 of 40 distinct signatures** in this conservative catalog.

That percentage is body coverage rather than full card legality coverage. Individual cards can add conditions involving Active position, attached Tools or Energy, opponent Pokemon categories, or temporary effects from a prior attack. Those prerequisites still belong to an upstream semantic layer.

## Strategic relevance

The remaining surface shows why the post-damage boundary must stay extensible.

A defender reaching zero remaining HP can still, before the KO check:

- inflict a Special Condition on the attacker;
- remove or move attacker Energy;
- draw or search cards;
- force hand disruption;
- place scaled counter damage.

Those outcomes can alter the same turn's simultaneous KO state, resource state entering the KO trigger window, or the following turn's tactical options.

## Limits

This is a text-family inventory. It does not prove that every selected row uses identical timing semantics beyond the conservative wording family.

The classifier intentionally avoids broad natural-language inference. New wording that does not match one of the recognized consequence forms will enter the `other` bucket and fail the regression's current zero-unclassified expectation, forcing explicit review.
