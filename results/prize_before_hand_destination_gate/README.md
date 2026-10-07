# Before-hand Prize effects require an actual hand-bound Prize

## Question

Can a Prize-origin effect whose text says "before you put it into your hand" still activate when another effect redirects that taken Prize to discard or the Lost Zone?

For the checked Expanded witnesses, no.

Implementation change: `tools/before_hand_prize_executor.py`  
Regression: `results/prize_before_hand_destination_gate/reproduce.py`

## Official rulings

The Japanese Pokémon Card Trainers Website provides direct witnesses:

- if Treasure Energy is taken while the opponent's Lost Block applies, Treasure Energy cannot be attached by its Prize-origin effect;
- if Treasure Energy is taken for a Knock Out affected by Billowing Smoke, Treasure Energy cannot be attached;
- if Chansey is taken for a Knock Out affected by Billowing Smoke, Lucky Bonus cannot be used.

These answers make the "before you put it into your hand" destination condition mechanically meaningful. A card redirected somewhere else never enters that trigger window.

Official Q&A searches:

- https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%88%E3%83%AC%E3%82%B8%E3%83%A3%E3%83%BC%E3%82%A8%E3%83%8D%E3%83%AB%E3%82%AE%E3%83%BC&regulation=all
- https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%A9%E3%83%83%E3%82%AD%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%8A%E3%82%B9&regulation=all

## Executor change

The shared before-hand executor now accepts `pre_hand_destination`, defaulting to `hand` for compatibility.

When a direct Prize trigger is used, or a Prize-origin Item begins resolving, the trigger window is legal only when `pre_hand_destination == "hand"`.

If the player does not use a direct trigger, the same argument also tells the executor where the exact pending card must physically go. This lets an upstream replacement decision route the card to discard or Lost Zone without passing it through hand.

## Regression

The regression compiles the repository's actual Prize-origin profiles and checks:

- Chansey under Billowing Smoke cannot use Lucky Bonus; declining the trigger sends the same physical card to discard;
- Treasure Energy under Lost Block cannot attach itself; declining sends it to the Lost Zone;
- Dream Ball cannot begin its Prize-origin Item play while Billowing Smoke redirects it to discard;
- ordinary hand-bound Treasure Energy still attaches normally;
- all resolved branches preserve physical card totals.

## Architectural implication

A `prize_pending` card needs a planned ordinary destination before E-31-style text is evaluated.

The timing chain is:

`Prize selected -> identity learned -> destination replacements resolved -> hand-bound before-hand effects -> final physical move`.

This preserves the existing information window while preventing a redirected Prize from receiving effects whose own wording presupposes imminent hand entry.
