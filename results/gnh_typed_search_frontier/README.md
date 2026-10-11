# Typed full-action frontier for Guzma & Hala in Aichi Expanded

## Motivation

The existing Aichi `paid_gnh_states` solver focuses on obtaining
Technical Machine: Evolution and Jet Energy. It can miss valid payment
lines if those immediate resources are already held. The standalone
[missing-path witness](../gnh_optional_paid_duplicate_search/) demonstrates
one such case.

This research supplies a reusable **typed, named-card action enumerator**
in [tools/gnh_typed_search_frontier.py](../../tools/gnh_typed_search_frontier.py)
without replacing the existing optimizer's narrower scoring code.

## Search and payment model

After a G&H Supporter has been committed, the state contains a hand
(with G&H already removed), searchable deck, and available payment cards.

- Optional cost: discard **exactly two physical cards** from current hand.
  A caller may specify names to protect from discard. This decision is
  made at G&H play, before any full-deck inspection it initiates.
- Stadium: search for zero or one card of a named Stadium category.
- Bonus Tool/Special Energy: available only if the optional two-card
  cost was actually paid. Each search may select zero or one named
  card of its own category.
- Every chosen fetched card moves from the searchable deck to hand.
  Every payment card moves out of hand into the discard-pile ledger.
- Only one ordinary Supporter can be played per turn; this component
  assumes that commitment happened before the input state.

The permitted card names are sourced from the 2026 Aichi list and its
Expanded card roles: Stadiums Artazon/Grand Tree; Tools Stealthy Hood,
Technical Machine: Evolution, Counter Gain; Special Energy
Capture/Jet/Memory. These are distinct categories. The code is
intentionally scoped to this list, and accepts further extension only
after verifying additional names and effects.

The action type records the selected payment pair and each of the
three optional search outputs. An action can be valid even if it
does not solve the first-turn TM/Jet setup objective. This matters
because later resource utility and deck composition differ.

## Verification

The [standalone regression](reproduce.py) constructs a physical
hand with five distinct card instances, including two Guzma, and
an eight-card deck with named multiple search categories. It
independently enumerates all physical discard index pairs and
Stadium/Tool/Energy pick indices. After grouping identical card
names, the oracle and typed action generator must agree for three
different protected-name sets.

For every generated action, the test verifies conservation of
physical card counts across hand, deck, and the newly paid discard
ledger. It also confirms that no-pay actions cannot access the Tool
and Special Energy bonus searches, while the missing two-card
payment remains available even with TM and Jet held.

CI: [Windows validation workflow](../../.github/workflows/validate-gnh-typed-search-frontier.yml).

## Card-pool ontology check

The companion [card-role regression](card_roles_reproduce.py) reads
the repository's complete English card JSON to verify every named
Aichi search target exists in the source roster and has the expected
printed category. It confirms Artazon/Grand Tree are Stadiums;
Stealthy Hood, Technical Machine: Evolution and Counter Gain
are Pokémon Tools; Capture, Jet and Memory Energy are Special
Energy; Guzma & Hala is a TAG TEAM Supporter with the
optional on-play discard clause; and Tag Call is an Item whose
search permits up to two TAG TEAM targets. This check prevents a
synthetic frontier from silently using invented card classifications.
It cannot replace format-specific legality verification.

## Interpretation limits

This enumerates **feasible named material lines** in a known physical
deal. It is not an implementable optimized policy under imperfect
information: selecting a payment on the basis of hidden Prize
composition would still be a K0 hindsight error unless some earlier
deck search has supplied K1. Nor does the module evaluate whether
discarded cards are strategically expendable, whether the Active
Pokémon can safely use Stellar Wish, or downstream win probability.

The next useful layer is a decision-information partition that groups
underlying deals by what a player actually observes at the moment of
payment, then assigns **one common K0 action per observation class**.
This would put a rigorous cap on the current existence-oracle estimates.
