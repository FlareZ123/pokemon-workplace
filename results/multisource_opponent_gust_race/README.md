# Multi-source opposing gust arrivals in an exact two-sided Prize race

## Purpose

Earlier [joint Boss/Counter opening access](../mixed_gust_opening_access/) measured cards seen by a deadline. Earlier [stochastic opposing gust arrival](../stochastic_opposing_gust_arrival/) allowed only one hidden gust. This result composes their physical initial-hand and Prize layouts with an exact finite-turn **multi-source tactical race**.

Both players begin with fixed boards of abstract one-hit-KO targets worth one, two or three Prizes. We always attack, spending at most one of our held Boss or Counter tokens if we choose to gust. The opponent may attack, gust using a held Boss or Prize-legal Counter, or pass. The opponent chooses its promotion after we score; we choose ours after they score. Each opponent reply draws one physical deck card without replacement. Source copies remain held until used. The source's physical starting zone and draw arrivals are publicly observable in the general solver.

## Exact initial-zone model and dynamic game

A 60-card opposing deck has B Basics, b Boss copies, c Counter copies, seven opening cards and six Prizes. The first hand is conditioned to contain a Basic. The exact joint source-zone distribution tracks the number of each class in hand, Prizes and the 47-card remainder. On each subsequent reply, the draw event is Boss with probability deckBoss/deckSize, Counter with probability deckCounter/deckSize, and filler otherwise.

The [new state solver](../../tools/multisource_opponent_gust_race.py) uses exact rational minimax with a separate source count in hand for each category. An unspent Counter is playable on the opponent reply only when their remaining Prize count exceeds ours. Passing can allow the Counter gate to open after our next KO. A held Boss can gust regardless of Prize counts within this model.

## Same four total gust slots, two radically different terminal exposures

Both examples condition on our starting six Prizes and a Basic-valid opposing opening. Values shown are our chance of winning.

**Witness A, immediate Boss window.** Our Active is a one-Prizer; Bench has a one-Prizer and newly added two-Prizer; we hold two Counters. The opponent has two Prizes remaining and two three-Prize Pokémon, one Active and one Benched. Our first KO takes three Prizes, so the opponent's Counter gate remains closed at its first reply. A Boss seen by then can KO our newly added two-Prizer for the win; without it, our second attack wins. Therefore the exact formula is

P(our win) = 1 - F(B,b,1),

where F(B,b,1) is Boss access in opening hand plus first opponent draw.

**Witness B, two-reply Boss or Counter window.** Our Active is worth one Prize and Bench is (1,1,3). We hold Boss + Counter. The opponent has three Prizes remaining and three two-Prize targets, Active plus two Bench. We must score three two-Prize KOs. The opponent can pass after our first attack and wait: our second KO opens their Counter gate. Either Boss or Counter in hand or drawn by the second reply can then KO our three-Prizer. Therefore

P(our win) = 1 - F(B,b+c,2).

These two special witnesses have indistinguishable opposing KO rewards, so our own target choice gives no useful information-contingent improvement. The formulas survive hiding the opponent's source status **within these narrow abstract games**, even though the general solver reveals status.

## Exact 60-card outcomes

Hypothetical opposing deck with four Basic Pokémon and four total Boss/Counter slots:

| Boss / Counter split | Witness A: immediate Boss window | Witness B: two-reply either-source window |
| --- | ---: | ---: |
| 0 / 4 | 100.0000% | 54.2795% |
| 1 / 3 | 87.8956% | 54.2795% |
| 2 / 2 | 77.0696% | 54.2795% |
| 3 / 1 | 67.4074% | 54.2795% |
| 4 / 0 | 58.8028% | 54.2795% |

At B=16 Basics, Witness A spans 100% to 56.6788% and Witness B stays 52.3189% for all five splits.

This is a direct constructive example of **different terminal utility despite identical any-gust source access**. It also shows a state where source split changes no tactical result at all because Counter's future window makes all source classes interchangeable for that objective.

## Verification

The [reproducer](reproduce.py) performs 36 exhaustive physical labeled small-deck hand/Prize source-location comparisons and 1,404 independent deterministic endgame comparisons against the original [bidirectional gust solver](../../tools/two_sided_bidirectional_gust.py). It additionally checks 24 reductions to the previous one-source stochastic/physical mixture engines and 60 exact four-source witness formulas across six Basic counts and all five source splits.

Run `python -m results.multisource_opponent_gust_race.reproduce` from repository root. Calculations use Python Fraction arithmetic without sampling.

## Limitations and extensions

The model assumes every Pokémon is knocked out in one attack, no damage or Energy costs, no Bench development, no Item/Supporter lock, no search engine, and source-neutral gust executability beyond Counter's Prize gate. Real Boss uses a Supporter and Counter is an Item, so this substitution is invalid when locks and competing Supporter actions matter. The general model's public source revelation also limits direct inference to private-hand real play.

Future work should add turn-level Supporter and Item restrictions, source acquisition from realistic draw/search paths, and private opponent hand beliefs. These conditional mathematical outcomes are not matchup win percentages.