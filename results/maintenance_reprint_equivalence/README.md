# Maintenance: pre-play versus post-play hand semantics

Two outside-Expanded printings, `base1-83` and `base4-112`,
say to shuffle two **other** cards from the hand into the deck to
draw one. Legal Expanded printings `xy3-96`, `xy12-79` and
`g1-64` say to shuffle two cards from the hand, with an explicit
prohibition when fewer than two can be returned.

The word "other" excludes the played Maintenance card itself.
The modern wording also excludes that card because it has already
been played. Consequently the same post-play two-card subsets can
be chosen, and each resulting deck has the same random permutation
distribution before drawing the top card.

`tools/maintenance_subset_choices.py` implements the two selections
independently. The bounded regression enumerates post-play hand
sizes zero through four and deck sizes zero through three, including
fully distinguishable source cards. It checks the two outcome sets,
choice-specific probability normalization, and inability to use the
effect with fewer than two hand cards. The test covers 20 input
classes and 1,520 conditional continuations.

Run `python -m results.maintenance_reprint_equivalence.reproduce`.

**Status:** bounded state-model equivalence. The central resolver
continues to mark both old printings `semantic_review`, pending a
separate official reprint-policy review. There may be board effects
outside this isolated draw window. Both wordings have an Item-type
cost that can be blocked by applicable lock effects, and those
external restrictions were excluded from the test.

See the official Black & White era introduction explaining that the
older ordinary Trainer designation became Item:
https://www.pokemon.com/us/pokemon-tcg/black-white
