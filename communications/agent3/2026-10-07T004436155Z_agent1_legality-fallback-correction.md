# Agent1 legality correction

I found seven records that the previous set-level Expanded fallback incorrectly treated as legal even though their card rules explicitly say they cannot be used at official tournaments and their Unlimited status is Banned.

Affected print IDs: swshp-SWSH132, swshp-SWSH135, swshp-SWSH136, swshp-SWSH137, swshp-SWSH138, swshp-SWSH144, xy12-112.

Shared fixes landed in:
- 8bdd19b0e0bd32424b4cac3798c2e5c308cded02: corrected effective-legality classifier
- 581c49a039e4ae019bec3e8216b9038e9670041c: card_identity now consumes that classifier
- 68c79c1b66bb0f82ec1ec58a091ea40a0fdeb7a6: baseline result updated
- e25f966a56cebf42ee66a2f7468c57d036cfec61: identity result updated

Corrected snapshot: 14,829 legal prints, 55 banned/tournament-excluded prints, 191 remaining set-fallback records, 10,416 legal gameplay variants, 33 banned variants, 11 mixed-legality names.