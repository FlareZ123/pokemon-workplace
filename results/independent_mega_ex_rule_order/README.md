# Independent XY Mega and Pokémon-EX rule order

## Question

Does the 2021 Celebrations Classic Collection M Rayquaza-EX
cel25c-76_A differ materially from its original Expanded-legal
XY Roaring Skies xy6-76 print, or is its semantic-review
status caused by card-data serialization order?

## Result

Both records have identical name, type, subtypes, Ancient Trait
Delta Evolution, HP, evolution prerequisite, attack, weakness,
resistance, retreat cost, and both printed Pokémon rules.
The **only** gameplay-fingerprint difference is the order of
their two printed rule-field strings:

- Mega Evolution rule: ending the turn upon Mega Evolution;
- Pokémon-EX rule: opponent takes two Prizes upon its Knock Out.

The 2021 source lists EX first, Mega second; its XY original
lists Mega first, EX second. These independently conditional
rule statements apply at distinct event windows and are
conjunctive. Reversing their order cannot change the board
transition or play permission they specify.

A full English-card corpus scan finds **85** records with the
canonical [Mega, EX] exact pair and exactly **one** reversed
pair, cel25c-76_A.

## Conservative normalization

tools/independent_mega_ex_rule_order.py recognizes only these
two complete rule strings on a Pokémon with both MEGA and EX
subtypes. It canonicalizes just the reversed exact pair.
Other rule lists, mixed rules, and cards of different subtypes
are left untouched, because effect order could matter
elsewhere.

Composing the normalization into
tools/current_card_semantics.py makes cel25c-76_A an
exact current-semantic fingerprint candidate pointing to
original legal Expanded print xy6-76.

Resolver counts move:

| Class | Before | After |
|---|---:|---:|
| Exact fingerprint candidates | 133 | 134 |
| Semantic-review | 3,964 | 3,963 |
| Total high-confidence candidates | 219 | 220 |

Of the 243 outside-set prints carrying Expanded: Legal
metadata, exact matches increase 118->119 and semantic
review decreases 36->35. Neither current official-errata
nor negative classifications change.

## Reproduction and boundaries

Run python -m results.independent_mega_ex_rule_order.reproduce.

Regression checks exhaustive exact-pair ordering, the
unedited source text, idempotence, original/new fingerprint
equality, legal target presence, and resolver classification.

The result establishes local card-text semantic equivalence,
rather than independent tournament-policy certification.
The correct source date remains 2021-10-08 under the
separate physical source-release gate.

References:
- Bundled English card records for cel25c-76_A and xy6-76.
- Bundled Advanced Player's Rulebook A-05 (evolution),
  D (Knock Outs), II D-18 (Rule Boxes).
- Official Celebrations checklist:
  https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/checklist/25th_web_cardlist_en.pdf
