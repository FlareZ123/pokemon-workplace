# Copycat numerical-wording equivalence

## Question and result

Can the two unresolved pre-Black & White Copycat Supporter printings be
connected to the current Tournament Handbook's certified Copycat example
without broad fuzzy matching?

**Yes, under the current card-text semantics.** The historical cards
`col1-77` (Call of Legends) and `hgss1-90` (HeartGold & SoulSilver)
say to draw *a number of cards equal to the number of cards in the
opponent's hand*. The already certified source `ex7-83` (Team Rocket
Returns) says to *count* the opponent's cards and draw *that many*. The
remaining Supporter classification, shuffle, and draw instructions are
identical. The certified source `ex7-83` is explicitly designated
functionally identical to the Expanded-legal `sm7-127` in the
Tournament Handbook.

A guarded rewrite of those two exact source texts to the certified
source's wording makes five historical Copycat printings match the
certified source fingerprint, compared with three beforehand. The
central resolver classifies the two newly covered prints as
`official_semantic_candidate`. That label refers to the documented
transitive evidence chain, rather than a claim that the Handbook
individually lists those two prints.

## Evidence and method

- Database identities: `col1-77` and `hgss1-90` are historical
  `Trainer / Supporter` cards whose complete effect paragraph matches
  `SOURCE_TEXT` in `tools/copycat_number_wording.py`.
- The canonical positive pair is `ex7-83 -> sm7-127`, recorded by
  `tools/reprint_positive_evidence.py`, with its policy source in
  `tools/reprint_semantic_benchmark.py`.
- The guarded normalizer changes only those exact two IDs, requires the
  exact sentence and subtype, and preserves all other card attributes.
  A changed source text fails loudly.
- For each opposing hand size 0 through 60 and each available
  post-shuffle deck size 0 through 60, the two wordings request the
  same draw count; the same shortage rule applies. This is a local
  operational sanity check, not a substitute for complete game
  simulation.
- The reproducible regression confirms the normalized historical
  source fingerprint equals that of certified `ex7-83`, validates
  all five source identities, and checks the resolver's current
  classification.

## Limits

Only Copycat's count-synonym sentence is normalized. The proof does not
extend to other historical Supporters, and card-print legality remains
subject to the tournament's official interpretation of functional
identity. The operational test checks the numerical distinction,
while the exact agreement in remaining clauses is verified separately.

## Reproduce

`python -m results.copycat_count_equivalence.reproduce`

Source: [2023 Play! Pokémon Tournament Rules Handbook, §5.4.1.3](https://www.pokemon.com/static-assets/content-assets/cms2/pdf/play-pokemon/rules/play-pokemon-tournament-rules-handbook-10062023-en.pdf).

## Follow-up

The analogous question for Energy Recycle System concerns the
equivalence of its optional branch wording and whether public
discard-pile reveals add any gameplay-visible action. That should be
proved separately rather than inferred from this card family.
