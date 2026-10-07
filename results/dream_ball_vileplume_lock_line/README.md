# Dream Ball -> Vileplume source-scoped Item-lock line

## Question

Can Dream Ball establish Vileplume's Irritating Pollen without an Oddish/Gloom evolution stack, and if two Dream Balls were taken together, does the first Vileplume lock prevent the second Dream Ball from resolving?

The composed state model says the line is executable.

Regression: `results/dream_ball_vileplume_lock_line/reproduce.py`

## Card-text facts

Dream Ball `swsh7-146` is a special Prize-origin Item. When taken as a face-down Prize, before entering hand it searches the deck for one Pokémon and puts that Pokémon directly onto the Bench.

Vileplume `xy7-3` is a Stage 2 Pokémon with Irritating Pollen:

`Each player can't play any Item cards from his or her hand.`

The source phrase matters. The restriction is against Item play from hand rather than a global statement that no Item can resolve from any zone.

The repository's source-scope audit independently classifies Vileplume's restriction as `prohibited_source_zone="hand"`.

## Executed two-Dream-Ball line

The regression starts with two materialized Dream Ball instances in the ordered `prize_pending` queue, Vileplume `xy7-3` and Pidgeot ex `sv3-164` as exact deck targets, and an existing Active Pokémon.

The first Dream Ball:

1. moves from `prize_pending` into `resolving_trainer`;
2. selects the exact Vileplume target witness;
3. moves one Vileplume card class out of deck;
4. materializes that same copy directly as a one-card Stage 2 Bench object;
5. finishes and moves the same Dream Ball instance to discard.

At that point Irritating Pollen is in play and the second Dream Ball remains the head of `prize_pending`.

The second Dream Ball is then executed while Irritating Pollen is supplied as an active Item-play restriction. The source-scope check gives:

- Item from `hand`: blocked;
- Item from `prize_pending`: not blocked.

The second Dream Ball therefore begins legally, searches Pidgeot ex, puts that Stage 2 directly onto the Bench, and then enters discard.

Neither searched Pokémon passes through hand. Card-class totals are conserved across the complete chain.

## Official-rule support

The official Japanese Dream Ball page states the deck-to-Bench effect without restricting the searched Pokémon to Basic Pokémon:

https://www.pokemon-card.com/card-search/details.php/card/39645/regu/XY

The official Dream Ball FAQ states both that Dream Ball cannot be used with a full Bench and that two Dream Balls taken together can both be used, resolving the first before the second:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%89%E3%83%AA%E3%83%BC%E3%83%A0%E3%83%9C%E3%83%BC%E3%83%AB&regulation_faq_main_item1=all

The official Vileplume page gives the equivalent Irritating Pollen effect, preventing both players from playing Items from hand while Vileplume is in play:

https://www.pokemon-card.com/card-search/details.php/card/33555/

The Advanced Player's Rulebook also treats "can't play ... from hand" effects as effects on a player, which is consistent with retaining their stated source scope.

## Strategic significance

This is an Archetype-Line-Specific style interaction with several unusual properties:

- a face-down Prize can become a live connector during the Prize window;
- the connector bypasses a Stage 2 evolution stack and normal evolution timing;
- the searched Pokémon turns on a symmetrical Item lock immediately upon entering play;
- that new lock does not retroactively invalidate the already-resolving Dream Ball;
- a second Prize-origin Dream Ball remains outside the lock's prohibited hand source and can resolve afterward.

A graph representation that reduces Irritating Pollen to a scalar `item_play=False` would incorrectly delete the second Dream Ball edge. The source zone has to remain part of the action predicate.

## Finding

Lock state is source-sensitive, and lock establishment can occur inside a special-source action that the new lock itself would forbid from hand.

This strengthens the repository's broader caution against representing play channels as unconditional booleans. The legality of an Item action can depend on where that Item is being played from, and the relevant source can differ inside recursive Prize-resolution lines.

## Limits

The regression assumes the two Dream Balls have already been awarded and staged in the pending Prize queue. It does not model which Knock Outs produced those Prize awards.

It proves mechanical executability under the modeled card text and source-scope rules. It does not estimate how often the line occurs in real decks or whether allocating slots to Dream Ball and Vileplume is strategically worthwhile.

The terminal-precedence edge is now resolved by `results/post_prize_window_game_resolution/` from an official Jirachi Prism Star ruling. `results/dream_ball_terminal_rescue/` applies that phase rule to Dream Ball.
