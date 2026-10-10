# Setup eligibility and format-legality alignment

## Finding

`tools/setup_eligibility.py` previously used a private partial
`_effective_status` implementation that recognized metadata bans and the
dated official overlay, but did **not** recognize the seven Expanded-scope
promotional cards whose printed text explicitly says they cannot be used in
official tournaments.

Four of the seven prohibited prints are Basic Pokémon:
`swshp-SWSH136` Mimikyu δ, `swshp-SWSH138` Hydreigon C,
`swshp-SWSH144` Greninja ★, and `xy12-112` Imakuni?'s Doduo.

Before the correction, these four exact prints could be counted as legally
placeable forced opening Basics, despite the format's exclusion policy.
The resulting setup catalog also overstated its legal print population by
seven. This is an eligibility-catalog error; it does not, by itself, prove
that any previously published individual deck-level simulation included
one of the affected prints.

## Correction

Setup eligibility now delegates its print status check to
`tools.build_expanded_legality_baseline.classify_effective_legality`. This
shares the existing precedence for current bans, card-level bans, explicit
official-tournament prohibitions, and set-level fallback.

| Snapshot measure | Previously | Corrected |
| --- | ---: | ---: |
| Legal Expanded print records | 14,836 | **14,829** |
| Legal Basic Pokémon print records | 7,259 | **7,255** |
| Legally placeable forced Basic print records | 7,258 | **7,254** |
| Tournament-prohibited promotional prints mistakenly allowed | 7 | **0** |

The sole legal Basic with a separate printed setup prohibition remains
Shedinja `swsh4-66` (Shell Survival). The six optional setup-exception
prints, including Cinderace and Talonflame, are unchanged.

## Evidence and reproduction

The exact seven exclusions are printed in `resources/cards/en/xy12.json`
and `resources/cards/en/swshp.json`. Their rules contain the official
tournament-use prohibition. The original legality-baseline audit documents
this print-specific source distinction at
[expanded_legality_baseline](../expanded_legality_baseline/).

Run `python -m results.setup_legality_catalog_alignment.reproduce`.
The regression reconstructs the legal snapshot independently using the
shared legality classifier, checks the exact seven printed exclusions and
their missing card-level Expanded fields, and checks the complete forced
starter set against the Basic-card population minus the printed Shedinja
exception.

## Scope

This is a **catalog correctness** finding. The setup catalog enumerates
physical prints under the current snapshot and is separate from
deck-construction legality, deck-specific start probability, and
a complete treatment of historical release dates or regional eligibility.
Future official ban changes still require updating the shared legality
source.
