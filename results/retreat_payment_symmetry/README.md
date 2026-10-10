# Symmetry reduction for physically interchangeable Retreat payments

## Result

A legal Retreat may admit many physical Energy-card payment choices that
produce the same class-level successor, provided the chosen cards are
interchangeable under all relevant effects and observations.

For a group of m indistinguishable attached Energy copies, choosing k to
pay Retreat has C(m,k) distinct physical selections. These selections
form a single class-count orbit under permutation of physical IDs.
Across groups, an orbit's multiplicity is the product of these binomials.

This can reduce search branching while preserving downstream value if
the state evaluator and transition rules are permutation-invariant
within every group.

## Exact algorithm and representative numbers

The reusable module `tools/retreat_payment_symmetry.py` enumerates
physical-payment class-count vectors, their multiplicities and whether
each vector is inclusion-minimal. It works with arbitrary positive
Energy-unit counts per class, subject to the existing repository
physical-card payment bound.

| One-unit copies | Two-unit copies | Cost | Physical payments | Class-count orbits |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 2 | 2 | 2 |
| 2 | 2 | 2 | 8 | 4 |
| 3 | 2 | 2 | 12 | 4 |
| 4 | 4 | 3 | 78 | 6 |
| 8 | 8 | 4 | 2,352 | 9 |
| 8 | 8 | 6 | 13,678 | 16 |

The 16-card examples illustrate hypothetical scaling. They do not
describe typical Expanded game states.

## Physical successor witness

An Active Pokémon has Retreat Cost 2, Dashing Pouch, two identical
one-unit Energy cards and two identical Double Colorless Energy cards.
One Pivot is Benched, and the Active is already damaged.

The exact `retreat_action_enumerator.py` produces eight committed
physical payment actions. They partition into four class-count orbits
with multiplicities 1, 1, 2 and 4.

For every orbit, the final hand Energy-class counts, remaining attached
Energy-class counts, Active position and canonical Retreat quota are
identical after the Dashing Pouch return-to-hand effect. The physical
identity of the individual cards differs, but the tested
permutation-invariant projection agrees.

## Evidence and verification

`results/retreat_payment_symmetry/reproduce.py` compares the orbit
construction with the canonical physical payment enumerator across
216 independent labeled-card configurations, with 0-5 copies per
class and costs 0-6. It additionally checks the exact physical
Dashing Pouch action set above.

The orbit multiplicities sum exactly to the previously proven
binomial full-payment count, and minimal-orbit multiplicities sum
to the prior inclusion-minimal subset count.

Reproduce: `python results/retreat_payment_symmetry/reproduce.py`.

## Critical validity boundary

Identical printed card names do not by themselves certify
interchangeability. A sound caller must verify that each group has the
same effective printed rules, provided Energy units, relevant attached
effects, destination restrictions and strategically relevant
observation/provenance state.

For example, if a replacement effect sends one specific physical
Energy instance to a different zone, treating it as exchangeable with
other attached Energy would incorrectly merge different successors.
Observer-private information can also break apparent class-level
symmetry.

The module is therefore a **conditional action symmetry framework**.
It does not automatically collapse physical card IDs inside canonical
game states; raw legal actions remain individually executable.
This approach is compatible with the earlier Dashing Pouch -> Ultra Ball
threshold, because destination-zone *counts* remain explicit even
when individual identical Energy IDs can be quotient out.
