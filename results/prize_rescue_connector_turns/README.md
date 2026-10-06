# Turn-by-turn Prize rescue with typed connectors

## Question

How does the timing class of a connector change the probability of rescuing critical Prize cards by a fixed number of Supporter windows?

Earlier repository results established three pieces separately:

- `results/prize_rescue_start_condition/` gives the exact setup-conditioned Prize topology.
- `results/timed_prize_rescue/` separates topology, random card access, and the number of Supporter opportunities.
- `results/gladion_access_connectors/` shows that real routes to Gladion have different timing and zone semantics.

This result combines the first timing layer with typed one-shot connectors in an exact turn-by-turn model.

Implementation: `tools/prize_rescue_connector_turns.py`  
Reproducer and exhaustive validation: `results/prize_rescue_connector_turns/reproduce.py`

## Model

The deck is partitioned into:

- critical setup-eligible starters;
- critical non-starters;
- Gladion-like rescue Supporters;
- Supporter-preserving connectors that are setup starters;
- Supporter-preserving connectors that are non-starters;
- Supporter-consuming connectors;
- filler setup starters;
- filler non-starters.

The opening hand is conditioned on containing at least one setup-eligible starter. Prize cards are then sampled from the remaining deck.

After setup, each modeled rescue turn has:

1. one random draw from the current deck;
2. access to one ordinary Supporter play.

A **preserving connector** is an idealized one-shot effect that can search one rescue Supporter from the deck without consuming the Supporter play. This abstracts the timing class of suitable Items or Abilities.

A **consuming connector** is an idealized one-shot Supporter that can search one rescue Supporter from the deck. Playing it uses the current turn's Supporter action, so the fetched rescuer cannot be played until a later modeled turn.

Search effects are treated as shuffling the remaining deck. Future draw probabilities therefore depend only on category counts.

The objective is narrow: recover every modeled critical card that began in the Prize cards before the specified rescue-turn horizon ends. Ordinary Prize-taking and alternative recovery are excluded.

## Isolated optimal policy

Within this restricted objective, the action policy is deterministic.

After the turn's random draw:

1. use enough preserving connectors to secure rescue Supporters needed for the remaining critical Prize cards, limited by rescuer copies still in the deck;
2. if a rescue Supporter is in hand, play one and recover one critical Prize card;
3. otherwise, if a consuming connector is in hand and a rescuer remains in the deck, play the connector and put that rescuer into hand for a later turn.

This policy is optimal inside the model because preserving connectors have no competing modeled use, earlier rescue cannot reduce future rescue capacity, and a consuming connector only becomes useful on a turn where no rescue Supporter can be played directly.

Real deck play has competing connector uses, so this isolated optimality claim should not be exported to a full game without an opportunity-cost model.

## Illustrative baseline

Use:

- 60 cards;
- 6 Prize cards;
- a 7-card accepted opening;
- 12 setup-eligible starters;
- 4 modeled non-starter critical singletons;
- 2 rescue Supporters;
- connector counts shown below.

Condition on at least one modeled critical singleton being initially Prized.

| Connector package | Rescue by turn 1 | Rescue by turn 2 | Rescue by turn 3 | Rescue by turn 4 |
| --- | ---: | ---: | ---: | ---: |
| None | 20.988290% | 23.799232% | 26.377561% | 28.912644% |
| 2 preserving | 37.309088% | 42.258081% | 46.083579% | 49.706940% |
| 2 consuming | 20.988290% | 39.478163% | 43.994428% | 47.874305% |
| 4 preserving | 49.984029% | 56.572661% | 60.820024% | 64.692857% |
| 4 consuming | 20.988290% | 51.654606% | 57.133550% | 62.052336% |
| 2 preserving + 2 consuming | 37.309088% | 53.940562% | 59.259539% | 63.373202% |

For this setup-conditioned composition,

`P(any modeled critical is initially Prized) = 35.383108%`.

## Finding 1: consuming connectors have zero first-window rescue value

Adding two or four consuming connectors does not change turn-1 rescue success at all. It remains 20.988290%, exactly the no-connector baseline.

The reason is mechanical. A consuming connector can place a rescue Supporter into hand, but the connector itself uses the only modeled Supporter play for that turn. The fetched rescuer becomes useful starting on a later Supporter window.

A raw reachability graph would still add edges from those connectors to the rescuer and could incorrectly score them as immediate consistency.

## Finding 2: preserving connectors convert access into immediate action

Two preserving connectors raise turn-1 rescue success from 20.99% to 37.31%. Four raise it to 49.98%.

Those connectors can find a rescuer and leave the Supporter play available, so their search edge and the rescue action fit inside the same window.

This is the same timing distinction quantified in `results/supporter_outs_timing/`, now embedded in an actual multi-turn Prize-rescue objective.

## Finding 3: consuming connectors become valuable after the turn boundary

The two-consuming package rises from 20.99% on turn 1 to 39.48% by turn 2. The four-consuming package rises to 51.65% by turn 2.

This is useful evidence against treating Supporter-based search as simply "bad access." Its value is delayed access. A temporal graph should move the resource into a future Supporter window rather than delete the edge.

The mixed package illustrates complementarity. Two preserving plus two consuming connectors give 37.31% turn-1 success and 53.94% turn-2 success. The preserving class handles current-window rescue while consuming connectors can prepare later windows when a rescuer is missing.

## Relation to Active Move Realism

These numbers still represent an optimistic connector abstraction.

A preserving connector may require:

- discardable cards;
- an open Bench slot;
- an Ability that is not locked;
- an evolution already in play;
- a coin flip or top-N hit;
- another connector first.

A consuming connector may compete with an Energy, setup, gust, draw, or disruption Supporter on the same turn.

The model therefore isolates temporal AMR. It answers whether the action class itself permits the line, before adding discard, Bench, lock, stochastic, and opportunity-cost constraints.

## Relation to connector domination

Suppose Computer Search could fetch Gladion immediately, while the same Computer Search is also the only route to an attacker required that turn.

The preserving classification says the Gladion route is temporally feasible. It does not say that using the connector for Gladion is strategically optimal.

The next layer needs a policy objective with competing uses. This result deliberately keeps that problem separate so timing can be validated first.

## Validation

The reported values are exact. No Monte Carlo sampling is used.

The reproducer independently validates a small 10-card case using labeled cards rather than category probabilities. It exhaustively enumerates every accepted opening-hand subset and disjoint Prize subset. For every such state with a critical Prize, it recursively averages over each possible labeled natural draw, applies the same isolated rescue policy, and continues through the rescue horizon.

For the preserved regression case:

- exact conditional success by turn 2: `99.25831202046039%`;
- independent labeled-card result: the same value to floating-point precision;
- exact `P(any critical Prized | valid start)`: `37.23809523809508%`;
- independent labeled-card result: `37.23809523809524%`.

The total setup-conditioned state mass is also asserted to be one.

A second regression verifies the timing claim: with one rescue turn, adding four consuming connectors leaves the conditional success probability exactly equal to the no-connector baseline.

## Limitations

The connector effects are idealized deterministic one-shot searches.

The model does not yet encode:

- Computer Search or Secret Box discard costs;
- Xtransceiver coin flips;
- Pokégear 3.0 or Trainers' Mail partial-deck sampling;
- Tapu Lele-GX or Jirachi-EX Bench and trigger requirements;
- Battle Compressor plus VS Seeker multi-card assembly;
- Item, Ability, or Supporter lock;
- extra Supporter capacity such as Dual Brains;
- targeted search for the connectors themselves;
- draw Supporters or Abilities;
- ordinary Prize-taking;
- alternative Prize recovery;
- competing uses of connectors or Supporters;
- matchup-dependent criticality.

Every modeled rescue turn begins with one random draw and then supplies one ordinary Supporter action. The caller should interpret "turn 1" as the first turn in the chosen horizon where that structure applies, rather than automatically equating it with a player's literal first game turn.

## Next useful work

The strongest continuation is to replace one idealized preserving-connector class with concrete connector mechanics.

A practical first pair is:

- deterministic but discard-gated Computer Search;
- probabilistic Xtransceiver.

That would connect the turn model to the repository's DCI/AMR discard-gate work and show how timing feasibility, card-access probability, and discard payability compound.

A second path is to add a small competing-use objective so a connector can choose between Gladion and a setup resource. That would turn connector domination from a qualitative warning into a policy comparison.
