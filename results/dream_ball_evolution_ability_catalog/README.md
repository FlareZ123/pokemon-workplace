# Dream Ball Evolution-Pokémon Ability geometry

## Question

How often can Dream Ball's unrestricted Pokémon search bypass an evolution stack and place an Evolution Pokémon whose Ability is positionally compatible with immediate Bench entry?

A conservative text-geometry audit finds that this is a broad interaction family, not an isolated Pidgeot ex trick.

Implementation: `tools/dream_ball_evolution_ability_catalog.py`  
Regression: `results/dream_ball_evolution_ability_catalog/reproduce.py`

## Method

The catalog scans exact effectively legal Pokémon prints in Expanded-marked sets using the repository's current legality classifier and search-tag compiler.

It keeps only Pokémon classified as Evolution Pokémon and records every Ability. The classifier then looks only at explicit entry/source/position wording and assigns one geometry:

- `in_play`: no explicit source or position restriction recognized;
- `bench_required`: explicitly requires this Pokémon to be on the Bench;
- `active_required`: explicitly requires this Pokémon to be Active;
- `hand_evolution_trigger`: triggers when this Pokémon is played from hand to evolve;
- `hand_bench_trigger`: triggers when played from hand onto the Bench;
- `off_board_zone`: explicitly works from hand, discard, deck, or Prize cards.

For Dream Ball direct Bench entry, only `in_play` and `bench_required` are called geometry-compatible.

This is deliberately weaker than "the Ability works." Other predicates, once-per-turn history, resource costs, locks, and game-state conditions still have to be checked by downstream semantics. Activation timing is classified separately: a leading event clause such as `Once during your turn, when ...` remains event-triggered because the once-per-turn phrase limits frequency rather than creating a freely callable action.

## Audited counts

The current bundled paper-Expanded pool contains:

- 1,539 exact legal Evolution-Pokémon Ability rows across 1,539 exact prints;
- 1,152 `in_play` rows;
- 23 `bench_required` rows;
- 159 `active_required` rows;
- 188 `hand_evolution_trigger` rows;
- 17 `off_board_zone` rows.

Therefore 1,175 exact rows are compatible with Dream Ball's direct Bench geometry.

Among those 1,175 compatible rows:

- 559 are classified as freely callable turn actions;
- 563 are classified as passive or continuous;
- 53 are classified as event-triggered.

These are card-print counts, not unique strategic effects. Reprints and functionally similar cards can appear more than once.

Across all 1,539 Evolution Ability rows, the timing classifier now reports 617 turn actions, 241 triggered Abilities, and 681 passive/continuous Abilities. The previous lexical precedence produced 645 turn actions and 213 triggered rows. The correction therefore reclassifies 28 exact rows without changing any geometry assignment.

## Named witnesses

Pidgeot ex `sv3-164` with Quick Search is an `in_play` turn-action witness. Dream Ball can put this Stage 2 directly onto the Bench as a one-card stack; its Ability text has no play-from-hand or Active-only gate.

Vileplume `xy7-3` with Irritating Pollen is an `in_play` passive witness. Its Ability blocks each player from playing Item cards from hand while Vileplume remains in play.

Team Rocket's Crobat ex `sv10-122` with Biting Spree is the counterexample. Biting Spree explicitly triggers when the card is played from hand to evolve one of your Pokémon. Dream Ball can place the Crobat ex card in play, but that direct placement does not satisfy the Ability's hand-evolution trigger.

The regression also confirms that the current Flapple Apple Drop ban overlay is respected. The banned `swsh2-22`, `swsh45sv-SV013`, `swsh10tg-TG02`, and `swshp-SWSH022` prints do not enter the catalog even if stale database metadata would otherwise expose them.

## Official-rule support

The official Japanese Dream Ball page states that the Item, when taken from a face-down Prize before hand entry, searches the deck for one Pokémon and puts it onto the Bench:

https://www.pokemon-card.com/card-search/details.php/card/39645/regu/XY

The official Dream Ball FAQ also states that Dream Ball cannot be used when the Bench is full, and that two Dream Balls taken together are resolved one after the other:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%89%E3%83%AA%E3%83%BC%E3%83%A0%E3%83%9C%E3%83%BC%E3%83%AB&regulation_faq_main_item1=all

The official Vileplume page gives the equivalent Irritating Pollen text, which prevents both players from playing Items from hand while Vileplume is in play:

https://www.pokemon-card.com/card-search/details.php/card/33555/

## Finding

Dream Ball is a general topology-bypass connector.

Its strategic ceiling is poorly represented by treating it as merely "search one Pokémon." For Evolution Pokémon, it can also bypass prerequisite stages and the normal evolution-time constraint. Whether that matters depends on the selected card's Ability geometry and remaining conditions.

The 1,175-row compatibility set is therefore best treated as a candidate surface for further analysis, not as 1,175 automatically strong combos.

## Limits

The geometry classifier is intentionally narrow and lexical. It does not prove full semantic usability.

`in_play` means only that no incompatible explicit source/position wording was recognized. An Ability may still require another Pokémon, Energy, damage, a Stadium, a matchup condition, or some other state.

The catalog operates at exact print level and does not collapse reprints to gameplay fingerprints.

It does not rank strategic value. Pidgeot ex and Vileplume illustrate high-impact possibilities; many compatible rows will be irrelevant or weak.

A next useful layer is source-aware line execution for especially important candidates, beginning with Dream Ball establishing Vileplume's hand-scoped Item lock from the Prize zone.
