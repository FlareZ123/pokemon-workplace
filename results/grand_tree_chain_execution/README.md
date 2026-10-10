# Grand Tree Stage 1 and Stage 2 share one Stadium activation

## Question

Grand Tree (`sv7-136`) is an ACE SPEC Stadium with a voluntary effect
usable once during each player's turn. It allows a Basic Pokémon to become
Stage 1, then permits the same Pokémon to become Stage 2 if the first stage
evolved through this effect. Must a planner pay two in-play Stadium activations
to perform the two evolutions? Does the normal no-same-turn-further-evolution
rule forbid the second step?

## Finding

No. The Stadium text specifies a **single effect** with a conditional Stage 2
continuation. The Advanced Player's Rulebook B-04 differentiates activation of
an already-in-play Stadium from playing another Stadium card. Rule C-12
explicitly allows effect-based evolution notwithstanding ordinary evolution
waiting periods, subject to the card's own restrictions.

Grand Tree itself excludes evolving a Basic on the first turn or evolving a
Basic that entered play this turn. Its restriction applies to the eligible
**Basic selected for the first step**. If the Stage 1 is produced by Grand
Tree, the Stage 2 continuation is explicitly allowed in that same resolution.

Therefore a state transition with the following source and target identities
is mechanically supported:

`Grand Tree effect (one instance use) -> Bulbasaur -> Ivysaur -> Venusaur`

The exact print witnesses in the bundled database are:

- Grand Tree: `sv7-136`
- Bulbasaur: `bw5-1`
- Ivysaur: `bw5-2`
- Venusaur: `bw5-3`

All three Pokémon records form the ordinary Basic / Stage 1 / Stage 2
evolution chain, and Grand Tree is inside the defined Expanded era.

## Implementation

`tools/grand_tree_chain_execution.py` implements
`execute_grand_tree_chain()`, composing the existing source gate, C-12
effect evolution executor, board stack identity, and Stadium instance-use
kernel.

The first evolution validates source availability, basic eligibility, turn
timing, and named evolution chain, marking the Stadium instance once.
The optional second evolution is resolved within the already-authorized
effect and needs no additional Stadium activation. It explicitly bypasses
the first stage's new `evolution_eligible=False` flag, which belongs to
ordinary entry-turn evolution timing.

A missing Stage 2 target is represented by the optional argument
`stage2=None`, so Grand Tree can end after producing Stage 1. The caller
receives only the final immutable state. An invalid proposed Stage 2
does not commit the staged first evolution or consume the caller's use
counter.

## Regression

`python results/grand_tree_chain_execution/reproduce.py`

Checks the one-activation double evolution, permitted single evolution,
preservation of Stadium-play quota already spent, same-instance repeated-use
rejection, first-turn and newly played Basic bans, physical stack identity,
and rollback of rejected second-stage selection.

## Scope and limits

This is an executable *card-semantic witness*, conditional on the selected
Stage 1 and Stage 2 being reachable in the deck and legal in the decklist.
The code does not yet model deck search, unknown Prize placement, final deck
shuffle, adversarial locks, or conservation of the actual evolution cards
across deck/hand/board zones. It assumes canonical card metadata has
already established the selected candidates' true evolutionary stages.

The code treats an explicitly supplied invalid Stage 2 candidate as an
invalid proposed transaction. In actual play, the Stage 2 search is optional:
when no Stage 2 is available, the Stage 1-only line remains legal.

## Confidence

High for rule-text ordering and the composite source-use/target-timing
boundary, conditional on the stated card-availability assumptions.
