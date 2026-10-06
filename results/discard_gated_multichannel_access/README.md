# Discard-gated multichannel access: cost realism and connector capacity compound

## Question

When a broad capacity-one search connector also has a discard cost, how much of a naive joint-access estimate is lost to payability and how much is lost because one physical connector cannot satisfy several missing channels?

This result combines two repository research threads:

- discard-gated Active Move Realism;
- finite shared-connector capacity.

Implementation: `tools/discard_gated_multichannel_access.py`

Independent reproducer: `results/discard_gated_multichannel_access/reproduce.py`

## Model

The deck contains:

- several target channels;
- copies of one any-target capacity-one connector;
- non-starter cards currently acceptable to discard;
- protected setup-eligible starters;
- protected non-starter filler.

The exact setup process conditions on a starter-containing opening hand, sets Prize cards from the remaining deck, and can add later random exposure.

For each resulting state, three access quantities are computed.

**Raw naive joint reachability**

The connector is considered available whenever it is exposed. Its discard cost is ignored. The same connector is also allowed to appear as an independent out to every missing target channel.

**Cost-aware naive joint reachability**

The discard cost must be payable. A physical connector still receives independent reachability credit on every target channel.

**Exact joint access**

The discard cost must be payable and each usable connector copy can search only one missing target channel.

The decomposition is:

`raw naive - exact = cost-gate overstatement + capacity overstatement`

where:

`cost-gate overstatement = raw naive - cost-aware naive`

and:

`capacity overstatement = cost-aware naive - exact`.

## Baseline

Use:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 protected setup-eligible starters;
- three target channels;
- 2 copies of each target;
- 1 capacity-one any-target connector;
- no additional random draws.

The raw naive joint access is **11.227080%** in every row below. Changing how many other non-starters are disposable does not change raw graph reachability.

### Two-card discard cost

| Disposable non-starters | Cost-aware naive | Exact joint | Cost-gate overstatement | Capacity overstatement | Total raw overstatement |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 3.045321% | 0.657543% | 8.181759% | 2.387777% | 10.569537% |
| 15 | 5.204087% | 0.751411% | 6.022993% | 4.452675% | 10.475669% |
| 20 | 7.241674% | 0.865215% | 3.985406% | 6.376459% | 10.361865% |
| 25 | 8.888855% | 0.987563% | 2.338226% | 7.901292% | 10.239517% |
| 30 | 10.047491% | 1.107062% | 1.179589% | 8.940429% | 10.120018% |
| 35 | 10.744108% | 1.212322% | 0.482972% | 9.531786% | 10.014758% |

At 20 disposable non-starters, enforcing the discard cost removes 3.985406 percentage points. Finite connector capacity removes another 6.376459 points.

At 35 disposable non-starters, the discard gate is small. Capacity becomes the dominant reason that individual target edges fail to compose into a complete line.

### Three-card discard cost

| Disposable non-starters | Cost-aware naive | Exact joint | Cost-gate overstatement | Capacity overstatement | Total raw overstatement |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 1.006259% | 0.580649% | 10.220821% | 0.425610% | 10.646431% |
| 15 | 1.947524% | 0.595914% | 9.279556% | 1.351610% | 10.631166% |
| 20 | 3.420250% | 0.627127% | 7.806830% | 2.793123% | 10.599953% |
| 25 | 5.246308% | 0.679985% | 5.980772% | 4.566323% | 10.547095% |
| 30 | 7.160048% | 0.760183% | 4.067032% | 6.399865% | 10.466897% |
| 35 | 8.877946% | 0.873417% | 2.349134% | 8.004529% | 10.353663% |

The higher discard cost shifts more error into the payability gate across the same disposable-card densities.

## Computer Search interpretation

The bundled `Computer Search` `bw7-137` requires two discards and searches for one card.

For a frozen state where the modeled disposable-card pool accurately describes what can be burned, the two-card table captures the interaction between its discard gate and its capacity-one any-card search shape.

This remains an abstract deck composition. The disposable pool is state-dependent, and Computer Search may have a stronger competing target.

## Why a cost-three row is abstract

A three-card discard cost can be useful as a sensitivity test.

It should not automatically be mapped to Secret Box in this multichannel model. Secret Box can retrieve several Trainer categories in one use, so its connector capacity is richer than the capacity-one shape modeled here.

That distinction is exactly why cost semantics and output-capacity semantics should be represented separately.

## Finding 1: the dominant failure mode changes with state

At low disposable density, raw graph access fails mostly because the connector cannot pay its cost.

At high disposable density, the connector becomes reliably payable and shared-capacity contention becomes the larger error.

A single scalar edge weight cannot represent both regimes accurately unless it is strongly state-dependent.

## Finding 2: fixing one modeling error exposes another

Suppose an optimizer becomes DCI-aware and removes connector credit when the discard cost cannot be paid.

That improves the model, while substantial overstatement can remain if the same payable connector is counted as an out to every simultaneous need.

Conversely, a capacity-aware graph can still be optimistic if it assumes every exposed connector is playable.

The two corrections address different state constraints.

## Validation

The reproducer uses three independent checks.

First, with discard cost zero, the model reduces exactly to `tools/shared_connector_multichannel.py`.

Second, with one target channel, the model reduces to the existing `tools/discard_gated_supporter_access.py` result for the matching composition. Raw naive access and discard-gated access agree to floating-point precision.

Third, a small labeled three-channel deck is exhaustively enumerated over accepted opening hands, Prize cards, and later draws. Raw naive, cost-aware naive, and exact joint probabilities match the category model.

## Scope limits

The disposable-card partition is binary and frozen for the modeled access check.

The model does not include:

- graded DCI values;
- cards that become disposable after sequencing;
- spare connector copies as discard fodder;
- target cards that themselves may be acceptable discards;
- multi-axis connector outputs;
- Supporter action timing;
- Bench requirements;
- lock states;
- competing connector uses;
- ordinary Prize-taking.

These should be added as separate state semantics rather than folded into one generic consistency score.

## Next useful work

The next integration should combine state-derived payability with the general connector-profile engine.

That would allow different connector types in the same deck state, including:

- capacity-one any-card search with a discard gate;
- true multi-axis search with its own discard gate;
- Supporter-consuming search;
- Bench-dependent Ability search.

The resulting state evaluator can measure a complete requirement vector after all connector costs and capacities are applied.
