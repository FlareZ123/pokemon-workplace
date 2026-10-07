# Game resolution after the Prize pending window

## Question

If both players' Active Pokémon are Knocked Out and a final Prize card has an E-31 before-hand effect that can put a Pokémon into play, when should Prize/no-Pokémon loss conditions be evaluated?

For the official Jirachi Prism Star witness, the E-31 window must finish first.

Implementation: `tools/post_prize_window_game_resolution.py`  
Regression: `results/post_prize_window_game_resolution/reproduce.py`

## Authoritative ruling

The official Japanese Pokémon Card Game Q&A asks about this exact state:

- both players have one Prize card remaining;
- neither player has any Benched Pokémon;
- one attack Knocks Out both Active Pokémon simultaneously;
- the attacking player takes Jirachi Prism Star with Wish Upon a Star as their face-down Prize.

The ruling says the player may put Jirachi Prism Star onto the Bench with Wish Upon a Star, and Jirachi's owner wins.

Official Q&A:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%81%BB%E3%81%97%E3%81%AB%E3%81%AD%E3%81%8C%E3%81%84%E3%82%92&regulation_faq_main_item1=BW

This resolves the terminal-precedence edge that earlier repository work deliberately left open.

## Consequence for the phase model

After both Active Pokémon are physically discarded, both players temporarily have zero Pokémon in play.

If a simulator immediately evaluates the final-Prize/no-Pokémon table at that instant, then with both players also reaching zero remaining Prizes the state is a tie.

That is the wrong result for the official witness.

The face-down Jirachi Prize instead enters the E-31 pending window. Wish Upon a Star puts that same physical Jirachi instance onto the Bench. Only after the Prize pending window finishes should the terminal snapshot use the resulting board.

At that point:

- both players have zero remaining Prize cards;
- Jirachi's owner has one Pokémon in play;
- the opponent has zero Pokémon in play.

The existing loss-condition-count table then gives Jirachi's owner one fulfilled loss condition and the opponent two, so Jirachi's owner wins.

## Adapter

`resolve_after_prize_window()` accepts the promotion-pending physical context and the current remaining-Prize counts.

It refuses to resolve while any `prize_pending` card remains.

After the pending queue is empty, it calls the existing rulebook-table resolver using the current physical Pokémon counts:

- terminal result -> `TERMINAL`;
- continuing result -> `PROMOTION`.

This removes the need for a caller to guess whether E-31 board mutations should be included in the terminal snapshot.

## Regression

The regression constructs the official geometry with exact physical card instances.

It demonstrates both states:

1. **early counterfactual:** both final Prizes taken, both Pokémon counts zero -> tie;
2. **official sequence:** Jirachi resolves from `prize_pending` into play first -> Jirachi owner wins.

The same Jirachi physical instance moves from Prize to pending to in-play, and both players' card-class totals remain conserved.

## Broader finding

The Prize window is part of game-state resolution, not only card destination handling.

A before-hand Prize effect can change whether a player satisfies the no-Pokémon loss condition. Terminal evaluation therefore belongs after applicable E-31 effects have resolved and before replacement-Active policy.

## Scope

This result covers Prize/no-Pokémon conditions around Knock Out resolution. Beginning-of-turn deck-out remains a separate timing rule.

The adapter takes remaining-Prize counts from upstream award logic. It does not decide Prize values or which physical Prize positions are selected.

It also does not compile arbitrary before-hand card text. The current executable Jirachi transition comes from `prize_before_hand_bench_entry.py`.
