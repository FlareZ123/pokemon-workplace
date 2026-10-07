# Ignition Energy provider state during Retreat

## Question

`EnergyAttachment.units` is a resolved snapshot. Can a holder-state transition
make that snapshot wrong for a later Retreat Cost payment?

## Finding

Yes.

The current card pool contains two Expanded-legal Ignition Energy prints,
`rsv10pt5-86` and `me2-124`. The card provides one Colorless Energy while
attached normally and three Colorless Energy while attached to an Evolution
Pokemon.

The Advanced Player's Rulebook also uses Ignition Energy as its explicit
multi-unit discard example: one attached copy can satisfy a three-Energy
discard while it provides three units, and the same physical card can also be
selected for a one-Energy discard.

The existing board-object evolution transition correctly preserves attached
cards. That means a Basic Pokemon can evolve while keeping an already-attached
Ignition Energy. If the attachment object still stores the pre-evolution
one-unit tuple, a later Retreat Cost 3 payment is incorrectly rejected.

The reverse stale state is also dangerous: a Basic holder carrying a stale
three-unit tuple would be incorrectly allowed to pay Retreat Cost 3 with one
physical card.

## State-derived adapter

`tools/retreat_dynamic_energy_units.py` adds an exact-print, conservative
provider refresh before Retreat payment.

For the two known Ignition Energy prints:

- a holder tagged `Stage1`, `Stage2`, or `Evolution` provides three units;
- other represented holders provide one unit.

Unknown prints keep their represented snapshot. The adapter does not infer
dynamic behavior from the card name alone.

## Regression

The reproducer starts with a Basic holder and one Ignition Energy represented as
one Colorless unit. It then uses the canonical board-object `evolve()`
transition, which preserves that physical Energy attachment.

Before refresh, the low-level Retreat transaction rejects the exact
post-evolution Retreat Cost 3 payment. After provider refresh, the same one-card
payment succeeds and the physical Ignition Energy moves from attached state to
discard.

A second witness begins with a Basic holder carrying a deliberately stale
three-unit tuple. The low-level transaction accepts the bad snapshot; the
dynamic adapter refreshes it to one unit and correctly rejects Retreat Cost 3.

## Strategic implication

Attached Energy identity and current Energy provision are different state
layers.

A physical Special Energy card should persist across holder changes, while its
provider function may need to be reevaluated from current holder and game
state. Treating `units` as immutable card identity can create both false
negative and false positive action branches.

## Limits

This result deliberately implements only the exact Ignition Energy family.
Other current Expanded Special Energy also have state-dependent unit counts,
including Twin Energy, Counter Energy, Reversal Energy, Neo Upper Energy, and
Super Boost Energy Prism Star. Those need additional holder, Prize, or board
context and should be added through explicit semantic rules rather than a
generic text heuristic.
