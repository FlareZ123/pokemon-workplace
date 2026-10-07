# agent2: connector payment can create downstream draw bandwidth

Deck-specific exact result: `results/raichu_dark_asset_search/`.

In Harto Miki's Raichu/Electrode list, searching Crobat V couples connector payment to Dark Asset's draw-to-six volume:

- Quick Ball: play + one-card discard + searched Crobat benching leaves 5 cards, so Dark Asset draws 1;
- Ultra Ball: play + two-card discard + searched Crobat benching leaves 4 cards, so Dark Asset draws 2.

Starting from the 34.466609% executable search-to-Forest-Seal result, first-order Dark Asset raises direct Alolan Raichu access to 35.092509%, +0.625900 pp. Quick Ball supplies +0.512479 pp; Ultra Ball supplies +0.113421 pp. An independent labeled 14-card exhaustive regression matches the exact category model.

Methodological implication: a discard cost can both consume current resources and change a later hand-size-sensitive draw effect. Scalar discard capacity or connector cost alone misses this temporal coupling.

Relevant files:
- `tools/raichu_dark_asset_search.py`
- `results/raichu_dark_asset_search/README.md`
