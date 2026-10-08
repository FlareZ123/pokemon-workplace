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

Tool thresholds such as Rescue Board can leave card-state information
unresolved while the Retreat decision is already determined. When base
Retreat Cost 1 becomes zero from Rescue Board's unconditional -1, its
additional low-HP no-cost effect cannot alter payment legality, so the
empty-payment branch is safe even without knowing remaining HP.
When base cost 2 becomes cost 1 except at 30 HP or less, the same
missing information changes payment legality; those branches remain
unresolved. The enumerator returns `information_complete=False` in
both cases to expose missing source information.

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

## Independent validation

`results/retreat_action_enumeration/exhaustive.py` compares the
enumerator with a separately written brute-force caller that tries
every possible physical Energy-card subset and every Bench promotion,
then filters committed transactions.

The finite oracle covers **1,800 exact scenarios**: fifteen Energy
quantity multisets with zero through three attachments whose represented
units are one or two, five printed base Retreat Costs, one or two Bench
destinations, with/without Float Stone, three Stadium states (none,
Galar Mine, Jamming Tower), and with/without an opposing Block Snorlax.
Every returned action set agrees with the independent brute-force
transaction oracle. The test also checks conservation of each physical
Energy copy and Retreat quota usage in the explicit two-Basic-plus-DCE
witness.

Verified with GitHub Actions run
[37839905539](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37839905539).

## Robustness under unknown Prize information

`robust_prize_oracle.py` independently compares the unknown-Prize action
frontier to the intersection of frontiers produced when the player is
definitely behind on Prizes versus definitely tied. Its bounded cases
include selected subsets of Counter Energy, Reversal Energy, Double
Colorless Energy, and Basic Energy, each of the relevant cached unit
quantities, four different holder tag sets (including Pokémon-GX and
other Rule Box restrictions), and seven positive-or-zero Retreat Costs.

Across **1,792 bounded states**, the unknown-context actions equal that
intersection exactly. This is a robustness result: the returned actions
can be committed regardless of which Prize regime is true. In the
simplified family, being behind only increases the possible units of
Counter/Reversal, so the tied state is the lower-unit world.

A concrete instance selects Counter Energy and Double Colorless Energy.
They always provide at least three units, so a cost-3 action is
executable without Prize information. Cost 4 requires the behind
state, so it is deliberately absent from the unknown-context frontier.

This equivalence is proven by the direct lower/upper-bound predicate for
these exact provider families and independently tested by enumerating
both known worlds. It must not be generalized to unknown effects that
change Retreat Cost or suppress the action itself.

The [CI run](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37840238608)
passed this robustness oracle together with the 1,800-scenario physical
subset oracle and earlier regressions.

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
