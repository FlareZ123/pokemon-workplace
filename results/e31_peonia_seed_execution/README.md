# Peonia makes the known-position E-31 Greedy/Dream/Jirachi branch executable

## Question

Can the exactly position-known Prize geometry in [the Greedy Dice ordering result](../e31_greedy_order_option/) be obtained from a legal Expanded card effect with conserved physical identities?

Yes, **conditionally on already holding Peonia, Greedy Dice, Dream Ball and Jirachi Prism Star while four Prize cards remain**, and being able to take a two-Prize Knock Out that turn.

Executable transaction: [tools/e31_peonia_seed_execution.py](../../tools/e31_peonia_seed_execution.py). Validation: [GitHub Actions run 37976094692](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37976094692), passed.

## Direct official authority

The Japanese Pokémon Card Game Q&A specifically addresses Peonia (シャクヤ), asking whether replacement cards chosen from hand must be shuffled when put face down as Prize cards. The answer is **no** and says the cards can be put in whatever order the player wishes.

Official source: https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%B7%E3%83%A3%E3%82%AF%E3%83%A4&regulation_faq_main_item1=all

This directly verifies that Peonia `swsh6-149` can create a known physical-position mapping while preserving face-down status. The same Q&A separately says taking Chansey from the Prize zone with Peonia cannot activate Lucky Bonus. These are two distinct windows: Peonia's Prize-to-hand exchange and a later Knock Out's Prize *award*.

The bundled English print text of Peonia is:

> Put up to 3 Prize cards into your hand. Then, for each Prize card you put into your hand in this way, put a card from your hand face down as a Prize card.

The replacement cards are chosen from the hand and placed face down; there is no Prize shuffle instruction in the effect. Related independent groundwork: [Peonia to Arc Phone positional policy](../peonia_arc_position/).

## Controlled physical setup

Initial supplied state has four face-down Prizes, one Active Pokémon and four Benched Pokémon, leaving one Bench slot free. Peonia, Greedy Dice `xy11-102`, Dream Ball `swsh7-146`, and Jirachi Prism Star `sm7-97` are in hand. A legal Tapu Lele-GX `sm2-60` search target is in deck.

Three existing Prize cards are taken into hand through Peonia. One of them is deliberately a Chansey, and the test checks that it does not enter the Bench or start Lucky Bonus while resolving Peonia. The three replacement cards are physically moved from hand into known face-down Prize positions in this order:

| Physical position after Peonia | Exact card |
| --- | --- |
| 0 | Greedy Dice |
| 1 | Dream Ball |
| 2 | Jirachi ◇ |
| 3 | Original inert filler Prize |

The Peonia instance enters discard. Every card class count remains conserved, and the unchanged fourth Prize retains its exact physical identity.

A separately supplied attack then Knocks Out a two-Prize Pokémon, and the player chooses positions 0 and 1 as the two awarded Prizes. The original same-award effects are resolved with Greedy Dice first. Because Greedy's effect can take an additional Prize, the selected extra position is the now-known Jirachi slot.

## Exact two-branch physical result

| Greedy Dice coin | Additional Prize sequence | Last Bench slot | Prizes taken during sequence |
| --- | --- | --- | ---: |
| Tails | None | Dream Ball searches Tapu Lele-GX | 2 |
| Heads | Jirachi, then the final filler from Wish Upon a Star | Jirachi ◇ enters play | 4 |

The coin is fair. The **conditional expected Prize count is exactly 3**. The entire final-Prize branch has probability 1/2 under the supplied Peonia packet. This provides an exact physical witness for the "position-known" column of [the earlier result](../e31_greedy_order_option/).

The original two Prize cards, additional Prize, and final Jirachi-generated Prize all retain stable materialized IDs. The executor checks that the original batch sibling is processed only after nested Prize work. It uses the existing `PendingPrizeBatchOrder`, `PrizePendingTakeState`, Greedy Dice before-hand Item executor, typed Dream Ball deck-to-Bench executor, Jirachi `use_wish_upon_a_star`, and the shared `IdentityLedger` conservation invariant.

## Scope and remaining question

This establishes **a physically possible setup transition** once the hand, board, Prizes and later Knock Out are supplied. It does not establish the likelihood of finding this four-card hand, drawing Peonia, satisfying the two-Prize attack, or obtaining Jirachi's optional ability under actual opposing interaction. Peonia consumes the only ordinary Supporter action that turn, a significant strategic cost.

The official sibling-order witness in the repository specifically concerns Chansey plus Dream Ball. Applying the same owner-chosen ordering to a simultaneous Greedy Dice plus Dream Ball award remains an explicitly identified rules extrapolation. The physical tests validate its consequences *conditional on that rule interpretation*; a direct ruling for the exact pair is still worth locating.

A second missing piece is observer belief: Peonia's player knows all three seeded Prize slots, but the opponent should not automatically learn which identities those face-down Prize cards contain. The current physical test preserves card truth without propagating that private information into the observer-specific posterior kernel.

## Reproduction

From the repository root:

`python tools/e31_peonia_seed_execution.py`

Its two physical branches are also run by `.github/workflows/validate-e31-greedy-order-option.yml`.
