# Search action legality and information-gain ordering

## Question

When a card says to search the deck, can a simulator treat the search edge as automatically available and immediately grant exact Prize information?

No.

Search-shaped actions have a legality boundary before the deck-inspection event. At the same time, absence of an eligible search target does **not** necessarily make a constrained search unusable.

This result separates three states that graph-style models can accidentally collapse:

1. the search zone is nonempty but contains no eligible target;
2. the search zone itself is empty;
3. a required destination or other pre-search condition is unavailable.

Implementation: `tools/search_action_legality.py`

Reproducer: `results/search_action_legality/reproduce.py`

## Rules basis

The Advanced Player's Rulebook establishes several relevant rules.

- Items, Supporters, announced Abilities, and voluntary Stadium effects cannot be used when resolving their effect would not change the game state.
- A constrained deck search may select fewer than the stated number, including zero. An unrestricted search for arbitrary cards must take the specified number.
- Looking through the deck for a search exposes its contents to the searching player, followed by shuffling.
- If a direct-to-Bench attack effect would put Pok√©mon from the deck onto a full Bench, the attack ends before the player searches the deck. A Trainer card or Ability with the same kind of direct-to-Bench effect cannot be used while the Bench is full.
- Attacks may still be used when part of their instructions cannot be applied, unless a card-specific condition says otherwise.

These rules are enough to show that `search exists` and `search executes` are different facts.

## Official Q&A anchors

The Japanese official Q&A supplies a particularly useful pair of rulings for Monster Ball-style constrained searches.

- A player may use Monster Ball or the referenced Supporter even when they already know the deck contains no Pok√©mon.
- Monster Ball cannot be used when the deck has zero cards.

Those two rulings isolate target absence from zone emptiness. A nonempty constrained search can legally resolve even when its eligible target set is empty, while an empty deck removes the search action entirely for this sole-effect Trainer case.

Official search page:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%9B%E3%83%BC%E3%83%BC%E3%83%AB&page=3&regulation=all&regulation_faq_main_item1=all

Empty-deck FAQ:

https://www.pokemon-card.com/rules/faq/details.php?id=1095

A separate Ultra Ball Q&A says that if the search finds no Pok√©mon, the cards discarded to use Ultra Ball are not returned; Ultra Ball was still used. This is consistent with targetless constrained-search resolution rather than rollback.

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%8F%E3%82%A4%E3%83%91%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%AB&regulation_faq_main_item1=all

The official Energy Retrieval Q&A provides the public-zone contrast: Super Energy Retrieval cannot be used when the discard pile contains no eligible Energy, while one eligible Basic Energy is enough to make the action usable.

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%A8%E3%82%B9%E3%82%AH%E3%83%8D%E3%82%B2%E3%83%BC%E3%83%88%
shows the direct-to-Bench contrast. With a full Bench, Bowl Town's effect cannot be used. The same search page confirms that when Bowl Town or Clavell has room to resolve but finds no eligible Basic Pok√©mon, the player shuffles and ends the search without a target.

## Core finding 1: a targetless constrained search can still be an information action

For a nonempty deck with zero eligible targets, `constrained_search_to_hand()` returns:

- action legal;
- full deck inspected;
- no material target moved;
- exact Prize composition acquired under the repository's skilled-tracking assumption.

This means `search success` is at least two dimensional:

- observation success;
- material target success.

A search can succeed on the first dimension and fail on the second.

## Core finding 2: empty deck and no eligible target are not equivalent

With an empty deck, a sole-effect Item search is rejected before the action and therefore grants no deck inspection and no information update.

A planner that only checks `eligible_targets == 0` cannot distinguish this state from the legal targetless case above.

The minimum state therefore needs at least:

-∞ÄÅ—Ω—Ö∞ÅçÖ…ëÃÅ…ïµÖ•π•πúÅ•∏Å—°îÅëïç¨Ï(¥ÅçΩ’π–ÅΩ»Åï·•Õ—ïπçîÅΩòÅï±•ù•â±îÅ—Ö…ùï—ÃÏ(¥ÅçÖ…êµÕ¡ïç•ô•åÅÖç—•Ω∏Å¡…ï…ï≈’•Õ•—ïÃÏ(¥ÅëïÕ—•πÖ—•Ω∏ÅçÖ¡Öç•—‰Å›°ï…îÅ…ï±ïŸÖπ–Ï(¥Å•πôΩ…µÖ—•Ω∏ÅÕ—Ö—îÅâïôΩ…îÅÖπêÅÖô—ï»Å—°îÅï·ïç’—ïêÅÕïÖ…ç†∏(