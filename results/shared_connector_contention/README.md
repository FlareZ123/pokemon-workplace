# Shared connector contention: one search card cannot satisfy two missing channels

## Question

How much can a reachability graph overstate joint consistency when one physical search connector is counted as an out to two different required resources?

This result isolates the one-use connector problem described qualitatively in `resources/human_concepts.md`. A broad connector can reach either of two targets, while each physical copy can only be spent once.

Implementation: `tools/shared_connector_contention.py`

Independent reproducer: `results/shared_connector_contention/reproduce.py`

## Model

The deck has five categories:

1. target A;
2. target B;
3. shared one-shot connectors;
4. setup-eligible starters;
5. filler.

Targets and connectors are non-starters in this baseline.

The state process follows setup order. A seven-card opening is accepted only when it contains a setup-eligible starter. Prize cards come from the remaining deck. The model can then expose a configurable number of additional random non-Prize cards.

A connector in the accessible hand may search exactly one missing target from the remaining deck.

The question is whether both target channels can be satisfied at the access check.

## Exact joint-access rule

Let:

- `h_A` be whether target A is already accessible in hand;
- `h_B` be whether target B is already accessible in hand;
- `d_A` and `d_B` indicate that the corresponding target still exists in the searchable deck;
- `c` be the number of shared connectors in the accessible hand.

The number of connectors required is:

`I(h_A = 0) + I(h_B = 0)`

Joint access is feasible when both target channels still exist and `c` is at least that required count.

For two channels, the naive graph error has a simple state characterization. It occurs exactly when both targets are missing from hand, both remain searchable in deck, and exactly one shared connector is accessible.

A per-target reachability test says each target is reachable through that connector. The joint state cannot realize both edges because the connector has capacity one.

## Illustrative baseline

Use:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 setup-eligible starters;
- 2 copies of target A;
- 2 copies of target B;
- no additional random draws before the check.

### Connector-count sensitivity

| Shared connectors | True joint access | Naive joint access | Connector-contention overstatement | Overstatement among naive joint successes |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 3.799330% | 3.799330% | 0.000000% | 0.000000% |
| 1 | 7.121909% | 14.286842% | 7.164933% | 50.150571% |
| 2 | 10.900978% | 23.783761% | 12.882783% | 54.166299% |
| 3 | 15.033145% | 32.366549% | 17.333404% | 53.553452% |
| 4 | 19.425794% | 40.107146% | 20.681352% | 51.565255% |

The naive graph gives every connector full credit on both target channels. The exact model requires two physical connector copies when both targets are missing from hand.

This produces a large joint-consistency error even though each individual target-access calculation is correct in isolation.

With one shared connector, each target individually has 29.837458% access in this composition. Their joint access is 7.121909% after one-use capacity is enforced.

## Extra random exposure

Keep two shared connectors and the same target counts.

| Extra random non-Prize draws | True joint access | Naive joint access | Connector-contention overstatement |
| ---: | ---: | ---: | ---: |
| 0 | 10.900978% | 23.783761% | 12.882783% |
| 1 | 14.213975% | 27.642711% | 13.428736% |
| 2 | 17.760189% | 31.486157% | 13.725967% |
| 5 | 29.273829% | 42.735032% | 13.461203% |
| 10 | 48.934817% | 59.696240% | 10.761423% |

More exposure raises direct target access and eventually reduces the absolute contention gap. The gap can initially grow because additional cards also make a shared connector more likely to appear while both target channels still need service.

## Target-copy sensitivity

Use one shared connector and no additional random draws.

| Target A copies | Target B copies | True joint access | Naive joint access | Connector-contention overstatement |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 2.709935% | 9.772975% | 7.063039% |
| 1 | 2 | 4.458002% | 11.585171% | 7.127170% |
| 2 | 2 | 7.121909% | 14.286842% | 7.164933% |
| 2 | 4 | 11.505118% | 17.346604% | 5.841486% |
| 4 | 4 | 18.176949% | 22.894279% | 4.717329% |

Higher target counts improve direct access, so the shared connector is less often asked to cover both missing channels at once.

## Strategic interpretation

This is a concrete form of connector domination and graph contention.

A connector can have broad theoretical reach while providing only one unit of realized search capacity. Counting the same card independently as an out to a Pokémon, an Energy, a rescue Supporter, or another required piece can create fictitious joint consistency.

The result also explains why marginal access metrics do not compose safely. Two channels can each have a strong individual access percentage while their simultaneous completion rate remains much lower.

A deck optimizer therefore needs resource-capacity state on connectors. Reachability edges alone are insufficient whenever one connector can serve several competing targets.

## Relation to existing repository work

`results/supporter_outs_timing/` shows that action class can make an apparent Supporter out unusable in the current window.

`results/discard_gated_supporter_access/` shows that a correctly timed connector can still fail because its discard cost cannot be paid.

This result isolates another failure mode. The connector is assumed usable and costless, while its one-use search capacity is enforced across two simultaneous needs.

The three effects are distinct and can compound in a real deck state.

## Validation

The reported values are exact.

The reproducer independently enumerates a labeled nine-card deck over every accepted opening-hand subset, every disjoint Prize subset, and every disjoint later-draw subset. It compares:

- target A access;
- target B access;
- true joint access;
- naive joint access;
- connector-contention probability;
- total probability mass.

The category model matches the labeled enumeration to floating-point precision. The reproducer also asserts that naive joint access minus true joint access equals the contention probability.

## Scope limits

The current model has two target channels and a connector that searches one target per use.

It omits discard costs, Supporter timing, Bench space, Ability or Item lock, stochastic search, target priority, multi-axis cards that genuinely obtain several resources with one play, search for the connector itself, ordinary Prize-taking, and state-dependent target urgency.

A card such as Secret Box can legitimately obtain several Trainer categories in one use. Such a card should receive a higher connector capacity for the channels its text can satisfy together.

## Next useful work

The next extension should generalize from two target channels to an arbitrary requirement vector and connector capacity matrix.

That representation can encode:

- one-shot any-card search;
- multi-axis search such as Stadium plus Special Energy plus Tool;
- connectors restricted to a subset of targets;
- several copies of the same connector;
- target-specific action costs;
- state-dependent connector availability.

A second useful extension is to add competing target value. When only one connector is available, the model should choose which missing channel receives it according to downstream win probability or line feasibility rather than treating every target as equally urgent.
