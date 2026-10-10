# English BW-onward Special Energy reprint-text audit

## Why this matters

Exact Retreat payment symmetry can group physical copies only if their
effects are truly interchangeable. Same-name printings may have
different wording, even when their effects are intended to agree.
A planner should preserve source-print identity until a card-equivalence
layer is validated.

## Exhaustive local-source scan

The bundled English card snapshot contains **113 Special Energy print
rows** from sets released on or after April 25, 2011, representing
**74 distinct names**. There are **26 names with multiple print rows**.

Four of those names have more than one raw text-string version:

- Prism Energy
- Jet Energy
- Luminous Energy
- Reversal Energy

The automatic formatting normalization consolidates differences in
whitespace and missing spaces after full stops. After this conservative
normalization, exactly **one name** still has distinct wording:

**Prism Energy**, between the older BW4 printing and the more recent
versions. Its old text phrases the Basic Pokémon condition as checking
the Pokémon to which the card is attached; the newer text phrases it
as checking whether the card is attached to a Basic Pokémon.

These clauses appear semantically consistent. This audit does not
claim to prove formal rules-text equivalence, because English print
string comparison is only a screening technique and updated rules text
can supersede an older print.

## Connection to safe symmetry

The preceding [payment symmetry result](../retreat_payment_symmetry/)
groups Energy copies by caller-certified interchangeability. This
scan can establish where a same-name group has uniform normalized
printed text in the supplied data. It cannot establish that the
effective state-dependent Energy units or hidden-information histories
are equal at every point in a game.

In particular, Reversal Energy's current provided unit count varies
with relative Prize state and its holder. Even two cards with identical
printed text need to be evaluated under their actual current board
conditions before grouping.

## Reproduction

`tools/special_energy_print_fingerprints.py` reads sets and card
records from `resources/`. It exposes print IDs, release dates,
raw card text and a minimal formatting-only normalized text.

`results/special_energy_reprint_fingerprints/reproduce.py` verifies
the exact row/name counts and the four raw and one normalized text
variant sets, including the three identified Prism Energy print IDs.

Run: `python results/special_energy_reprint_fingerprints/reproduce.py`.

## Scope

The result covers the available English card snapshot and its
release-date metadata. That snapshot does not necessarily contain
every Japanese-only paper Expanded promotional printing. It is a
source-data quality and compatibility audit, not a legality
certification or competitive recommendation.
