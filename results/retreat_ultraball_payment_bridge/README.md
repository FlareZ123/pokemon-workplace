# Retreat payment overage enables Ultra Ball on the same turn

## Question

Can selecting a legal *larger* Retreat payment immediately unlock a
Trainer action that the inclusion-minimal payment cannot execute?

**Yes.** This result composes the physical Retreat action enumerator and
the independent canonical Trainer discard/search transaction over the
**same conserved card-class zone ledger**. It demonstrates a concrete
counterexample to using inclusion-minimal Retreat payment as a general
deck-search action-generation rule.

## Card text and exact constructed state

- Dashing Pouch, sm4-92: Energy discarded to pay the Retreat Cost of
  its holder goes into hand instead.
- Double Colorless Energy, bw4-92, provides two generic Energy units.
- Ultra Ball, swsh9-150, requires discarding two *other* cards from
  hand before searching the deck for any Pokémon.
- Advanced Player's Rulebook: normal Retreat payment (A-03), Items
  (B-01), the discard destination (C-01) and effect precedence (II-A).

Construct one Stage 1 Active Pokémon with Retreat Cost 2, an attached
Dashing Pouch, one damage counter, one Double Colorless Energy (DCE),
and one Basic Psychic Energy. Its Bench has one Pivot. The entire
represented hand holds only Ultra Ball; a searchable Basic Pokémon is
in the deck. It is the player's own ordinary turn, before attacking,
with Item play permitted.

The two payment selections and resulting *immediate* Ultra Ball access:

| Paid to Retreat | Physical Energy in hand afterward | Can discard two other cards for Ultra Ball? |
| --- | ---: | --- |
| DCE | 1 (DCE) | No |
| DCE plus Basic Psychic | 2 (DCE and Basic) | **Yes** |

Both Retreats physically commit, promote the same Pivot, consume one
normal Retreat action, and conserve each Energy card. In the larger
payment branch, the canonical Ultra Ball transaction discards both
returned Energy cards and moves the selected Pokémon from deck to hand.
The Retreat budget remains spent and no Supporter is consumed.

The important nonlinear interaction is **discard-cost threshold
crossing**. The extra payment converts an unexecutable Item search
into an executable one without using any additional Supporter or
energy-attachment allowance. The cost is leaving the outgoing
Stage 1 Pokémon with no attached Energy.

## Independent suppression controls

- Opposing Mr. Mime sm9-66 with enabled Scoop-Up Block, plus the
  holder's existing damage, prevents the two paid Energy cards
  entering hand. Neither branch pays Ultra Ball.
- Jamming Tower sv6-153 temporarily disables Dashing Pouch and
  likewise leaves no Energy in hand.
- An Item-play lock prevents the Ultra Ball action even after the
  larger payment returns two Energy cards.
- One additional expendable card already in hand eliminates the
  narrow access gap: either Retreat payment now provides two
  discardable cards for Ultra Ball.

The state was deliberately engineered. It does not establish a
general deck-building preference for overpaying Retreat, nor
that discarding the Basic Energy is always correct. The value of
keeping it attached to the old attacker depends on the next turns.
The result establishes a concrete **action-feasibility difference**
rather than an empirical win-rate change.

## Reproduction

The script uses existing, validated repository components:
tools/retreat_action_enumerator.py,
tools/retreat_energy_transaction.py,
tools/trainer_search_transaction.py, and
tools/discard_cost_witness.py. It reuses the Energy-zone ledger from
the exact physical Retreat as the input to Ultra Ball's typed retrieval
transaction, preserving each card-class total.

Run from the repository root:

python results/retreat_ultraball_payment_bridge/reproduce.py

A dedicated workflow also runs both parent-kernel regressions.

Related results:
- results/typed_retreat_payment_pruning/: why pruning happens to be safe
  in the much narrower monotone-energy gust minimax
- results/retreat_resource_allocation_frontier/: raw physical
  nonminimal payment destinations
- results/discard_search_item_catalog/: other discard-gated search Items

## Implication

A game-tree optimizer may prune an action only after proving that the
current value function and reachable continuation preserve the required
resource monotonicity. Physical Retreat payment size alone is
insufficient. Action-cost gates in hand create discrete strategic value
that a board-only search model will miss.
