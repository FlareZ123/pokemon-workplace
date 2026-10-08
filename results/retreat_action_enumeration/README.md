# Exhaustive physical Retreat action enumeration

## Question

Can a search planner enumerate every executable normal Retreat action from
an exact represented game state, including the destination Bench Pokémon
and the physical Energy cards chosen as payment?

## Method

`tools/retreat_action_enumerator.py` first executes a read-only preflight
of `attempt_board_derived_retreat` to derive the current effective Retreat
Cost and normalized attached Energy provider units. It then enumerates the
canonical `legal_retreat_energy_choices` for that cost and crosses these
choices with all current Bench destination identities.

Each candidate runs through the full existing physical and action-budget
transaction from the same immutable starting state. Only actually committed
branches are returned. The result includes a preflight witness and count of
candidate branches evaluated, preserving reproducibility.

This is an exact finite enumerator over the represented mechanic, with
combinatorial complexity in attached Energy-card count. It does not prune
legal overpayments simply because another payment consumes fewer cards:
discard destination effects and longer-term strategies can make physical
card choice meaningful.

## Initial bounded cases

A Stage 1 Active with base Retreat Cost 2, one Double Colorless Energy,
two distinct one-unit Basic Energy cards, and two Bench destinations has
four legal physical payment sets per destination, for **eight Retreat
actions**. A Galar Mine changes effective cost to 4 and collapses the
payment choices to one three-card selection per destination, yielding
two actions.

Float Stone instead makes the cost zero, giving exactly one empty
payment for each destination. An Active opposing Block Snorlax prevents
all normal Retreat actions even with Float Stone.

The enumerator also distinguishes known and unknown Prize-context
dynamic Energy providers. An eligible Counter Energy with a cached
two-unit snapshot cannot be relied on to pay cost 2 without knowing
relative Prize counts. Counter Energy plus Double Colorless Energy
can guarantee the three-unit cost, so that branch may still be returned
with incomplete information.

Tool thresholds such as Rescue Board may make a cost or payment
unresolved; the enumerator propagates the composed model's uncertainty
rather than creating a physically committed branch by assumption.

## Research use

This offers the missing action-generation edge between the detailed
Retreat transaction kernels and search/planning methods. It can supply
legal defensive escape successors to the bounded gust-minimax models
in `results/typed_retreat_gust/`, which previously accept already
resolved Retreat Costs and Energy units.

A search policy can now compare legal payment witnesses by downstream
value: saved Energy, hand retrieval through Dashing Pouch, preserved
singletons, replacement Active, and future turn preparation. The
enumerator itself does not attach strategic utility values or estimate
real match-up frequencies.

## Limits

Card legality and the completeness of already compiled Retreat source
effects remain inherited from the underlying kernel. The supplied
current Stadium, causal Ability state, and external modifiers must be
valid. A snapshot with hidden Prize-dependent providers may yield only
guaranteed executable actions, with `information_complete=False`.

This module enumerates normal Retreat actions. Effect-based switching
is a separate execution channel and remains legal in states where
normal Retreat is blocked. Very large numbers of attached Energy
copies can make exhaustive enumeration expensive.

Reproduce: `python results/retreat_action_enumeration/reproduce.py`.
