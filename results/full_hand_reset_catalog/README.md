# Expanded full-hand reset catalog: where doomed-resource sequencing can recur

## Question

The Harto Raichu investigation found a local sequencing principle:

> when a planned full-hand reset will discard a search Item and its payment anyway, using the search first can have zero incremental hand-material cost.

How broadly can this situation arise in the current paper Expanded card pool?

Implementation: `tools/catalog_full_hand_resets.py`  
Regression: `results/full_hand_reset_catalog/reproduce.py`

## Method

The catalog scans every bundled English card record, calls the repository's shared effective paper-Expanded legality classifier, and keeps effect text matching the exact form:

`Discard your hand and draw N cards.`

It checks Trainer rules, Abilities, and attacks.

Professor's Research professor-name variants are normalized to one canonical family.

The catalog records timing features that materially affect sequencing:

- Supporter use;
- first-turn wording;
- turn-ending behavior;
- once-per-game GX or VSTAR use;
- explicit top/bottom-deck sensitivity.

## Result

The current snapshot contains **80 legal prints across 15 canonical effect families**.

| Family | Source | Draw | Timing / resource feature |
| --- | --- | ---: | --- |
| Professor Juniper | Supporter | 7 | Supporter bandwidth |
| Professor Sycamore | Supporter | 7 | Supporter bandwidth |
| Professor's Research | Supporter | 7 | Supporter bandwidth |
| Carmine | Supporter | 5 | first-turn exception wording |
| Ingo & Emmet | Supporter | 5 | explicitly looks at top card; can draw from top or bottom |
| Dedenne-GX, Dedechange | Ability | 6 | hand-to-Bench trigger |
| Hisuian Zoroark VSTAR, Phantom Star | Ability | 7 | VSTAR Power, once per game |
| Rayquaza VMAX, Azure Pulse | Ability | 3 | once during turn |
| Squawkabilly ex, Squawk and Seize | Ability | 6 | first-turn-only Ability |
| Zamazenta V, Regal Stance | Ability | 5 | ends the turn |
| Zebstrika, Sprint | Ability | 4 | once during turn |
| Raging Bolt ex, Burst Roar | Attack | 6 | attack ends turn |
| Rayquaza-GX, Tempest-GX | Attack | 10 | GX attack, once per game; attack ends turn |
| Talonflame V, Fast Flight | Attack | 6 | first-turn exception; attack ends turn |
| Tapu Koko, Fast Flight | Attack | 5 | first-turn exception; attack ends turn |

## General sequencing implication

All 15 families can create a state where cards in hand are scheduled to be discarded by a later action.

If a legal pre-reset action consumes only cards that the reset would certainly discard, then the relevant incremental cost is smaller than the action's literal payment suggests.

For Quick Ball specifically, a zero-output constrained search can preserve the same unordered hand/deck/discard material projection before one of these resets while adding deck-composition information, provided the earlier theorem's conditions hold.

This expands the phenomenon beyond draw-engine Pokémon. Professor Juniper, Professor Sycamore, Professor's Research, Carmine, and Ingo & Emmet can create the same doomed-hand geometry with an Item played before the Supporter.

## Timing classes matter

The same material argument does not imply the same strategic value.

### Supporter resets

Professor-family cards, Carmine, and Ingo & Emmet consume the Supporter window. Playing an Item before them does not itself consume that window, but other Supporter lines remain mutually exclusive.

Ingo & Emmet is especially important because it explicitly observes the top card and can draw from the top or bottom. The `pre_reset_shuffle_value/` result therefore applies directly: a prior search shuffle can change the information and positional state that Ingo & Emmet uses.

### Ability resets

Dedechange, Phantom Star, Azure Pulse, Squawk and Seize, Regal Stance, and Sprint preserve the Supporter window, but each has different board or global-resource gates.

Phantom Star spends the once-per-game VSTAR Power.

Regal Stance ends the turn after use.

Dedechange requires playing Dedenne-GX from hand onto the Bench.

### Attack resets

Burst Roar, Tempest-GX, and both Fast Flight families end the turn because an attack was used.

That removes post-reset same-turn action value. Search-before-attack information can still affect whether the attack should be chosen, but cards drawn by the reset cannot be converted into additional same-turn Trainer or Ability actions after the attack completes.

Tempest-GX also spends the once-per-game GX attack.

## Methodological consequence

"Discard your hand and draw N" should be represented as a zone transition with action timing, rather than as a generic draw-N edge.

The same literal hand reset can differ through:

- when the reset is available;
- which turn resource it consumes;
- whether the turn ends;
- whether a once-per-game resource is spent;
- whether deck-position information matters;
- whether the player can act on the fresh hand immediately.

Those distinctions change AMR, connector opportunity cost, and the value of pre-reset sequencing.

## Limits

The catalog deliberately matches the exact discard-then-draw wording.

It does not include:

- shuffle-hand-and-draw effects;
- draw-first-then-discard effects;
- effects that discard only part of the hand;
- effects whose current legal text is functionally similar but worded differently;
- effects that replace the hand through another zone.

The 80-print count is a database-snapshot result under the shared legality classifier. Strategic applicability still depends on board state and the gates of each individual effect.

## Next work

Two extensions now look useful:

1. catalog full-hand replacement effects beyond literal discard-and-draw wording;
2. construct a reset-effect type system recording turn termination, Supporter/VSTAR/GX contention, board-entry gates, position sensitivity, and whether the fresh hand can be acted on during the same turn.

That type system could feed a generic sequencing planner instead of maintaining Harto-specific branches.
