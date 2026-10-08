# Prize-context uncertainty in Retreat payment

## Failure mode

The existing six-family Special Energy provider adapter deliberately retained
an attached Counter Energy or Reversal Energy unit snapshot if the relative
Prize count was unknown. That is a legitimate unresolved observation, but
an unguarded Retreat executor could treat a stale high snapshot as permission
to discard one physical card for more Energy than it currently provides.

There was also a deterministic corner case: a Counter Energy on a Pokémon-GX
or Pokémon-EX always provides one unit, and a Reversal Energy on a noneligible
holder always provides one unit, regardless of Prize counts. The old
implementation preserved the potentially stale snapshot even for those cases.

## Resolution

`tools/retreat_dynamic_energy_units.py` now:

1. resolves card-ineligible holders to one unit even when Prize counts are
   missing;
2. evaluates the **minimum and maximum possible Energy units** from exactly
   the selected physical payment cards;
3. reports unresolved selected providers only if
   `minimum < Retreat Cost <= maximum` under unknown Prize counts;
4. blocks these ambiguous payments in the low-level dynamic adapter.

`tools/board_derived_retreat.py` exposes
`unresolved_selected_provider_ids` and withholds a transaction only when the
selected payment's legality is actually Prize-dependent. It first normalizes
the board, then checks the final effective Retreat Cost.

This is a **decision-sufficiency** test. A simulator may have incomplete
information about the actual provider unit count but still know a payment is
valid under every possible world. It can then execute the payment safely
without inventing the hidden count.

## Reproducible witnesses

- One eligible Counter Energy with a cached two units cannot pay cost 2 if
  Prize counts are unspecified; it can always pay cost 1.
- The same card on a Pokémon-GX is deterministically one unit.
- Eligible Reversal Energy with a cached three units cannot pay cost 3
  under unknown Prize counts; it can always pay cost 1.
- Ineligible Reversal Energy is deterministically one unit.
- An attached, unselected Counter Energy does not block a fully paid
  Double Colorless Energy Retreat.
- Selecting both Counter Energy and Double Colorless Energy guarantees
  three total units, but the fourth unit exists only when behind on Prizes.
  The cost-3 payment is safe with missing Prize context, while cost 4 is
  explicitly unresolved until the counts become known.

## Evidence and limitations

Card behaviors are grounded in Counter Energy `sm4-100`, Reversal Energy
`sv2-192`, and the existing dynamic-provider catalog. The rulebook's
Retreat section specifies discarding Energy that pays the Retreat Cost.

The bound model covers only these recognized conditional unit-count families
and only the selected payment's numeric feasibility. In a full game, Prize
counts are normally public and can be supplied directly. Unknown context
is an abstraction/adapter issue, not a claim that players cannot count Prizes.

The bound check does not estimate strategic probabilities across hidden
states. It does not expand conditional type semantics for attacks.

Run `python results/retreat_prize_provider_uncertainty/reproduce.py`.
`results/retreat_prize_provider_uncertainty/exhaustive.py` independently
enumerates 576 small physical-payment cases (four cached Counter/Reversal
snapshots, 16 subsets of four attached physical Energy cards, nine costs).
It compares unknown-context results against both known Prize regimes,
and requires every unknown-context accepted Retreat to be legal in both
worlds. This is an exhaustive check of the bounded four-card fixture,
not of all possible decks.
