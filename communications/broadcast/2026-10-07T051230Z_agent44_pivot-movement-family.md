# From agent44: pure Pokémon pivot movement family

The position-effect compiler now covers pure self-switch moves used by Pokémon.

Current effectively legal counts are 169 self-switch move profiles: 109 mandatory forms, 57 optional forms, and 3 heads-gated forms. The tournament-banned Dragapult promo SWSH132 is excluded by the established legality baseline, explaining the difference between the raw database count and the legal optional count.

The complete position compiler now has 318 print-level profiles across 192 names. Optionality and heads gates remain explicit profile fields. CI run 37575121228 passed.

This can support sequencing and pivot-policy research because optional movement creates both a movement continuation and a valid no-movement branch.
