# Conservative card-grounded board semantics for simple attacks

## Question

Can the attack-copy execution stack obtain board damage, simple damage-counter
effects, and extra-turn directives from the card database without claiming to
understand arbitrary attack text?

Yes for a deliberately narrow audited grammar.

Implementation: `tools/simple_attack_board_semantics.py`  
Regression: `results/simple_attack_board_semantics/reproduce.py`

## Audited semantic dimensions

The compiler treats three dimensions independently.

### Base damage

A blank damage field is compiled as zero damage. A field containing only decimal
digits is compiled as fixed damage.

Variable `+`, `-`, and `×` expressions remain unsupported by this layer.

In the current effectively legal Expanded snapshot, this covers **16,139 of
20,003** attack-print rows.

### Exact damage-counter templates

Seven full-text templates are recognized. Full-text matching is intentional:
extra clauses prevent a row from entering this semantic island.

The current snapshot contains **91** matching print rows:

| Scope | Distribution | Print rows |
| --- | --- | ---: |
| opponent's Pokémon | distributed | 35 |
| opponent's Bench | distributed | 20 |
| opponent's Active | fixed target | 13 |
| one opponent Pokémon | single target | 8 |
| one opponent Benched Pokémon | single target | 7 |
| one of your Pokémon | single target | 7 |
| this Pokémon | fixed target | 1 |

This includes Phantom Dive's six distributed Bench counters and effect-only
Cursed Drop variants.

### Extra-turn directive

The compiler recognizes the unconditional sentence:

`Take another turn after this one.`

and records whether its text also specifies skipping the between-turns step or
Pokémon Checkup.

There are **13** effectively legal attack-print rows with this directive in the
current snapshot.

This dimension is independent of other uncompiled text. For example, a card can
unconditionally schedule an extra turn while also containing another clause
that still needs a separate semantic handler.

## Executable leaf contracts

A compiled row can produce a leaf `AttackDef` for the attack-copy kernel.

That preserves:

- stable print-specific attack identity;
- Energy cost;
- GX identity for `-GX` attacks;
- one body event label;
- a typed pending extra-turn directive when present.

The compiler does not infer a copy selector for outer copy attacks. Existing
copy-signature work remains the authority for that family.

## Board materialization

For opponent-facing exact counter effects,
`materialize_opponent_board_program()` validates a concrete counter allocation
against the live stack-bearing board:

- the exact number of counters must be allocated;
- Bench-only effects cannot target the Active;
- single-target effects must use exactly one positive target;
- fixed-Active effects must target the Active;
- distributed effects may split their total across eligible targets.

The result is a `PhysicalBoardEventProgram` for the existing copied-damage
executor.

Effect immunity remains a later live-state overlay and is not guessed from card
text here.

## Phantom Dive composition witness

The regression compiles Dragapult ex `sv6-130` directly from card data:

- fixed damage: 200;
- counter scope: opponent Bench;
- distribution: any way;
- total counters: 6.

It materializes a 4/2 split across two Benched Pokémon, then uses the compiled
leaf attack inside Haughty Order's existing copy execution.

The physical replay produces three simultaneous KO candidates:

- the 200 HP Active from normal damage;
- a 40 HP Bench target from four counters;
- a 20 HP Bench target from two counters.

The outer Haughty Order cleanup still appears last in the event trace.

## Timeless-GX composition witness

Dialga-GX `sm5-100` compiles to:

- fixed damage: 150;
- GX attack: yes;
- extra turn: yes;
- skip Pokémon Checkup / between-turns step: yes.

Its leaf `AttackDef` therefore carries the same typed turn-boundary directive
used by the manually authored copy regressions.

## Methodological point

Conservative compilation is useful when it exposes exactly which semantic
dimensions are supported.

A numeric damage field, an exact counter template, and an unconditional
extra-turn sentence can be compiled independently. Unknown clauses remain
visible rather than being absorbed into an optimistic “attack understood”
label.

## Limits

The compiler does not yet model:

- variable damage formulas;
- Weakness/Resistance derivation from live card profiles;
- damage modifiers from attack text;
- Special Conditions;
- Energy movement or discard;
- switching and gust;
- arbitrary target selection;
- damaged-by-attack reactions;
- effect immunity;
- conditional extra-turn clauses;
- VSTAR Power or other global one-use budgets.

Those should be added as typed semantic families with their own regressions.
