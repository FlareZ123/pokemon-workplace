# Harto Raichu: Quick Ball draw-engine semantics

## Question

Harto Miki's list can search three materially different draw engines with Quick Ball: Crobat V, Dedenne-GX, and Squawkabilly ex. This result pins down their execution semantics from the bundled card data before extending the combinatorial planner.

Implementation: `tools/raichu_draw_engine_profiles.py`  
Regression: `results/raichu_draw_engine_profiles/reproduce.py`

## Card-grounded profiles

| Card | Ability | Activation | Hand effect | First-turn only | Forest Seal host |
| --- | --- | --- | --- | --- | --- |
| Crobat V `swsh3-104` | Dark Asset | hand to Bench | draw until 6 | no | yes |
| Dedenne-GX `sm10-57` | Dedechange | hand to Bench | discard hand, draw 6 | no | no |
| Squawkabilly ex `sv2-169` | Squawk and Seize | announced during first turn | discard hand, draw 6 | yes | no |

Forest Seal Stone `swsh12-156` grants Star Alchemy only to the Pokémon V it is attached to, so Crobat V is the only host in this trio.

## Hand-size transitions

The preceding Raichu models use a seven-card action hand after setup plus one ordinary draw. Quick Ball leaves hand and its mandatory one-card payment leaves hand.

When the engine is searched from deck, searching adds the engine and benching it removes it again:

- searched Crobat V leaves five cards, then Dark Asset draws 1 and preserves those five;
- searched Dedenne-GX leaves five cards, then Dedechange discards 5 and draws 6;
- searched Squawkabilly ex leaves five cards, then Squawk and Seize discards 5 and draws 6 during the first turn.

When the engine was already in hand, benching it after Quick Ball leaves four cards:

- Crobat draws 2;
- Dedenne discards 4 and draws 6;
- Squawkabilly discards 4 and draws 6 in its first-turn window.

If the engine is already in play, Crobat and Dedenne cannot re-create their hand-to-Bench triggers. Squawkabilly differs because its Ability is an announced first-turn action rather than an entry trigger, so an in-play Squawkabilly can still reset the post-Quick-Ball hand.

## Interpretation

These cards are not interchangeable Quick Ball draw-engine edges.

Crobat preserves exact hand identities and creates a Forest Seal host, while its draw volume depends on whether the search itself supplied Crobat. Dedenne gives a six-card fresh sample while destroying the residual hand. Squawkabilly shares the reset shape but has different timing geometry.

The source location of the same engine also changes continuation value. A held Crobat after Quick Ball draws two, while a searched Crobat draws one.

## Evidence

The compiler loads the exact bundled card records, verifies their effective paper-Expanded legality, checks the relevant Ability text fragments, and verifies Forest Seal Stone's Pokémon V host wording.

The reproducer asserts all three profiles and the source-location hand transitions.

## Next quantitative step

The K0 discard planner currently treats failure to find a deck-resident Crobat V as terminal. A stronger planner should choose among Crobat V, Dedenne-GX, and Squawkabilly ex after K1, preserve the first-turn restriction, and distinguish searched engines from engines already held or in play.
