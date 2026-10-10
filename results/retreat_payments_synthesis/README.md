# Retreat payment research: legality, uncertainty, search thresholds and safe reductions

## Executive synthesis

Normal Retreat looks like a simple Energy-cost payment. For a robust
paper-Expanded simulator, it has four separable layers:

1. **Rules-valid physical action.** The outgoing Active, payment card
   identities, attached Energy units, effective cost, ability/position
   prohibitions, Bench promotion and canonical Retreat quota determine
   whether a physical action can be executed.
2. **Physical consequences.** The selected cards leave attachment and
   may enter hand, discard or Lost Zone depending on their own rules,
   Tools, locks and replacement effects.
3. **Future action availability.** Hand discard gates, attack readiness,
   supporter/item usage, attached-resource retention and future opposing
   locks affect the continuation value of that chosen payment.
4. **Search compression.** A planner may group symmetric payments and
   sometimes discard dominated payments, but only under explicitly
   proved equivalences or objective-specific dominance conditions.

This synthesis links exact model results obtained in the supplied
card/rule environment. It does not convert them into empirical deck
win rates or claim that all possible Expanded rulings are compiled.

## The underlying mechanical base

The [physical payment ruling study](../retreat_energy_payment_semantics/)
used an official Japanese Dashing Pouch Q&A to establish that two
Double Colorless Energy cards may both be selected for a cost-two
Retreat. A policy restricted to inclusion-minimal payments therefore
omits at least one documented legal physical action.

The [Retreat transaction](../retreat_energy_transaction/),
[derived board sources](../board_derived_retreat/) and
[complete action enumerator](../retreat_action_enumeration/)
represent and verify physical outgoing Energy IDs, promotions,
resolved cost modifiers, destination effects and the shared action
budget. Important lock and reactivation boundaries are covered by
[Ability suppression](../retreat_causal_ability_overlay/) and
[Jamming Tower projections](../retreat_stadium_tool_overlay/).
The action enumerator was compared against 1,800 independent bounded
subset/Bench cases and 1,792 known-versus-unknown Prize contexts.

The existing modeled payment bound selects no more than the positive
numeric Retreat Cost in physical Energy cards. This is a
conservative implementation with direct published support for the
two-DCE cost-two case; it is not a universal proof of every historic
multi-unit Energy interaction.

## Objective-specific pruning can be provably safe

The [typed gust minimax](../typed_retreat_gust/) only uses attached
Energy to enable future normal Retreat payments. Additional retained
Energy cannot harm the defending player's options in that toy game.
The [pruning theorem](../typed_retreat_payment_pruning/) proves that
every nonminimal payment has an inclusion-minimal payment which
leaves at least as much Energy attached. The defender can replicate
the original continuation, and possibly choose additional escapes.
An independent complete-payment solver agrees in 7,680 bounded
minimax configurations.

The conclusion belongs to the abstract **objective and transition
model**. It is not permission to erase extra physical payment
actions from the complete game engine.

## Search gates create nonlinear payment value

The [physical resource frontier](../retreat_resource_allocation_frontier/)
shows Dashing Pouch can return two paid cards to hand rather than
retaining one card attached. The
[Ultra Ball bridge](../retreat_ultraball_payment_bridge/)
makes this tactically concrete.

Construct a cost-two Active with Dashing Pouch, DCE plus Basic Energy,
and one Ultra Ball as the only card in hand. Paying DCE alone
returns one card and leaves Ultra Ball's mandatory two-card discard
cost unsatisfied. Paying DCE plus Basic returns two and permits the
same-turn typed Ultra Ball search. The latter line requires Item
play; Jamming Tower, applicable Scoop-Up Block or Item lock closes
it. One other expendable card already in hand eliminates the gap.

The [typed discard-search threshold atlas](../retreat_search_gate_thresholds/)
extends this to the local card-text catalog: when paying an additional
Energy returns exactly one additional discardable card, a required
k-card discard gate is newly enabled exactly when the hand already
contains k-2 other expendable cards. Returned Energy does not satisfy
Cram-o-matic's specifically Item-only discard requirement.

The stronger line may have a real cost: the old attacker loses
additional attached Energy. The value of that trade remains
matchup-, turn- and strategy-dependent.

## Unknown information changes safe optimization order

[Unknown Prize provider robustness](../retreat_prize_provider_uncertainty/)
and [its exact oracle](../retreat_action_enumeration/)
show how eligible Counter/Reversal Energy can have different
current Energy unit counts across otherwise identical modeled states.
Normal game Prize counts are public; unresolved counts here reflect
an incomplete simulator projection.

The [minimality intersection counterexample](../retreat_prize_minimality_paradox/)
demonstrates a noncommutativity:

- In tied-Prize state, Counter + Basic pays cost two minimally.
- Behind on Prizes, Counter alone is already sufficient.
- The two-card payment remains legal in both states.

Intersecting separately **minimal** world-conditioned actions
returns empty, whereas intersecting complete legal actions returns
the guaranteed two-card payment. Across 1,792 bounded states, that
premature worldwise-pruning approach lost 220 guaranteed minimal
actions in 168 cases.

**Safe order:** construct feasible action sets for each possible
world, intersect when seeking guaranteed actions, then prune under a
proof that applies to the robust objective and remaining information.

## Branching complexity and safe symmetry

The [binomial payment formula](../retreat_payment_branch_complexity/)
counts exact labeled one-/two-unit payment subsets.
The [mixed-unit DP](../retreat_payment_polynomial_dp/) extends counts
to any positive supported Energy unit size. Its summary states
track number of paid cards, total supplied units and the
smallest unit contribution, which suffices to determine whether a
payment is inclusion-minimal.

A constructed five-card Active with three one-unit and two two-unit
Energy has twelve cost-two physical payments, compared with five
inclusion-minimal ones. A larger illustrative cost-four state with
eight of each has 2,352 physical payments.

The [symmetry-orbit model](../retreat_payment_symmetry/)
counts only different class-level payment vectors, retaining the
number of underlying physical choices as a binomial multiplicity.
For that illustrative 16-attachment cost-four state,
2,352 physical choices become nine class-count orbits if all
within-class copies are genuinely interchangeable.

Interchangeability is stronger than matching provided Energy units.
It requires identical relevant rules and destination effects plus
equivalence under all observer-visible histories. The
[Special Energy print audit](../special_energy_reprint_fingerprints/)
finds 113 English BW-onward Special Energy print records and flags
Prism Energy's distinct wording after formatting normalization.
Neither that scan nor a shared card name alone proves card
effect equivalence.

## Recommended solver architecture

A search implementation should maintain an exact physical-state
source of truth and an observer-relative belief model where needed.

- Compile each current state's effective Retreat Cost, sources of
  prohibitions and conditional Energy units.
- Generate legal physical payment and Bench-promotion actions; preserve
  card IDs and destination replacements in the canonical transition.
- Preserve all world-possible actions until the desired information
  robustness guarantee is established.
- Project each successor into a valuation-relevant state that retains
  hand discard opportunities, attached Energy, future actions and locks.
- Apply optional permutation symmetry only after verifying that every
  copy in a proposed group is indistinguishable for all relevant
  transition and observation effects.
- Apply dominance pruning only with a proof tailored to the
  continuation model. If the continuation admits future hand
  discard/search gates, use the larger payment set unless a
  stronger dominance criterion is established.

These steps allow a planner to exploit large speedups in some settings
while retaining known strategically distinct payment branches in others.

## Evidence status and next directions

The results above are mathematical deductions or exact finite
mechanics tests with saved reproducible code and passing CI.
They are **not** sampled real-match outcomes. The bounded action
kernels still rely on externally supplied or partially compiled
board effects in places, and the complete Japanese legal card pool
can extend beyond the supplied English snapshot.

Useful next questions include: how to join observer-relative card
identity with payment orbit equivalence; how to value returning
Energy to hand versus preserving it on an attacker; how much
safe symmetry survives when cards enter Lost Zone or hand
through distinct replacement effects; and how to integrate
current opponent-turn Retreat options into a larger tactically
correct game-tree policy.
