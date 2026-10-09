# Outside-set Expanded flags versus functional-reprint evidence

## Problem

There are 243 English card records whose set has no direct
Expanded: Legal flag but whose **individual print** has
expanded: Legal metadata, across historical sets and
2021 Celebrations Classic Collection.

These flags are data-source claims. Pre-Black & White
prints generally require current functional-reprint
equivalence to an eligible Expanded print under
current Play! Pokémon policy.

## Contradictions

Four clear examples are historic TV Reporter
ex15-82, ex3-88, and pop2-11 (empty-deck action
difference), and historic Pokégear 3.0 hgss1-96
(mandatory-versus-optional deck-window choice).
Each has print-level expanded: Legal, but the
current resolver records independent negative
semantic evidence. A print-level metadata flag
must not silently erase a specific negative witness.

The audit program cross-joins all 243 prints
against the current resolver. It reports counts
by evidence class, names every conflict and
retains unresolved cases distinctly.

Not every flag is erroneous: some have exact
fingerprint matches or official errata. The
proper output carries both source metadata
and modern semantic provenance.

## Reproduction

Run python -m results.outside_set_expanded_flag_audit.reproduce

The regression asserts the 243-flag population,
four named negative conflicts, and presence of
unresolved print evidence.

See tools/outside_set_expanded_flag_audit.py.
