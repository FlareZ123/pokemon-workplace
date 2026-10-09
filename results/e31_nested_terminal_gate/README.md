# Nested Jirachi final Prize must not bypass older E-31 siblings

## Question

When Greedy Dice and Dream Ball were taken simultaneously and Greedy Dice first takes Jirachi Prism Star as an extra Prize, can Jirachi take the very last remaining Prize before the original Dream Ball pending card is resolved? If so, when does game termination occur?

In the controlled physical trace, **Jirachi can exhaust the Prize zone while Dream Ball remains pending**. The E-31 window still needs to close before the game-resolution policy runs.

Regression: [tools/e31_nested_terminal_gate.py](../../tools/e31_nested_terminal_gate.py).  
CI: [passing run 37976853889](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37976853889).

## Physical trace

The test reuses [Peonia-seeded four-Prize geometry](../e31_peonia_seed_execution/), in which:

- original selected two Prize cards are Greedy Dice and Dream Ball;
- Greedy Dice resolves first;
- Jirachi Prism Star is the known additional-Prize target;
- the fourth Prize is an inert filler;
- only one Bench slot is available;
- the opponent has an additional Pokémon to promote after the assumed Knock Out.

On Greedy Dice heads:

1. Greedy Dice enters the before-hand Item `resolving_trainer` zone.
2. Its effect takes Jirachi as an additional face-down Prize.
3. Jirachi moves from the `prize_pending` zone directly into the last Bench slot.
4. Wish Upon a Star takes the final filler Prize.
5. Greedy Dice completes and enters discard.
6. The older Dream Ball sibling remains `prize_pending`, despite **zero Prizes left**.
7. The terminal resolver correctly returns `None` while Dream Ball is unresolved.
8. Dream Ball follows the hand route because the Bench is now full.
9. With the pending window empty, the terminal resolver awards the player who has zero remaining Prizes the win.

On Greedy Dice tails, it takes no extra Prize. Dream Ball can place Tapu Lele-GX on the Bench. Two Prizes remain after the original two-award Knock Out; the terminal resolver correctly advances to the normal promotion phase and both players remain in the game.

The physical card totals are conserved in both branches. The phase gate checks both the pending queue and the resolving-Trainer zone.

## Source authority and limitation

The previously established [post-Prize-window resolution](../post_prize_window_game_resolution/) cites an official Jirachi Prism Star ruling requiring the E-31 window to complete before the terminal snapshot. Its exact terminal example involves simultaneous Active Knock Outs and final-Prize Jirachi.

This test extends that implementation to **nested extra Prize work**, with an older sibling still unresolved at the moment the last Prize is taken. The result is a code-level integration of established timing rules, conditional on the Greedy Dice + Dream Ball sibling-order extrapolation noted elsewhere.

The test does not establish whether an opponent would permit the setup, nor how often the four-card Peonia packet is available. It models the post-attack Prize window and subsequent game resolution.

## Reproduction

`python tools/e31_nested_terminal_gate.py`.
