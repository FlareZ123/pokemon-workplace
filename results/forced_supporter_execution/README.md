# Hand Control: forced Supporter play is a nested out-of-turn transaction

## Question

How should a simulator represent Hypno `xy3-36` / Hand Control, which makes the opponent play a Supporter during Hypno's attack?

It needs several roles. The outer turn owner, the player who plays the Supporter, the player controlling most decisions, hidden-information ownership, and the physical Supporter transaction can differ.

Implementation: `tools/forced_supporter_execution.py`  
Regression: `results/forced_supporter_execution/reproduce.py`

## Corpus finding

A conservative scan of the effectively legal paper Expanded pool finds one direct effect with the exact forced-play wording: `Hypno xy3-36 / Hand Control`.

Hand Control makes the opponent actually play the selected Supporter during Hypno's attack. This differs from Mimikyu Impersonation and Liepard Silent Claw, which execute a Supporter body as an attack effect.

## Split authority from official rulings

The Japanese official Hand Control Q&A family is extensive:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%B9%E3%83%AA%E3%83%BC%E3%83%91%E3%83%BC&page=6&regulation=all&regulation_faq_main_item1=all

It establishes several distinct roles.

- Hypno's owner controls Supporter choices and targets.
- The opponent remains the Supporter player. A Kahili ruling says that opponent flips Kahili's coin, and on heads Kahili returns to their hand.
- The Hypno owner does not get to inspect cards the opponent draws through a forced Tierno.
- The outer turn still belongs to Hypno's player. A Roxie/Weezing ruling says Weezing's Blow-Away Bomb cannot be used after the forced Roxie discards Weezing because Blow-Away Bomb is limited to the Weezing owner's turn.
- A Dizzying Wind ruling likewise says its next-turn Trainer coin flip does not apply when Hand Control forces the Supporter during Hypno's turn.

Kahili:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%AB%E3%83%92%E3%83%AA&regulation_faq_main_item1=all

Roxie/Weezing:
https://www.pokemon-card.com/rules/faq/search.php?sc_group_id=411

## Nested physical transaction

The model introduces a `resolving_supporter` zone.

`begin_hand_control()` moves the opponent-owned Supporter from hand into that zone and records turn owner, card player, decision controller, and source attack. The outer attack remains open while the Supporter body resolves.

`finish_hand_control()` accepts the Supporter body's physical final destination, then closes the outer attack. The default is discard. Hand and Prize destinations are also represented because official rulings show card-specific Supporter bodies can redirect the same physical card, such as Kahili returning to hand or Gladion being exchanged into Prize cards.

The non-current player's ordinary turn budget is preserved. The forced Supporter play is logged separately as an out-of-turn event. Their normal Supporter allowance belongs to their own turn.

## Architectural consequence

Hand Control needs independent state for:

1. physical card owner and zone;
2. outer turn owner;
3. card player;
4. decision controller;
5. current execution class;
6. information visibility when hidden cards are drawn or inspected.

A single generic `actor` field cannot represent these rulings.

## Limits

The executor owns the outer nested transaction and does not implement arbitrary Supporter bodies. A card-specific body executor must determine effects and any non-default final destination.

The corpus scan only identifies the exact `opponent plays that Supporter card` grammar. Other forced-play effects with different wording require separate compilation.
