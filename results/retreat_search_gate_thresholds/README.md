# Typed Trainer search payment thresholds after Dashing Pouch Retreat

## Conditional theorem

A verified Dashing Pouch Retreat can return one Energy card under a
minimal payment, or two under a larger legal payment. Suppose the hand
contains f additional expendable non-Item cards, with the played Item
excluded. A search Item requiring k other cards of any type becomes
playable after the smaller payment iff f+1 >= k, and after the larger
payment iff f+2 >= k. The larger payment alone enables the Item
precisely when f = k-2, provided f is nonnegative.

## Local card-text catalog

| Required discard | Names | Starting spare fodder for unique overpayment benefit |
| --- | --- | ---: |
| 1 arbitrary | Earthen Vessel, Mysterious Treasure, Quick Ball, Techno Radar | None |
| 2 arbitrary | Computer Search, Electromagnetic Radar, Fiery Flint, Ultra Ball | 0 |
| 3 arbitrary | Secret Box | 1 |
| Another Item | Cram-o-matic | None from returned Energy |

The source catalog has ten distinct discard-search Item names in the
Black and White onward dataset. This is a card-text census, not a
certification of all paper-Expanded ban and reprint statuses.
Computer Search and Secret Box are alternative ACE SPEC candidates.

Returned Energy does not meet the other-Item requirement of Cram-o-matic.
An Item's ability to pay its cost also does not ensure its search target
is available or that an opponent's Item lock permits playing it.

## Independent verification

The reproduction script reads the repository's local card catalog and
enumerates exact eligible hand-card payment choices using the existing
discard_cost_witness engine. It tests ten Item names across four
starting-fodder counts and both returned-Energy states (40 paired cases).
All 40 paired cases match the threshold model.

Reproduce from the root: python results/retreat_search_gate_thresholds/reproduce.py

Parent physical transaction: results/retreat_ultraball_payment_bridge/.

These numbers concern isolated search playability. Preserving Energy
for a future attack may be strategically more valuable than unlocking
one present search action.
