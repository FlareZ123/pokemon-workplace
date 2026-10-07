# Dream Ball can change the post-Prize terminal snapshot

## Question

Once the E-31 terminal-precedence rule is established by the official Jirachi Prism Star ruling, can the same phase ordering make a final Prize-origin Dream Ball change a zero-Pokémon terminal result?

Yes, when Dream Ball can legally put a Pokémon onto the Bench.

Regression: `results/dream_ball_terminal_rescue/reproduce.py`

## Authority inherited from the Jirachi ruling

The official Japanese Q&A gives an exact terminal-precedence witness:

- both players have one Prize remaining;
- neither player has a Benched Pokémon;
- one attack Knocks Out both Active Pokémon;
- the attacking player takes Jirachi Prism Star as the face-down final Prize.

The ruling says Wish Upon a Star may put Jirachi onto the Bench and that Jirachi's owner wins.

Source:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%81%BB%E3%81%97%E3%81%AB%E3%81%AD%E3%81%8C%E3%81%84%E3%82%92&regulation_faq_main_item1=BW

The repository encodes that phase rule in `post_prize_window_game_resolution.py`: terminal Prize/no-Pokémon evaluation remains closed while the E-31 Prize window is unresolved, including while a Prize-origin Trainer occupies `resolving_trainer`.

## Dream Ball derivation

Dream Ball `swsh7-146` is another E-31 Prize-origin effect. Its Item body searches the deck for a Pokémon and puts it directly onto the Bench.

The regression begins at the same critical geometry:

- Player A has zero Pokémon in play;
- Player B has zero Pokémon in play;
- both players have zero remaining Prizes after awards;
- Player A's final face-down Prize is still a pending Dream Ball;
- Player A has Pidgeot ex `sv3-164` available in deck.

Terminal resolution is refused while Dream Ball remains pending.

## Two policy branches

### Decline Dream Ball

If Player A declines the special Prize-origin play and Dream Ball enters hand, the Prize window closes with both players at:

- zero remaining Prizes;
- zero Pokémon in play.

The existing terminal table returns a tie.

### Use Dream Ball

If Player A uses Dream Ball:

1. Dream Ball moves into `resolving_trainer`;
2. exact typed search selects Pidgeot ex;
3. the Pidgeot ex copy moves from deck directly into a materialized Bench object;
4. Dream Ball finishes and enters discard;
5. only then does the Prize window close.

The final terminal snapshot is now:

- Player A: zero remaining Prizes, one Pokémon in play;
- Player B: zero remaining Prizes, zero Pokémon in play.

The terminal table returns Player A win / Player B loss.

Pidgeot ex still has no selected Active position at that instant. No promotion occurs because the game is already terminal once the post-E-31 snapshot is evaluated.

## Finding

E-31 cards can have discrete terminal value that is invisible to a Prize-count-only or early-board snapshot.

For Dream Ball, the searched Pokémon's ordinary strategic value may be irrelevant in the terminal branch. Any legal target that creates the needed surviving Pokémon can change the game-resolution outcome before promotion policy is reached.

This is a concrete example of why before-hand Prize effects belong inside terminal game-state resolution rather than after it.

## Limits

The official ruling is for Jirachi Prism Star, not Dream Ball specifically. The Dream Ball result is a derived application of the same E-31 phase boundary combined with Dream Ball's official deck-to-Bench text and the repository's executable Prize-origin Item semantics.

The regression assumes the final Prize award and zero-Pokémon post-KO geometry are already established upstream. It does not model the attack that caused the simultaneous Knock Outs.

The branch requires Dream Ball itself to be a face-down Prize taken during the valid timing window, an open Bench, and a searchable Pokémon target.
