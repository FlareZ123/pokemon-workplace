# Greedy Dice + Dream Ball: official ordering evidence audit (2026-10-12)

## Research question

The controlled [Greedy Dice / Dream Ball order-option model](../e31_greedy_order_option/) chooses which of two simultaneous face-down Prize-origin Items resolves first. Is that chooser and order directly established by a contemporary official ruling for **Greedy Dice + Dream Ball**, or extrapolated from related cases?

## Directly supported source facts

1. **Bundled Advanced Player's Rulebook v3.4 (2025-08-01), E-31, page 68:** effects that activate before a card enters the hand occur after seeing the previously face-down card and before placing it in hand. When two or more such cards are about to be put in hand, their effects are applied **one by one**. The printed example uses two Chansey Lucky Bonus cards. This section does **not explicitly specify** who chooses first among two distinct Prize-origin Item effects.
2. **Pokémon Japan Dream Ball FAQ (8-result query):** for a simultaneous two-Prize draw of Chansey (Lucky Bonus) and Dream Ball, **the Chansey's owner chooses which effect to process first**. This is a *closely related* owner-choice precedent, not a literal Greedy Dice/Dream Ball answer. Same FAQ confirms that two Dream Ball cards taken together can both resolve, each completed before the next, and that Dream Ball is optional and cannot be used with a full Bench.
3. **Pokémon Japan Greedy Dice FAQ (11-result query):** confirms both Greedy Dice can be used if taken together as the two Prizes for an EX Knock Out, that another Greedy Dice reached by a successful first Greedy Dice may be used, and that Greedy Dice is optional. A Greedy Dice Prize can resolve before the opponent promotes a replacement Pokémon after a Knock Out. These establish recursive and timing behavior, but give **no explicit paired-Dream-Ball chooser** in the inspected search results.
4. **Both official FAQ categories:** face-up Prizes exposed by Town Map cannot activate the respective Greedy Dice or Dream Ball face-down-only clauses.

Official source URLs, inspected 2026-10-12:
- [Dream Ball official Japanese FAQ](https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%89%E3%83%AA%E3%83%BC%E3%83%A0%E3%83%9C%E3%83%BC%E3%83%AB&regulation_faq_main_item1=all)
- [Greedy Dice official Japanese FAQ](https://www.pokemon-card.com/rules/faq/search.php?freeword=%E6%AC%B2%E5%BC%B5%E3%82%8A%E3%83%80%E3%82%A4%E3%82%B9)
- Bundled `resources/advanced-players-rulebook.md`, v3.4 E-31, pages 67–68.

## Assessment

**Strongly supported:** The two before-hand effects do not resolve simultaneously; each must complete before the next. An effect-resolution order can matter for Bench occupancy and recursive Prize-taking. The already-published exact conditional results for the model's fixed `Greedy-first` and `Dream-first` policies remain valid as **model results under those order inputs**.

**Reasonable extrapolation requiring a direct source:** The Prize-taking player may freely select either Greedy Dice or Dream Ball first, exactly as the Chansey/Dream Ball FAQ permits for that pairing. The inspected Dream Ball and Greedy Dice FAQ searches do **not** provide an exact-match official answer. The lack of a hit is bounded to those queried official FAQ collections and should never be represented as proof that no ruling exists.

**Do not upgrade the experiment to unconditional legality.** Keep the chooser assumption visible in `results/e31_greedy_order_option/`; if a judge/rules authority resolves this precise pairing differently, only the reachable-order set changes, while the branch transition and probability calculations can be reused.

## Competitive relevance

An otherwise high-value exact Prize-chain combo may depend on a choice of sibling effect order that has not been directly verified. In deck optimization, treat `Greedy-first` as a conditional legal-action assumption rather than a guaranteed play against an opponent. Ask for an exact-pair ruling when tournament legality hinges on the branch. These sources do not measure matchup wins, turn frequencies, or value of the required deck slots.

## Reproduction of the source audit

Review Advanced Rulebook v3.4 E-31; open the two linked official FAQ search pages. Confirm the cited Chansey/Dream and two-Dream decisions among 8 Dream FAQ results, and both-Dice and recursive-Dice decisions among 11 Greedy FAQ results. Translate the Japanese answers with care. Recheck the sources when they are updated; search-result counts are time-dependent.
