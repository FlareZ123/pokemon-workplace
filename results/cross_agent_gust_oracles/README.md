# Independent cross-agent audit of gust state-space kernels

## Purpose

Several paper Expanded tactical studies independently implement the same
bounded gust problem. Agent44's earlier typed Boss/Serena and later mixed
Boss/Counter engines differ from agent20's versions in representation and
some action-enumeration details. Agreement between independent codebases is
stronger evidence than identical conclusions inside a single implementation.

This audit checks the overlap, preserves the exact denominators behind
slightly different source-priority summaries, and prevents future
generalizations from silently relying on one potentially flawed kernel.

## Tested models

### Pokémon V target eligibility

Agent44 uses a `Target(prizes, is_pokemon_v)` dataclass, with five
target categories and boards containing 2..5 Pokemon.

Agent20 uses literal classes `N1,N2,N3,V2,V3` and boards with 2..6
Pokemon. The common 2..5 range has **582 distinct Active/Bench board
classes**.

After converting target classes, the reproducer compares both kernels
for all nine inventories with `Boss copies = 0,1,2` and `Serena copies
= 0,1,2`, producing **5,238 independent exact comparisons**.

The size-six extension in agent20's model remains outside this direct
cross-agent comparison, although it has its own Boolean-deadline
regression.

### Prize-gated Counter Catcher

Both agents independently implemented a minimax for unconditional
Boss gusts and threshold-gated Counter gusts with the same one-hit-KO
six-Prize opponent board, adversarial promotion, and a fixed opponent
remaining-Prize count. Compare all 146 board classes and all nine
`Boss copies = 0,1,2` by `Counter copies = 0,1,2` combinations,
for opponent remaining-Prize counts 1..5:

`146 × 9 × 5 = 6,570` cross-agent state results.

The reproducer checks exact equality, rather than just aggregate
histograms.

### Source order: a denominator reconciliation

Agent20's [mixed study](../mixed_gust_prize_minimax/) evaluates a
source preference *after optimizing over all opposing Bench target
choices*, producing one result per **board class**.

Agent44's [mixed study](../mixed_boss_counter_minimax/) instead
compares forcing Boss first or Counter first on a **fixed target
Prize value**. There are 292 distinct board-plus-Bench-value options
for each opposing Prize count, across the same 146 board classes.

This audit independently computes each same-target conditional
continuation with agent20's transition kernel and compares the value
to agent44's source-order solver. Across five opponent Prize counts,
**1,460 comparisons** agree.

Strict advantages from Counter first under identical target choice
are **0, 0, 82, 130, 162** of 292, for opposing remaining Prizes
1..5 respectively.

These numbers differ from the board-level minimum comparison
**0, 0, 73, 94, 100** of 146, because the units differ. Both
are valid for their explicitly stated decision problems.

## Why this improves reliability

The two implementations share some rule assumptions, so agreement
cannot prove full-card accuracy. Yet the independently designed
representations and recurrences provide checks against coding
errors, bookkeeping mistakes, and accidental shifts in state scope.

In particular:

- The five target classes map one-to-one onto a typed Python
  dataclass with boolean V identity.
- The Prize-gated source values agree state by state, including
  inventories with more than one Boss or Counter copy.
- The same-target source-priority comparison reproduces the
  independent fixed-choice census and reconciles the differently
  aggregated findings.

## Reproduction

`python -m results.cross_agent_gust_oracles.reproduce`

Underlying implementations:

- `tools/typed_gust_target_minimax.py`
- `tools/target_restricted_gust_minimax.py`
- `tools/mixed_boss_counter_minimax.py`
- `tools/mixed_gust_prize_minimax.py`

The reproducibility script asserts **13,268 cross-agent state and
action-order results**. The tests use integer attack counts, so
there is no floating-point comparison tolerance.

## Limits

Both kernel families model immediate one-hit Knock Outs, no additional
opponent Bench entries or attacks, no changing opposing Prize count,
and a single effective gust before attacking. Agreement does not
cover real card accessibility, Serena's draw mode, Supporter quota
contention, actual Item lock, damage carryover, or opponent hidden
information. Those questions have separate research paths and need
independent validators.
