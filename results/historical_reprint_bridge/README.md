# Historical official reprint bridge

The official 2012 Modified-Legal Reprint List can resolve a large part of the current raw-text semantic-review queue.

This result uses a deliberately narrow subset: older prints marked "Reference Required: No" where a same-name Black & White-onward print had already been released by the source date, 2012-03-13. The source describes these no-reference cases as reprints whose mechanics did not require updated reference text.

That produces 42 historical prints across eight names:

| Name | Prints |
| --- | ---: |
| Switch | 10 |
| Poké Ball | 9 |
| Energy Search | 7 |
| Energy Switch | 7 |
| Super Scoop Up | 6 |
| Full Heal | 1 |
| Recycle | 1 |
| Double Colorless Energy | 1 |

Forty-one are Trainers and one is Energy.

This evidence is stronger than fuzzy text similarity because Pokémon Organized Play explicitly accepted these exact old printings while the Black & White-onward counterpart was already in the legal card pool. It also remains narrower than a blanket name match. Historical entries marked as requiring a reference are excluded, as are cards whose bridge at that date could have depended only on a pre-Black & White printing.

Integrating the 42-print bridge into the reprint resolver changes the current same-name review partition from 106 exact + 44 name-wide errata + 4,110 semantic-review prints to:

- 106 exact-fingerprint candidates;
- 42 historical-official candidates;
- 44 name-wide official-errata candidates;
- 4,068 remaining semantic-review prints.

The high-confidence pre-semantic candidate set therefore rises from 150 to 192. Among the 168 historical Trainer prints sharing a name with a legal Expanded Trainer, 87 now have exact, historical-official, or name-wide official evidence.

The bridge does not generalize old Special Darkness Energy or Special Metal Energy into current Basic Energy. Those cards were historically legal against a different format boundary and their mechanics differ from Black & White-onward Basic Energy. Reference-required historical entries are also left out.

Source: Pokémon Organized Play, 2012 Modified-Legal Reprint List, last updated 2012-03-13.

Reproduce with:

python results/historical_reprint_bridge/reproduce.py
