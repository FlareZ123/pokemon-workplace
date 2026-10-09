# Current reprint-policy coverage

## Question

How much of the historical same-name print pool can the current deck-legality proof classify at the present snapshot boundary?

## Population

The audit uses the 4,260 outside-scope prints whose names also have at least one legal Expanded target in the bundled English snapshot.

It evaluates the pool as of 2026-10-09.

## Conservative policy

The conservative profile promotes no historical reprint candidate automatically.

At this checkpoint it classifies 77 prints as ineligible from explicit non-equivalence evidence and leaves 4,183 unresolved.

## Current semantic evidence policy

The `current_semantic_evidence` profile accepts three evidence classes whose present semantic relationship is directly represented:

| Evidence class | Eligible prints |
| --- | ---: |
| exact current-semantic fingerprint | 133 |
| official errata | 44 |
| current Tournament Handbook semantic example | 3 |
| **Total** | **180** |

The same 77 known non-equivalent prints remain ineligible.

The unresolved remainder is 4,003 prints:

- 39 historical-official candidates whose evidence does not by itself establish present equivalence;
- 3,964 semantic-review prints.

The current-semantic profile therefore resolves 257 of the 4,260 same-name historical prints into an eligible or ineligible state. The remaining 4,003 still require further evidence.

## Interpretation

Reprint semantics remain a major legality bottleneck even after the strongest current evidence is accepted.

The evidence-assisted profile increases usable historical-print coverage while preserving older positive evidence as a distinct historical class.

The semantic-review remainder is a concrete research queue. Future work can reduce it through rule-grounded normalization, official errata, explicit handbook examples, and distinguishing witnesses.

## Reproduction

`tools/reprint_policy_coverage.py` composes the same print-level classifier used by deck adjudication over the full same-name historical pool.

`results/reprint_policy_coverage/reproduce.py` derives its assertions from the resolver's evidence-class totals. This keeps the composition test valid when concurrent semantic research legitimately moves prints between resolver classes.
