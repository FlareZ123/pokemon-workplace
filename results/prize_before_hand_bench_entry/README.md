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

## Turn-ownership gate

Both Lucky Bonus and Wish Upon a Star require the face-down Prize to be taken during the card owner's turn.

The executable API therefore requires an explicit `during_your_turn` input and refuses the trigger when that condition is false.

Official Japanese Jirachi Prism Star Q&A confirms this boundary in two independent contexts: Wish Upon a Star cannot be used when the Prize is taken during the opponent's turn from Electrode-GX's self-Knock-Out Ability, and it cannot be used when the Prize is taken during Pokémon Checkup.

Source:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%81%BB%E3%81%97%E3%81%AB%E3%81%AD%E3%81%8C%E3%81%84%E3%82%92&regulation_faq_main_item1=BW

The regression rejects both Chansey and Jirachi when the caller marks the Prize take as outside the owner's turn.

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

## Two competing destination replacements across two Prizes

The official Japanese Q&A confirms that Lost Block and Billowing Smoke can both apply to the same Knock Out, and that the player taking a two-Prize award may choose the destination separately for each card. Applying Lost Block first sends a selected Prize to the Lost Zone; applying Billowing Smoke first sends an ordinary selected Prize to discard. [Official Lost Block and Billowing Smoke interaction](https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%AD%E3%82%B9%E3%83%88%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF&regulation_faq_main_item1=BW).

The added end-to-end regression obtains those replacement choices from the **actual Knocked Out Tool holder and surviving Barbaracle in the board-object KO kernel**, then stages two exact face-down Prizes: Jirachi Prism Star and Chansey. Both choice orders resolve successfully:

| Selected override for Jirachi | Selected override for Chansey | Final Jirachi | Final Chansey |
| --- | --- | --- | --- |
| Billowing Smoke | Lost Block | Lost Zone (Prism Star rule) | Lost Zone |
| Lost Block | Billowing Smoke | Lost Zone | Discard |

Both self-to-Bench effects are ineligible because the respective Prize destination is not the hand. Both cases conserve every physical Prize/board card and finish the pending queue. These are a deterministic rules test under an assumed two-Prize KO award. It is deliberately separate from deck selection, matchup frequency, or win-rate evidence. The KO object and pending Prize board are separate kernel projections; the fixture checks them in sequence but does not claim a unified game-engine implementation.

## Recursive E-31 chain

The Jirachi regression starts with Jirachi Prism Star as the taken Prize and Chansey as another face-down Prize.

Wish Upon a Star:

- moves Jirachi from `prize_pending` into play;
- takes the Chansey as an additional Prize;
- places Chansey at the front of the pending queue.

Lucky Bonus then resolves from that new pending card and puts the same Chansey instance onto the Bench.

This is an executable example of E-31 effects creating further E-31 work before the Prize window closes.

## Knock-Out location and sequential Bench-capacity contention

The expanded regression separates four same-turn own-board disposal patterns while assuming that an opposing Active Knock Out has already earned the initial face-down Prize. All four begin with five Benched Pokémon and the same ordered Jirachi, Chansey, Other Prize identities.

| Own Pokémon simultaneously Knocked Out | Bench before Prize effects | Jirachi enters? | Chansey enters from Jirachi's extra Prize? |
| --- | ---: | --- | --- |
| Active only | 5 | No | No extra Prize |
| One Benched only | 4 | Yes | No, Jirachi fills the Bench |
| Active and one Benched | 4 | Yes | No, Jirachi fills the Bench |
| Active and two Benched | 3 | Yes | Yes, the next open Bench slot remains |

The official Japanese Jirachi Prism Star Q&A explicitly distinguishes simultaneous own-Active versus own-Benched Knock Outs with a full starting Bench: the former refuses Wish Upon a Star, while the latter permits it. This validates the first two rows as an actual game rule.

Official source: https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%81%BB%E3%81%97%E3%81%AB%E3%81%AD%E3%81%8C%E3%81%84%E3%82%92&regulation_faq_main_item1=BW

The remaining rows are executable consequences of the same KO disposal order, physical Bench capacity, and two card texts. In the four-Bench cases, Jirachi's own entry consumes the single opening; the additional Chansey Prize still reaches hand because Lucky Bonus cannot place it on the full Bench. In the three-Bench case, both enter; a heads result on Chansey stages the third face-down Prize, which then reaches hand. Every path verifies exact physical-card conservation.

These are deterministic conditional transition tests. They do not estimate the frequency of such multi-Knock-Out states or show that a Jirachi/Chansey inclusion improves match win rates.

## Prize-destination replacement gate: Billowing Smoke

Jirachi Prism Star and Chansey require the face-down Prize to be on the normal path into hand before their optional self-to-Bench effect can run. **Billowing Smoke** (`swsh3-158`) replaces the opponent's hand entry for Prize cards earned by attacking and Knocking Out its holder with a discard. The official Japanese Q&A rules that Wish Upon a Star cannot activate in this situation; the same answer is given for Treasure Energy's before-hand trigger.

Sources:

- Billowing Smoke text: https://pkmncards.com/card/billowing-smoke-darkness-ablaze-daa-158/
- Official Jirachi/Treasure Energy rulings: https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%82%E3%81%8F%E3%82%82%E3%81%8F%E3%82%B9%E3%83%A2%E3%83%BC%E3%82%AF

The specialized executors now accept a `pre_hand_destination` keyword and reject the optional Bench entry when its value is not `hand`. This follows the existing `before_hand_prize_executor` contract and uses the upstream `prize_destination_applicability` / `prize_destination_overrides` layers to determine replacements. The regression checks both Jirachi and Chansey with a Billowing Smoke destination decision, and physically resolves the ordinary Chansey case into discard without inventing a Bench object.

The specialized Jirachi branch now also executes its **Prism Star Lost-Zone rule** after a final Prize-destination decision. Billowing Smoke's attempted `discard` sends exact `sm7-97` to `lost_zone`, leaving no board object; the matching Chansey Prize ends in `discard`. The complete resulting physical ledgers conserve every card. Official [Jirachi Prism Star text](https://www.pokemon-card.com/card-search/details.php/card/34980/regu/all) and the [Pokémon TCG Prism Star rulebook](https://assets.pokemon.com/assets/cms2-en-uk/pdf/trading-card-game/rulebook/par_rulebook_en.pdf) require this replacement. This single-print handler consumes a selected decision from the existing Prize-destination layer; it does not replace the engine-wide handling of Prism Star cards. The default pre-hand argument remains `hand`, so integrations must pass any applicable override destination explicitly.

## Limits

The current executable island does not yet cover:

- Dream Ball;
- Treasure Energy;
- Greedy Dice;
- observer-belief updates for an additional Prize staged from inside an E-31 effect;
- general card-text compilation from the atom catalog into these executable functions;
- global Prism Star replacement for arbitrary Pokémon, Trainers, and Energy outside the exact Jirachi Prize transition.

Those are separate semantic layers rather than assumptions hidden inside this transition.
