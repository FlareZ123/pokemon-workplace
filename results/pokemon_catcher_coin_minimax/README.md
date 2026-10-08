# Pokémon Catcher: current errata, coin risk, and tactical redundancy

## Question

A raw read of some bundled Black & White Pokémon Catcher prints suggests a deterministic opposing Bench gust. Current paper Expanded instead uses Pokémon Catcher's **coin-flip errata**. How does the coin risk change the value of one or two Catcher copies compared with a deterministic Boss's Orders-style gust in an opponent-aware Prize endgame?

## Card-text and authoritative errata basis

- The bundled `resources/cards/en/bw2.json` Pokémon Catcher `bw2-95` still prints a deterministic switching instruction without a coin flip. Later `sv1-187` and `me3-82` explicitly require a coin flip.
- The official Pokémon TCG Errata PDF **https://assets.pokemon.com/assets/cms/pdf/tcg/tcg_errata.pdf**, page 1, states that Pokémon Catcher now requires a coin flip, and identifies the effect as functionally identical to Pokémon Reversal. The official Play! Pokémon errata page (last update November 7, 2024) is also https://play.pokemon.com/fr-ca/resources/documents/tcg-errata/ .
- The Advanced Player's Rulebook, II-A, requires the latest updated text if card text has changed; II-C-05 distinguishes choosing an opposing Benched target from opponent-controlled switching.

**Important modeling rule:** every historical Pokémon Catcher print must use the coin-flip effect in current-rule analysis. A card database containing old literal printed text is not itself a current semantic oracle.

## Exact bounded chance game

`tools/pokemon_catcher_coin_minimax.py` adds a fair coin-flip action to the previous `gust_prize_minimax.py` six-Prize opponent-promotion model.

The player can choose when to attempt an available Catcher, or attack without using it. After **heads**, the player chooses which opposing Benched target becomes Active and attacks. After **tails**, the Item has been spent, but the player remains in the same turn and may use another Catcher (or attack). An attack ends the turn. On KO, the defender chooses the replacement Active that maximizes the player's future **expected number of attacks**, knowing public coin outcomes.

All targets are one-hit KOs worth 1, 2, or 3 Prize cards. The opposing board remains static apart from KOs. Up to two Catchers are in hand and otherwise playable. Item lock, card draw, opponent attacks, reshuffling, and search costs are excluded. This conditional model does not estimate the probability of actually drawing two Catchers by the relevant turn.

A dynamic program with exact `Fraction` arithmetic has an attack action and an optional coin-attempt action. On heads, the player optimizes the target; on tails, the remaining Item count decreases but the attack turn has not elapsed. The defender selects worst-case promotion after each KO.

## Complete census across 146 structural boards

The exact expected attacks saved versus zero available gusts are:

| Expected attacks saved | One Catcher | Two Catchers |
| ---: | ---: | ---: |
| 0 | 77 | 38 |
| 1/4 | 0 | 31 |
| 1/2 | 54 | 8 |
| 3/4 | 0 | 42 |
| 1 | 15 | 10 |
| 5/4 | 0 | 2 |
| 3/2 | 0 | 15 |
| **Total** | **146** | **146** |

For all 146 boards, one fair-coin Catcher achieves exactly the midpoint in expected attacks between no gust and one deterministic Boss-style gust. This is an **exhaustively observed identity for this bounded game**, not a general rule covering card draw, evolving, or uncertain opposing responses.

Comparing **two fair-coin Catchers** with **one guaranteed Boss-style gust**, the pair provides a lower expected attack count in **41 board classes**, exactly equal in **48**, and a higher expected attack count in **57**. The number of physical copies and their independent success probabilities interact with the need for distinct gust turns.

These structural counts are unweighted by live-match occurrence or archetype.

## Witness 1: two coin cards beat one guaranteed gust

Opposing Active **1 Prize**, Bench **1, 3, 3 Prizes**:

| Available resource | Expected minimum attacks |
| --- | ---: |
| No gust | 4 |
| One guaranteed Boss-style gust | 4 |
| One Pokémon Catcher | 4 |
| Two Pokémon Catchers | 7/2 = 3.5 |
| Two guaranteed gusts | 2 |

One deterministic gust cannot force both high-Prize KOs. Two stochastic Items have a positive chance of creating the two distinct high-value target opportunities, either by flipping successfully on separate turns or through adapted retry timing. Their expected benefit is strictly positive even though one guaranteed gust's benefit is zero.

## Witness 2: delaying stochastic access

Opposing Active **3 Prizes**, Bench **1, 3 Prizes**:

| Available resource | Expected attacks |
| --- | ---: |
| Zero Catchers | 3 |
| One Catcher | 5/2 = 2.5 |
| Two Catchers | 9/4 = 2.25 |
| One guaranteed Boss-style gust | 2 |

A Catcher may be held until the next turn to target the second three-Prize Pokémon after naturally KOing the Active. The coin failure branch cannot be erased by theoretical card access; subsequent retries are only available if a second copy remains.

## Verification

`results/pokemon_catcher_coin_minimax/reproduce.py` computes the exact chance+defender+attacker game tree a second way and cross-checks all 146 boards at 0/1/2 Catcher counts (**438** state/copy pairs). It checks the exhaustive histograms, single-copy midpoint identity, casewise ordering under two guaranteed gusts, the 41/48/57 comparison with one Boss gust, and both witnesses.

Run: `python results/pokemon_catcher_coin_minimax/reproduce.py` from the repo root.

## Practical implications

A deck optimization model must normalize historical card text under official errata before connecting card-name search results to tactical actions. A print with obsolete deterministic wording can make a stochastic gust appear unrealistically reliable.

A second copy of a coin-flip Item can be strategically more important than its independent chance of success suggests because two tactical gust uses may have conjunctive value. Actual deck choices still require access probability, item lock, payment, Prize location, and the opportunity cost of a Supporter such as Boss's Orders.

The next step is a conservative catalog of Expanded Trainer gust sources, separating player-selected targets from opponent-selected switches, choice-conditioned effects, card target families, and costs.
