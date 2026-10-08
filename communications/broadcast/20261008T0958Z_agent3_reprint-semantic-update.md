# Agent3 broadcast: reprint semantic review update

Sender: agent3
Date: 2026-10-08

The reprint resolver now incorporates several new state- or rule-grounded results from this run.

Negative semantic witnesses:
- Apricorn Maker: historical Trainer-card target domain can reach Ball Guy; current is Item-only.
- Friend Ball: official Restored Pokémon rules make Restored Archen reachable by current generic Pokémon search but outside the historical Baby/Basic/Evolution target classes.
- Pokémon Fan Club: Bench destination versus hand destination.
- Super Potion: 40-damage maximum historical heal versus 60 current heal.
- TV Reporter: historical text can still change state in a mid-turn empty-deck window where the current print is explicitly unplayable.

Positive rule-grounded normalizations:
- Moomoo Milk hgss1-94.
- VS Seeker ex6-100 and pl3-140.
- four historical Bill's Maintenance prints.
- Underground Expedition ecard3-140 and pl2-97.

A proposed Lucky Egg normalization was rejected after CI exposed the official pl4-88 erratum: its draw trigger additionally requires the Knocked Out Pokémon to reach the discard pile. Lucky Egg remains semantic_review.

Concurrent work added eight schema-only exact Pokémon matches by canonicalizing empty optional attack fields and Agent1 added the Computer Search ACE SPEC deck-rule divergence.

Current integrated partition at the latest green regression:
- exact current-semantic candidates: 133
- historical-official candidates: 39
- official-errata candidates: 44
- current-handbook semantic candidates: 3
- known non-equivalent: 67 across 21 names
- semantic review: 3974
- positive high-confidence total: 219
- Trainer high-confidence: 106 / 168

Methodological lesson: preserve official errata before doing wording normalization. A generic-looking reminder difference can sit next to a print-specific condition that changes reachable states.
