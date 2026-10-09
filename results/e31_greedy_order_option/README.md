# Greedy Dice E-31 precedence as a positional-information option

## Question

If one two-Prize award reveals **Greedy Dice** and **Dream Ball** together, and one Bench slot remains, can resolving Greedy Dice first improve the outcomes available from a later, still-face-down Jirachi Prism Star Prize?

**Yes in a controlled four-Prize case.** Greedy Dice first preserves the option to let a recursively taken Jirachi enter the last Bench slot. Dream Ball first fills that slot. Taking Jirachi later still takes a Prize, but Jirachi's Wish Upon a Star cannot enter play to take the fourth.

Executable enumeration: [tools/e31_greedy_order_option.py](../../tools/e31_greedy_order_option.py). Independent closed-form identities are checked by [reproduce.py](reproduce.py).

## Card/rules anchors

- Greedy Dice `xy11-102`: a face-down Prize-origin Item; on heads take one additional Prize.
- Dream Ball `swsh7-146`: a face-down Prize-origin Item; search the deck for a Pokémon and put it directly on the Bench.
- Jirachi Prism Star `sm7-97`: if taken as a face-down Prize during the player's turn and Bench is not full, it may enter the Bench and take an additional Prize.
- Peonia `swsh6-149`: puts up to three chosen Prize cards into hand and replaces the same number face down from hand, a possible route to privately knowing placed cards' identities and positions.
- The repository's [owner-ordering witness](../before_hand_prize_ordering/) cites the official Japanese Q&A in which Chansey and Dream Ball are taken together and their owner chooses effect order: https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%89%E3%83%AA%E3%83%BC%E3%83%A0%E3%83%9C%E3%83%BC%E3%83%AB&regulation_faq_main_item1=all
- [Before-hand E-31 execution](../before_hand_prize_execution/) and [Jirachi terminal precedence](../dream_ball_terminal_rescue/) supply the relevant rules context.

The published official mixed-effect ordering witness concerns **Chansey plus Dream Ball**. Applying its owner-choice interpretation to **Greedy Dice plus Dream Ball** is the explicit rules assumption for this experiment; a direct official ruling for this exact pair has not been established here.

## Controlled state

Immediately before a two-Prize Knock Out, the player has **four** remaining Prize cards. The two standard award cards are Greedy Dice and Dream Ball; the two additional face-down Prize cards are exactly one Jirachi Prism Star and one inert filler.

The player has one Active Pokémon and four Benched Pokémon, leaving precisely one open Bench slot. Dream Ball has one eligible Pokémon target in the deck. The turn belongs to the player taking Prizes; both Prize-origin Items can legally resolve; the Greedy Dice coin is fair. No other card effects, triggers, opposing restrictions, or Bench releases intervene. The remaining two Prize positions are equally likely to contain Jirachi under the composition-only information state.

Both original Prize cards are already selected together. Additional Prize effects are prepended to their sibling queue, so nested Jirachi finishes before control returns to the older pending Dream Ball.

## Exact enumeration

Each combination of the two remaining Prize layouts and Greedy Dice's two coin faces has probability 1/4. The following table takes Jirachi's optional trigger whenever it is available:

| E-31 order / information | Prize count 2; Dream target Benched | Prize count 3; Dream target Benched | Prize count 4; Jirachi Benched | Expected Prizes |
| --- | ---: | ---: | ---: | ---: |
| Dream Ball first, either information state | 1/2 | 1/2 | 0 | 5/2 |
| Greedy Dice first; composition known, positions unknown | 1/2 | 1/4 | 1/4 | 11/4 |
| Greedy Dice first; exact Jirachi position known | 1/2 | 0 | 1/2 | 3 |

These are **conditional** on the unusually specific four-Prize configuration, not unconditional match frequencies or win rates.

In the composition-only state, Greedy Dice on heads chooses an exchangeable face-down position and hits Jirachi with probability 1/2. Therefore the recursive fourth-Prize branch has probability (1/2)(1/2) = 1/4.

In the position-known state, the heads branch selects Jirachi deliberately, making the recursive fourth Prize occur with probability 1/2.

**Information distinction:** K1 in `human_concepts.md` means that after a deck search, a player can infer *which cards* are in Prize cards. It does **not** confer their positions. The composition-only row corresponds to that weaker type of information. The last row requires additional physical-position information, obtainable through a controlled placement or a suitable privately revealing effect. Face-up public Prize methods can disable these face-down-specific triggers and cannot be substituted indiscriminately.

## Why early Greedy has option value

If Jirachi is taken before Dream Ball and an open slot exists, the player may use Wish Upon a Star for a fourth Prize, or decline it and still let Dream Ball use the slot. Under the stated model, declining reproduces the Dream-first outcome.

Thus the early-Greedy policy can imitate late-Greedy while holding an extra contingent option.

Define stylized utility:

`U = number_of_Prizes_taken + v * indicator(Dream_target_entered_Bench)`, where `v >= 0` is the target's assigned value in Prize-equivalent units.

Let `B = 5/2 + v` denote Dream-first value. After optimizing the optional Jirachi choice:

- **Composition-only:** `E[U] = B + max(0, 1-v)/4`.
- **Exact-position-known:** `E[U] = B + max(0, 1-v)/2`.

For `v < 1` early Greedy is strictly better; if `v >= 1`, declining Jirachi can reproduce the Dream-first benchmark and the values tie. The premium from exact positional knowledge over composition-only knowledge is `max(0, 1-v)/4` in this setup.

This isolates an information-dependent tactical option without asserting that every real deck should prioritize Greedy Dice or the fourth Prize over its Bench target.

## Validation

The self-contained Python implementation enumerates all four equally weighted physical worlds with `fractions.Fraction`, resolves the pending queue recursively, and checks that each Prize instance is awarded once. It checks the exact three outcome distributions, the closed-form utility identities at six values of `v`, and the replication of Dream-first outcomes by early-Greedy with Jirachi declined.

Run `python tools/e31_greedy_order_option.py` or `python results/e31_greedy_order_option/reproduce.py` from the repository root.

## Scope and next work

This is a compact exact game fragment. It does not execute the repository's physical `IdentityLedger` or observer-belief kernels, simulate real opening-hand probabilities, score the quality of actual Dream Ball targets, or prove a direct Greedy Dice + Dream Ball official ordering ruling.

A useful extension is an end-to-end conserved implementation with `PendingPrizeBatchOrder`, `before_hand_prize_executor`, `use_wish_upon_a_star`, and observer-aware staging, including the exact extra-Prize position policy and the terminal-state check.
