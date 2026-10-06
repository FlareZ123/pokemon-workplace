# Discard-cost action realism: exact compositional baseline

## Question

How much can theoretical access to a discard-cost search card overstate its immediate usability when a deck contains many cards that are strategically protected from discard?

This result tests one narrow part of the AMR / DCI / connector-domination framework in `resources/human_concepts.md`. It does not assign a universal DCI score to cards. Instead, it freezes a game state and partitions non-action cards into two classes: cards acceptable to discard now and cards protected now.

## Card-text basis

The bundled Expanded card pool contains:

- `Ultra Ball` (`sv1-196`), which can be used only if the player discards 2 other cards from hand, then searches for a Pokémon.
- `Secret Box` (`sv6-163`), an ACE SPEC, which can be used only if the player discards 3 other cards from hand, then searches for an Item, Pokémon Tool, Supporter, and Stadium.

`Secret Box` is a singleton by ACE SPEC rule. The Ultra Ball calculations use four copies, a common maximum-copy stress case. Both referenced prints are marked Expanded legal in the bundled database.

## Exact model

Let:

- `N` = deck size;
- `A` = copies of the action card;
- `D` = non-action cards that are acceptable discard targets in the modeled state;
- `H` = sampled hand size;
- `C` = discard cost;
- `P = N - A - D` = protected/other cards.

For a hand containing `a` action copies and `d` designated disposable cards, the exact multivariate-hypergeometric mass is

`C(A,a) * C(D,d) * C(P,H-a-d) / C(N,H)`.

The action is playable when at least one action copy is present and enough fodder exists to pay the cost. The strict policy counts only the `D` designated cards. The spare-action policy also allows extra copies beyond the one being played to count as discard fodder.

The implementation is `tools/discard_gate_probability.py`. It exposes exact library functions for presence probability, playable probability, conditional payability, and minimum disposable-pool thresholds. `results/discard_cost_amr/reproduce.py` regenerates the tables below.

## Seven-card random sample

The table below uses `N=60`, `H=7`, four Ultra Ball, one Secret Box, Ultra Ball discard cost 2, and Secret Box discard cost 3. Ultra Ball uses the spare-action policy here because a second or later copy can be expendable in some states.

| Disposable non-action cards | Ultra Ball present | Ultra Ball playable (spares usable) | P(playable \| present) | Secret Box present | Secret Box playable | P(playable \| present) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 12 | 39.95% | 17.45% | 43.69% | 11.67% | 1.07% | 9.19% |
| 20 | 39.95% | 29.54% | 73.94% | 11.67% | 3.79% | 32.52% |
| 28 | 39.95% | 36.56% | 91.51% | 11.67% | 7.16% | 61.41% |

The important quantity is the conditional column. With only 12 non-action cards considered disposable, fewer than half of seven-card samples containing Ultra Ball can pay its cost even when spare Ultra Balls may be burned. Secret Box is much more sensitive: with 20 disposable non-action cards, only 32.52% of samples containing Secret Box can pay three discards.

## How large must the disposable pool be?

For the same seven-card sample, the following is the smallest `D` that reaches each target conditional payability:

| Conditional payability target | Ultra Ball, strict | Ultra Ball, spare copies usable | Secret Box |
| ---: | ---: | ---: | ---: |
| 50% | 16 | 14 | 25 |
| 80% | 24 | 23 | 35 |
| 90% | 29 | 28 | 39 |

This gives a useful compositional diagnostic. In this abstract state, a four-copy Ultra Ball package needs roughly 23 non-action disposable cards before at least 80% of seven-card samples that contain Ultra Ball can pay the cost under the spare-copy policy. A singleton Secret Box needs 35.

These thresholds are not deck-building recommendations. They quantify how demanding the costs are under a frozen binary discardability state.

## Hand-size sensitivity

At `D=20`, reducing the sampled hand size sharply reduces conditional payability:

| Sample size | Ultra Ball P(playable \| present), spares usable | Secret Box P(playable \| present) |
| ---: | ---: | ---: |
| 5 | 48.24% | 10.83% |
| 6 | 62.64% | 20.96% |
| 7 | 73.94% | 32.52% |
| 8 | 82.35% | 44.30% |

This supports the qualitative warning that putting cards into play, preserving singleton resources, or otherwise shrinking the pool of cards actually available to discard can strongly alter the realism of a search line. The hand-size table is only a sensitivity test. Real setup actions are selected and correlated with card identity, so a smaller uniform random sample is not a literal model of benching Pokémon.

## Strategic interpretation

### Derived result

A search card's draw probability can substantially exceed its immediate-play probability. The gap grows with higher discard cost, smaller hands, and fewer state-acceptable discard targets.

That means a graph or optimizer that gives full credit to `Ultra Ball -> Pokémon` or `Secret Box -> multiple Trainer categories` whenever the search card is reachable can materially overvalue the connector. A cost-aware representation should include the probability or state predicate that its discard requirement is realistically payable before granting the downstream access.

### Heuristic implication

For deck analysis, one useful intermediate quantity is:

`conditional payability = P(cost can be paid | action card is present)`.

This can be treated as one component of AMR. It should remain state- and matchup-dependent. Cards can move between protected and disposable classes as the game evolves, and the act of resolving earlier actions changes the hand itself.

### Relation to DCI

The binary partition here is intentionally cruder than the scalar DCI proposal in `resources/human_concepts.md`. It is useful because it is exact and interpretable. A future model could replace the binary classes with state-dependent policies or distributions over acceptable discard sets. It should avoid interpreting DCI values directly as independent discard probabilities unless that interpretation is explicitly justified.

## Validation

The implementation was checked in two ways:

1. selected 60-card outputs were independently recomputed from the same closed-form combinatorial definition;
2. a small `N=8` case was exhaustively enumerated over every labeled four-card hand and matched the library result exactly.

No Monte Carlo sampling is required for these reported values.

## Limitations

This is a compositional baseline, not a full first-turn simulator. It does not condition on mulligans, Active/Bench setup, Prize cards, draw effects, search sequencing, matchup information, Supporter contention, lock effects, or dynamic changes in discardability. It also assumes the `D` designated non-action cards are interchangeable with respect to the discard decision.

The model asks whether a cost can be paid using cards declared acceptable in the frozen state. It does not decide whether paying that cost is strategically correct, whether the searched target remains in deck, or whether another use of the same connector dominates the line.

## Next useful work

A stronger extension would feed actual decklists and explicit state-dependent discard policies into a turn-sequencing model. That would allow the same exact cost gate to interact with Prize knowledge, board setup, Supporter contention, connector domination, and matchup-specific preservation rules instead of treating `D` as a fixed deck-level count.