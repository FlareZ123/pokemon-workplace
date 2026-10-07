# Executable Prize-before-hand Bench entry

## Question

Can the existing `before_hand_prize_trigger` catalog atom be made executable for Prize cards that put themselves onto the Bench?

For Chansey's Lucky Bonus and Jirachi Prism Star's Wish Upon a Star, yes.

Implementation: `tools/prize_before_hand_bench_entry.py`  
Regression: `results/prize_before_hand_bench_entry/reproduce.py`

## Card-text scope

This result implements two exact Expanded card identities already recognized by the Prize-effect catalog:

- `sv3pt5-113` Chansey, Lucky Bonus;
- `sm7-97` Jirachi Prism Star, Wish Upon a Star.

Both require the card to have been taken as a face-down Prize during the turn, both act before hand entry, both require open Bench space, and both can place the pending Prize card itself onto the Bench.

Lucky Bonus stages one additional Prize only on heads. Wish Upon a Star stages one additional Prize deterministically.

## Physical transition

The transition requires `PrizePendingTakeState` and `PromotionPendingState` to share the same `IdentityLedger`.

When the effect is used:

1. the next pending Prize must be the expected exact card class and must have been face down;
2. the board must have an open Bench slot;
3. the pending physical card moves from `prize_pending` to `in_play` with a new board-object binding;
4. a corresponding `BoardPokemon` is created from that same physical instance;
5. if the effect takes an additional Prize and one remains, `stage_additional_prize_front` moves that Prize into the front of the pending queue.

No card is copied or recreated. Conservation is checked from the pregame class counts through the final physical state.

## Why this matters after an Active KO

A player can reach a state where their prior Active has already been discarded and no surviving Pokémon remain. At the physical level, a face-down Chansey Prize can then enter the empty Bench during the Prize window and create a future promotion candidate.

The regression proves that geometry. The later `post_prize_window_game_resolution` result resolves the win/loss precedence with an official Jirachi Prism Star ruling: an E-31 Bench-entry effect can change the Pokémon-in-play count before the terminal snapshot is evaluated.

## Official full-Bench validation

The official Japanese Pokémon Card Game Q&A gives a complementary boundary case.

It asks about a player with five Benched Pokémon whose 50-HP Great Tusk ex uses Gigant Tusk, Knocks Out the opponent's Active, and is also Knocked Out. If the taken Prize is Chansey, can Lucky Bonus be used? The official answer is no.

Source: https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%A9%E3%83%83%E3%82%AD%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%8A%E3%82%B9&regulation_faq_main_item1=BW

The regression mirrors this exact geometry. After Active disposal and before promotion, all five survivors still occupy the Bench, so `open_bench_slots == 0`. A later promotion would open a slot, which is too late for Lucky Bonus.

## Recursive E-31 chain

The Jirachi regression starts with Jirachi Prism Star as the taken Prize and Chansey as another face-down Prize.

Wish Upon a Star:

- moves Jirachi from `prize_pending` into play;
- takes the Chansey as an additional Prize;
- places Chansey at the front of the pending queue.

Lucky Bonus then resolves from that new pending card and puts the same Chansey instance onto the Bench.

This is an executable example of E-31 effects creating further E-31 work before the Prize window closes.

## Limits

The current executable island does not yet cover:

- Dream Ball;
- Treasure Energy;
- Greedy Dice;
- observer-belief updates for an additional Prize staged from inside an E-31 effect;
- card-text compilation from the atom catalog into these executable functions;
- general card-text compilation from the atom catalog into these executable functions.

Those are separate semantic layers rather than assumptions hidden inside this transition.
