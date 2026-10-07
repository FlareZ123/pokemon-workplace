# Dependent two-sided position effects

## Question

How should a planner represent moves such as Rapid Spin that first switch the attacking Pokémon and only afterward switch the opponent's Active Pokémon?

Implementation: `tools/compound_position_effects.py`  
Regression: `results/compound_position_effects/reproduce.py`

## Rules basis

The Advanced Player's Rulebook treats “Do A. If you do, do B” and the relevant “Then” construction as conditional sequencing. The second part is performed when at least part of the first part occurred. If the first part cannot be done at all, the second part is not performed.

The movement rules also preserve the earlier geometry result: the first self-switch moves the attacking Active object; the forced opposing switch applies to the opponent's current Active, and the opponent chooses the replacement.

## Compiled family

A conservative literal compiler finds **19 legal clean-text profiles across 10 Pokémon names**.

- 12 use an explicit `If you do` connector.
- 7 use the older `Then` wording.

Representative profiles include Baltoy `sv3-94` / Rapid Spin and Blastoise-EX `xy12-21` / Rapid Spin.

Two otherwise recognizable records are deliberately excluded because their bundled English text contains apparent typos:

- Blastoise-EX `xyp-XY122`: “The,” where parallel prints say “Then,”;
- Palkia `me55-20`: “oppoennt”.

The compiler does not silently repair those records without a stronger semantic source.

## Execution result

The executor resolves the two movement clauses in printed order.

When both players have a legal replacement, both switches occur.

When the attacking player has no Benched Pokémon, the first switch cannot occur and the dependent opponent switch is skipped. The same suppression occurs if an upstream effect-immunity overlay blocks the first movement target.

When the first switch succeeds and the opponent has no Benched Pokémon, the first movement remains completed and the second movement fails. Blocking effects on the opponent's Active produces the same first-only result.

This creates an asymmetric dependency:

`first fails -> no second`

`first succeeds + second fails -> keep first`

That asymmetry is strategically relevant. A graph that represents Rapid Spin as two independent movement edges can invent an illegal opponent-switch line when the attacker has no pivot, or erase a legal self-pivot line when the opponent cannot move.

## Scope

The model covers only four exact clean-text families whose movement body is otherwise semantically isolated. Attack damage is recorded but resolved elsewhere. Energy payment, attack permission, Knock Out timing, and other attack-body effects remain upstream or in their existing kernels.

## Reproduction

Run `python results/compound_position_effects/reproduce.py`.
