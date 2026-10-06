# Prize rescue with a discard-gated preserving connector

## Question

How do Supporter-window timing and discard payability compound when a same-window connector must discard cards before it can find a Gladion-like rescue Supporter?

This result extends the turn-by-turn Prize-rescue optimizer with one concrete AMR cost channel.

Implementation: `tools/prize_rescue_discard_connector.py`  
Reproducer and exhaustive validation: `results/prize_rescue_discard_connector/reproduce.py`

## Prior results connected here

`results/prize_rescue_connector_turns/` models preserving and Supporter-consuming connectors across multiple rescue windows.

`results/discard_gated_supporter_access/` measures a discard gate in a single current-window target-Supporter access check.

The present model combines those ideas. A connector preserves the Supporter play, so its timing is favorable, while its search is usable only when the current hand contains enough modeled disposable cards.

## Model

The deck is partitioned into:

- critical setup-eligible starters;
- critical non-starters;
- Gladion-like rescue Supporters;
- copies of one Supporter-preserving discard-gated connector;
- disposable non-starters;
- protected setup starters;
- protected non-starters.

The opening hand is conditioned on a valid setup, then Prize cards are sampled from the remaining deck.

Each modeled rescue turn:

1. draws one random card;
2. allows any number of modeled connector searches that can be paid;
3. allows at most one rescue Supporter play.

Each connector search finds one rescue Supporter from the deck. A search consumes one connector and exactly `discard_cost` disposable cards from hand. Search effects are treated as shuffling the remaining deck.

The connector class is deliberately generic. With one copy and discard cost two it resembles the current-window cost structure of Computer Search for this narrow target-access purpose. With one copy and cost three it resembles the discard gate of Secret Box. Their other strategic differences are excluded.

## Exact action optimization

The model does not force the connector to be used as soon as it becomes payable.

After each random draw, the dynamic program considers:

- waiting;
- playing a rescuer already in hand;
- spending zero or more payable connector copies, fetching that many rescuers, and then playing one rescuer.

It chooses the action that maximizes the probability of rescuing every modeled critical Prize by the horizon.

Waiting can be correct. A player may already have enough future turns to draw a rescuer naturally, and preserving the connector plus its discard fodder can provide stronger insurance against a later miss.

## Illustrative baseline

Use:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 protected setup starters;
- 4 non-starter critical singletons;
- 2 rescue Supporters;
- 1 preserving connector.

Condition on at least one modeled critical singleton being initially Prized.

The table varies the binary disposable pool and the connector's discard cost.

| Disposable non-starters | Discard cost | Rescue by turn 1 | Turn 2 | Turn 3 | Turn 4 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 0 | 29.653559% | 33.602650% | 36.952742% | 40.187978% |
| 10 | 2 | 23.843534% | 27.752874% | 31.415999% | 35.059903% |
| 10 | 3 | 21.678252% | 24.965769% | 28.134006% | 31.376702% |
| 20 | 0 | 29.653559% | 33.602650% | 36.952742% | 40.187978% |
| 20 | 2 | 27.595597% | 31.986391% | 35.785357% | 39.372988% |
| 20 | 3 | 24.719339% | 29.174533% | 33.306706% | 37.305618% |
| 30 | 0 | 29.653559% | 33.602650% | 36.952742% | 40.187978% |
| 30 | 2 | 29.290984% | 33.406484% | 36.858599% | 40.145175% |
| 30 | 3 | 27.979202% | 32.528235% | 36.343135% | 39.863285% |

Discard cost zero is an idealized preserving connector with no hand gate. The disposable-card count has no effect in those rows.

## Finding 1: DCI can erase much of a same-window connector's nominal value

With only 10 disposable non-starters, the ideal connector raises turn-1 rescue success to 29.65%. A cost-two gate yields 23.84%, and a cost-three gate yields 21.68%.

The no-connector turn-1 baseline from the preceding result is 20.99%. In that sparse-disposable state, most of the theoretical current-window value of the three-discard connector disappears.

This is a direct quantitative interaction between temporal feasibility and DCI. The connector acts in the correct window, yet the hand often cannot pay for the edge.

## Finding 2: later draws repair discard AMR

With 20 disposable non-starters and a cost-two connector:

- turn 1: 27.595597%;
- turn 4: 39.372988%.

The ideal cost-zero connector reaches 40.187978% by turn 4. The gap becomes much smaller because later random draws can supply either the rescue Supporter directly or enough disposable cards to make the connector payable.

A one-turn AMR estimate therefore should not automatically be reused at later horizons. Discard payability evolves with the hand.

## Finding 3: higher discard costs remain visible for longer

At 20 disposable non-starters, the cost-three connector reaches 37.305618% by turn 4, while the cost-two connector reaches 39.372988%.

At 30 disposable non-starters, both approach the ideal connector much more closely by turn 4.

The interaction is nonlinear because the hand must cross a discrete discard threshold. Adding disposable density has larger strategic value when it moves many states across that threshold.

## Computer Search and Secret Box

For this narrow rescue objective, Computer Search is represented by a one-copy preserving connector with discard cost two. Secret Box can be stress-tested with discard cost three.

This does not compare the cards as whole cards.

Secret Box searches multiple Trainer categories simultaneously. That multi-axis effect can justify a larger cost and can satisfy other lines in the same action. Computer Search can find any one card and may have a stronger competing target than Gladion. Both are ACE SPEC resources with substantial connector-domination concerns.

The numbers here answer only: if this connector's sole purpose in the model is to find the rescue Supporter, how often does its discard gate permit that line by the horizon?

## Validation

The result is exact and uses no Monte Carlo sampling.

The reproducer independently validates a small labeled-card case:

- 10-card deck;
- 2 Prize cards;
- valid 3-card opening with 3 protected starters;
- 2 critical non-starters;
- 2 rescue Supporters;
- 1 preserving connector;
- 2 disposable cards;
- discard cost one;
- 3 rescue turns.

It exhaustively enumerates every accepted opening-hand subset and disjoint Prize subset. Future natural draws are recursively averaged over labeled cards. After each draw, every legal connector-spending count and the wait action are evaluated, and the best future success probability is selected.

The category dynamic program gives conditional rescue success `97.52308402585412%`; the independent labeled calculation gives the same value to floating-point precision.

The exact and labeled calculations also agree on

`P(any critical initially Prized | valid start) = 40.44817927170866%`.

Total setup-conditioned state mass is asserted to be one.

## Limitations

The binary disposable pool is intentionally coarse.

The model does not include:

- graded DCI values;
- state-dependent changes in which exact cards are disposable;
- discard payloads that are strategically beneficial;
- cards that must be preserved for another line;
- spare connector copies used as discard fodder;
- Secret Box's simultaneous Item, Tool, and Stadium value;
- competing uses of Computer Search;
- targeted search for the connector itself;
- stochastic connector effects;
- Ability, Item, or Supporter lock;
- Bench constraints;
- ordinary Prize-taking;
- alternative Prize recovery;
- matchup-specific criticality.

Setup-eligible starters are treated as protected rather than as generic discard fodder.

## Next useful work

The strongest next extension is an explicit competing-use model.

A connector such as Computer Search can often solve more than one missing channel. A state could require both Prize rescue and an attacker, Energy piece, or lock component. The optimizer could then choose which target to search and measure the opportunity cost of spending the connector on rescue.

That would directly formalize connector domination instead of treating it as an external caveat.
