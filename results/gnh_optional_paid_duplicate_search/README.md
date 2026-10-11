# Aichi Guzma & Hala: paid duplicate search despite held essentials

## Missing legal branch

The existing `tools/aichi_gnh_discard_frontier.py` solver returns only a
no-payment path when both Technical Machine: Evolution and Jet Energy are
already held. G&H's on-play optional two-card discard remains available in
that state and can provide **additional** Tool and Special Energy cards.
The Aichi 2026 list contains two copies of each named output, so this
is possible without introducing cards absent from the source deck.

The correct timing is discard before first deck inspection, as established
by the [official G&H phase audit](../gnh_on_play_discard_timing/).
The assumption that two other hand cards are strategically expendable
must be tested rather than inferred.

## Exact conditional physical witness

One projected hand contains TM: Evolution, Jet Energy, Guzma, and Karen.
The projected deck contains another TM, another Jet Energy, Artazon,
one Ticket-role TechSlot1, and eight other cards. An unused Jirachi
Stellar Wish will inspect five after G&H finishes searching and shuffles.
Assume Guzma and Karen may be discarded without undermining a different
winning line, and that the surrounding board allows the late Wish.

- The existing solver obtains Artazon with no payment, leaving eleven
  searchable deck cards. The Ticket top-five hit chance is **5/11**.
- A legal additional line pays Guzma and Karen at G&H play, obtains
  Artazon plus the spare TM and Jet, and leaves nine deck cards. The
  Ticket top-five hit chance is **5/9**.

Thus the conditional hit gain is exactly **10/99**, approximately
**10.101010 percentage points**. This number applies only to the
constructed eleven-versus-nine-card post-search state. It does not
describe actual Aichi opening frequency, overall setup success, or
match-winning value.

The standalone [reproducer](reproduce.py) imports the actual old
solver, verifies that it returns only one no-payment path, constructs
a physically conserved paid alternative, and independently enumerates
five-card subsets to check both rational probabilities.

## Modeling implication

A payment solver should preserve the optional payment action even
when its immediate required outputs are held. Additional named fetches
may have utility as future resources or deck-thinning operations.
The correct comparison depends on discard opportunity cost, prior
Prize knowledge, remaining named copies, and later action constraints.

This test preserves the existing solver unchanged and documents a
specific action-space completeness counterexample. The measured
advantage is a conditional access calculation, not a deck recommendation.
