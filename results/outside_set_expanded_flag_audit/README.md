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

## Measured resolver partition (October 9, 2026)

The passing audit found 243 flagged prints across 46 outside-scope
sets, partitioned into:

| Resolver class | Print count |
| --- | ---: |
| Exact current-semantic fingerprints | 118 |
| Historical official reprint evidence | 39 |
| Current official errata | 43 |
| Current official-semantic example | 3 |
| Known non-equivalent, conflicting labels | 4 |
| Semantic review unresolved | 36 |
| **Total** | **243** |

Thus 164 have evidence in the current-semantic eligibility policy,
39 have historical-only positive evidence, four carry current
negative evidence, and 36 remain in semantic review. These are
evidence classifications rather than 243 verified tournament
legality decisions.

The [source-release gate](../outside_source_release_gate/)
separately prevents all 25 Celebrations Classic physical prints
from being classified as historically available before
October 8, 2021.
