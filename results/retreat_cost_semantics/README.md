# Retreat Cost semantics and fixed-delta catalog

## Question

How should a simulator combine Retreat Cost increases, reductions, and effects
that make a Pokemon have no Retreat Cost? How much of the current paper
Expanded card pool can be compiled conservatively from literal fixed-delta
wording?

## Rule-derived algebra

The Advanced Player's Rulebook distinguishes three relevant operations:

- D-11: effects that make a cost more stack with one another;
- D-12: effects that make a cost less stack with one another, and more/less
  effects are calculated together;
- D-13: "has no Retreat Cost" or equivalent nullification takes priority over
  simultaneous more/less effects.

`tools/retreat_cost_semantics.py` therefore represents already-applicable
effects as additive integer deltas plus an explicit no-Retreat-Cost flag.

For base Retreat Cost `b` and applicable deltas `d_i`:

`effective = max(0, b + sum(d_i))`

unless any applicable no-Retreat-Cost effect is active, in which case the
effective cost is zero.

The regression verifies:

- base 3 + Air Balloon (-2) + Galar Mine (+2) + Ariados Big Net (+1) = 4;
- reductions floor at zero;
- an applicable Float Stone-style no-cost effect yields zero even while increase
  and reduction modifiers are also present.

## Conservative fixed-delta compiler

`tools/retreat_cost_effect_catalog.py` scans effectively legal paper Expanded
cards and compiles only literal fixed forms such as:

- `Retreat Cost ... is Colorless more`;
- `Retreat Cost ... is ColorlessColorless more`;
- `Retreat Cost ... is Colorless less`;
- `Retreat Cost ... is ColorlessColorless less`.

A match followed by `for each` is deliberately classified as variable rather
than converted into a constant.

On the current repository card pool and effective-legality overlay, CI run
`37579192191` finds:

- **55 fixed print-effect rows** across **27 distinct texts**;
- 22 Ability rows, 7 attack rows, and 26 rule-text rows;
- 17 rows at -2;
- 13 rows at -1;
- 23 rows at +1;
- 2 rows at +2;
- **2 variable print-effect rows** across 2 distinct texts.

The two variable witnesses are Beldum `sm7-92` and Magnemite `xy8-51`,
whose Retreat Cost reductions depend on matching Benched Pokemon counts.

Named fixed regressions include:

- Air Balloon `me1-166`: -2;
- Galar Mine `swsh2-160`: +2;
- Ariados `sv6-5`, Big Net: +1;
- Hisuian Sneasler `swsh10-93`, Carry and Climb: -2.

## Why this split matters

The algebra answers a mechanical question after effect applicability is known.
The catalog answers a text-compilation question for one safe wording island.

Those are separate problems. Air Balloon's -2 is fixed text, while whether its
Tool effect is currently enabled depends on attachment state and effects such as
Jamming Tower. Ariados's +1 is fixed text, while applicability depends on
source Ability activity, opponent ownership, target position, and Evolution
status. Attack-applied modifiers also have duration state.

A planner should therefore derive applicable modifier instances from board and
effect state, then feed them into the small algebra. It should not infer
applicability from the existence of a matching card in the deck.

## Limits

This result does not yet compile the broad `has no Retreat Cost` family from
card text because those effects contain many different activation predicates.
The algebra supports no-cost modifiers once an upstream semantic layer has
established that they apply.

Variable numeric effects, copied text, errata outside the existing legality
layer, and dynamic holder conditions also remain upstream.

## Reproduction

Run:

`python results/retreat_cost_semantics/reproduce.py`

The script rebuilds the catalog from repository resources, checks the named
witnesses and algebra, and prints the current catalog counts.
