# Maintenance: conditional two-card shuffle and draw equivalence

## Historical comparison

Base Set Maintenance (`base1-83`) and Base Set 2 (`base4-112`) instruct the player to shuffle two **other** hand cards into their deck as a prerequisite to drawing one card. XY Furious Fists (`xy3-96`) and XY Evolutions (`xy12-79`) explicitly say to shuffle two hand cards into the deck, explain that the Item cannot be played with fewer than two eligible hand cards, then draw one.

When the played Trainer is removed from the hand as it is played, the historical phrase *other cards* describes the same two-card selection as the XY wording. With fewer than two remaining hand cards, both effects are unusable. With two or more, each combination of two hand cards is a legal choice and all permutations of the enlarged deck are equally likely; the player draws its top card. Even if the starting deck was empty, the selected cards provide a nonempty deck before the draw.

## Reproducible model

`tools/maintenance_shuffle_equivalence.py` implements the two texts independently. It enumerates 24 states: hands with zero through five other uniquely identified physical cards, and decks with zero through three uniquely identified cards. For every legal two-card choice it enumerates all resulting shuffled deck orders with exact rational conditional probabilities. It compares chosen cards, drawn card, hand contents and deck order, including probabilities.

Run `python -m results.maintenance_shuffle_equivalence.reproduce`. Windows CI is `.github/workflows/validate-maintenance-shuffle-equivalence.yml`. [Windows run 38732326449 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38732326449).

## Limits

The two pre-Black & White Maintenance records `base1-83` and `base4-112` now normalize through `tools/maintenance_current_semantics.py` to the same current-semantic fingerprint as `xy3-96` and `xy12-79`. The full reprint resolver has moved them from `semantic_review` to `exact_fingerprint_candidate`. Aggregate regression [38732464795](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38732464795) passes, with 226 high-confidence candidates overall and 3,957 still needing semantic review. All changes are exact-print guarded and immutable.

This is a **conditional state-transition proof** assuming the played Trainer is outside the hand during its own effect. [The Pokémon Company's Black & White introduction](https://www.pokemon.com/uk/pokemon-tcg/black-white) explicitly describes Item as the new name for old Trainer cards, citing Poké Ball and PlusPower, and explains the modern Trainer subclass structure. Applying this category-wide rule to Maintenance is consistent with treating the older plain Trainer print as an Item, provided it has not been redesignated as another Trainer subclass. Old-print paper Expanded acceptance remains subject to applicable reprint equivalence and tournament policy. The official generic-category statement alone does not certify specific Maintenance copies. The simulation does not estimate a deck's win rate.

The audit does not assert equivalence of other reprints with different effect text or categories.
