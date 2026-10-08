# Rule-grounded historical Trainer semantics

## Question

Can current rules resolve any of the four remaining semantic-review rows in the official historical reprint benchmark without using fuzzy wording similarity?

## Result

Yes. Seven wording families can be normalized from explicit current rules while preserving the benchmark's known negative boundaries.

### Fisherman

Historical Fisherman `ecard3-125` says to choose four basic Energy from the discard pile, take all if fewer are available, show them to the opponent, and put them into hand. Current Fisherman such as `sm7-130` says to put four basic Energy from the discard pile into hand.

Two current rules remove the apparent semantic differences:

1. Advanced Player's Rulebook II-A says that when card text specifies a number but fewer objects are available, apply the closest possible number.
2. The official Pokémon TCG glossary says discard-pile cards are always face up and anyone may inspect them at any time, so revealing selected discard-pile cards adds no information.

The normalizer therefore maps the two exact historical Fisherman effect strings in the local archive to the current effect string. It does not apply a generic text rewrite to other cards.

### Life Herb

Historical no-exclusion Life Herb `pl1-108` and `hgss2-79` remove all Special Conditions and six damage counters. Current Life Herb `sm7-136` heals 60 damage and removes all Special Conditions.

Advanced Player's Rulebook C-06 defines healing as removing damage counters and says to remove all counters if fewer than the stated healing amount are present. C-07 defines one damage counter as 10 damage. Six counters therefore correspond to 60 damage under current terminology, including the old "all if fewer" clause.

The normalizer is deliberately limited to the exact no-exclusion wording. The historical `ex5-90` and `ex6-93` Life Herb printings exclude Pokémon-ex targets and remain distinct, preserving the repository's current format-relative negative evidence.

### Moomoo Milk

Historical Moomoo Milk `hgss1-94` says that each heads removes three damage counters from the chosen Pokémon. Current Moomoo Milk `sm8-185` says that each heads heals 30 damage.

Advanced Player's Rulebook C-06 defines healing as removing damage counters. C-07 defines each damage counter as 10 damage. For each heads, removing three damage counters is therefore exactly a 30-damage heal under current terminology, including the ordinary rule that healing removes all available damage if less than the stated amount remains.

The normalizer maps only the exact historical Moomoo Milk effect string to the current effect string.

### VS Seeker

Historical VS Seeker `ex6-100` and `pl3-140` say to search the discard pile for a Supporter, show it to the opponent, and put it into hand. Current `xy4-109` says to put a Supporter from the discard pile into hand.

The discard pile is a public zone: Pokémon's official glossary says its cards are always face up and anyone may inspect them at any time. The historical reveal therefore contributes no additional observation. Advanced Player's Rulebook D-04 also explains that required card choices can be implicit in wording, so both effects select one Supporter when the effect is usable.

The normalizer maps only the exact historical VS Seeker effect string to the current effect string.

### Bill's Maintenance

Historical Bill's Maintenance `ecard1-137`, `ex14-71`, `ex6-87`, and `pop5-6` say that if any cards remain in hand, shuffle one into the deck and then draw three. Current `sm7-126` says to shuffle a card from hand into the deck and, if that happens, draw three.

Advanced Player's Rulebook B-03 prevents a Supporter from being played when carrying out its effect would not change the game state. Therefore, the apparent historical empty-hand branch does not create an extra legal action under current rules. Whenever the effect is playable, both versions move exactly one hand card into the deck and then draw three. E-20 preserves the dependency between the first action and the draw.

The normalizer maps only the exact historical Bill's Maintenance effect string to the current effect string.

### Underground Expedition

Historical Underground Expedition `ecard3-140` and `pl2-97` and current `sm7-150` all inspect the bottom four cards of the deck, move two of those cards into the hand when two are available, and return the remaining inspected cards to the bottom in any order.

The wording differences are covered by current numbered-choice semantics. Advanced Player's Rulebook II-A applies the closest possible number when fewer objects exist, and D-04 explains that a required choice can be implicit in effect wording. No version exposes a different card set or destination.

The normalizer maps only the two exact historical Underground Expedition effect strings to the current effect string.

### Lucky Egg

Historical Lucky Egg `pl4-88` contains the old Tool reminder telling the player to attach Lucky Egg only to a Pokémon without another Tool and to discard Lucky Egg when that Pokémon is Knocked Out. Current `swsh1-167` uses the modern generic Tool attachment reminder. Advanced Player's Rulebook B-02 now supplies those attachment, one-Tool-per-Pokémon, persistence, and Knock Out discard semantics as category rules.

The historical effect begins with “When the Pokémon ... is Knocked Out,” while the current print begins with “If the Pokémon ... is Knocked Out.” Advanced Player's Rulebook E-04 explicitly says these wordings use the same Knock Out trigger rules.

After those two exact, name-scoped normalizations, both prints have the same current semantic fingerprint.

## Benchmark consequence

After composing this normalizer into `current_card_semantics.py`:

- Fisherman `ecard3-125` moves from `semantic_review` to `exact_fingerprint_candidate`.
- Life Herb `pl1-108` moves from `semantic_review` to `exact_fingerprint_candidate`.
- the benchmark's remaining semantic-review gap falls from **4 to 2**;
- both remaining rows are the older Pokédex wordings with "up to 5 cards";
- the two Pokémon-ex-excluding Life Herb prints stay `known_non_equivalent`.

The broader archive also resolves the same exact no-exclusion Life Herb wording on `hgss2-79`, the same public-discard Fisherman wording on `hgss1-92`, historical Moomoo Milk `hgss1-94`, historical VS Seeker `ex6-100` and `pl3-140`, four historical Bill's Maintenance prints, historical Underground Expedition `ecard3-140` and `pl2-97`, and historical Lucky Egg `pl4-88`.

## Why Pokédex remains unresolved

The older Pokédex wording lets the player look at "up to 5" cards, while the later wording instructs the player to look at the top five. Current D-05 gives "up to" explicit choice semantics. Even if looking at more cards seems strategically favorable, hidden-information state is part of game state and the repository now models information explicitly. This result therefore does not erase that difference without stronger official evidence.

## Implementation

`tools/trainer_rule_semantics.py` contains only exact-string, exact-name transformations supported by the rules above, including Moomoo Milk's three-counter to 30-damage healing equivalence and VS Seeker's public-discard retrieval equivalence. `tools/current_card_semantics.py` applies it after print errata, legacy Tool normalization, and Trainer category-boilerplate removal.

The reproducer verifies positive Fisherman and Life Herb convergence, the two Life Herb negative witnesses, the unresolved Pokédex boundary, and the updated 76-row official benchmark partition.

## Evidence classes

**Rule fact.** A specified number uses the closest possible number when fewer objects exist.

**Rule fact.** A damage counter represents 10 damage, and healing removes damage counters up to the amount available.

**Official zone fact.** Discard-pile cards are face up and inspectable by either player.

**Historical official evidence.** The 2012 Modified-Legal Reprint List marked the benchmark Fisherman and no-exclusion Life Herb printings as usable without a reference card under the then-current policy.

**Methodological judgment.** These transformations are kept narrow and literal. They are evidence-backed semantic normalization, not a general natural-language equivalence engine.

## Sources

- Repository Advanced Player's Rulebook: `resources/advanced-players-rulebook.md`
- Pokémon TCG Glossary: https://www.pokemon.com/us/play-pokemon/about/pokemon-tcg-glossary
- 2012 Modified-Legal Reprint List: https://assets.pokemon.com/assets/cms/pdf/op/tournaments/2012/2012_modified_legal_reprints.pdf

## Next work

Treat the two Pokédex rows as an information-state question. A useful next test is whether the "up to 5" choice can produce any observable continuation that fixed-five inspection cannot reproduce, while preserving the fact that the player learns a different amount of hidden information.
