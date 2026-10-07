# Output capacity versus discard cost: a Computer Search / Secret Box abstraction

## Question

When two independently required channels can both be searched by Secret Box, when does its larger simultaneous output overcome its higher discard cost relative to Computer Search?

The bundled card database gives the relevant structural difference:

- **Computer Search**: discard 2 cards, then search for any 1 card;
- **Secret Box**: discard 3 other cards, then search for an Item, a Pokémon Tool, a Supporter, and a Stadium.

For a two-channel objective, Computer Search has output capacity one. Secret Box can have output capacity two when the two required resources occupy distinct eligible Secret Box categories.

Implementation: `tools/connector_output_capacity.py`  
Reproducer: `results/connector_output_capacity/reproduce.py`

## Model

The opening and Prize model is the same exact setup-conditioned model used by `results/connector_domination/`.

The deck contains:

- target A;
- target B;
- one connector;
- currently disposable non-starters;
- protected setup starters;
- protected non-starters.

Joint success requires access to both target classes in the same window.

For the Computer Search-like connector:

- discard cost = 2;
- output capacity = 1.

For the Secret Box-like connector:

- discard cost = 3;
- output capacity = 2.

The Secret Box interpretation assumes target A and target B are distinct categories that Secret Box can legally search at the same time. The model does not give Secret Box arbitrary two-card universal search.

## Baseline composition

Hold fixed:

- 60 cards;
- 6 Prize cards;
- accepted 7-card opening;
- 12 protected setup starters;
- target A = 3 outs;
- target B = 2 outs;
- 1 connector.

Vary only the number of currently disposable non-starters.

| Disposable pool | Capacity 1, cost 2 | Capacity 2, cost 3 | Capacity-2 difference |
| ---: | ---: | ---: | ---: |
| 5 | 5.663012% | 5.521746% | -0.141266 pp |
| 10 | 6.188586% | 5.915645% | -0.272941 pp |
| 15 | 6.882632% | 6.867371% | -0.015261 pp |
| 16 | 7.028951% | 7.125762% | +0.096811 pp |
| 20 | 7.607900% | 8.352325% | +0.744425 pp |
| 25 | 8.262883% | 10.185674% | +1.922791 pp |
| 30 | 8.781818% | 12.093487% | +3.311669 pp |
| 35 | 9.134688% | 13.783877% | +4.649189 pp |

The positive-payability crossover in this baseline occurs between **D=15 and D=16**.

At D=0 or D=1, neither connector can pay its discard requirement in the modeled opening hand, so both reduce to direct target access. Those trivial ties are excluded from the crossover statement.

## Finding 1: connector capacity can outweigh a worse discard gate

At low disposable density, the cost-two connector has better AMR.

Once discard payability is common enough, the output bottleneck becomes more important. The capacity-two connector can solve states where both target channels are missing, while the capacity-one connector cannot.

This creates a real crossover rather than a universal ranking.

## Finding 2: DCI changes which ACE SPEC structure is favored

At D=10, the cost-two connector leads by 0.272941 percentage points.

At D=20, the capacity-two connector leads by 0.744425 points.

At D=35, the capacity-two connector leads by 4.649189 points.

The strategic value of the extra output is therefore conditional on the hand's discardability distribution.

A graph that ignores discard cost would favor the multi-output connector too early. A graph that ignores output capacity would favor the cheaper connector too long.

## Finding 3: multi-axis search is a different connector class

This result helps explain why Secret Box should not be represented as "Computer Search with cost three."

For eligible multi-channel states, Secret Box can satisfy several independent requirements in one action.

That property directly attacks connector domination.

Computer Search remains more flexible in **what** single card it can find. Secret Box is less universal, while being broader in simultaneous eligible outputs.

The correct comparison therefore depends on both target categories and current resource contention.

## Rules and card-text scope

The local card data marks `bw7-137` Computer Search as an Expanded-legal ACE SPEC Item that discards two cards and searches for one card.

It marks `sv6-163` Secret Box as an Expanded-legal ACE SPEC Item that requires discarding three other cards and can search one Item, one Pokémon Tool, one Supporter, and one Stadium.

This analysis uses only the two-channel consequence of those texts.

## Validation

The output-capacity implementation uses the collapsed exact Prize integration from `tools/connector_domination.py`.

For capacity one and discard cost two, the reproducer cross-checks every displayed row against the independently implemented capacity-aware connector-domination result.

It also asserts the stated D=15 / D=16 crossover.

No Monte Carlo sampling is used.

## Limitations

The two target channels are abstract.

Secret Box receives capacity two only when both targets are simultaneously eligible distinct search categories.

The model excludes the value of its third and fourth possible search outputs, as well as cases where an extra searched Trainer is intentionally taken to become future discard fodder or support another line.

It also excludes:

- later draws;
- search routes into the ACE SPEC;
- graded DCI;
- Supporter contention after acquisition;
- Stadium replacement effects;
- Tool attachment constraints;
- lock effects;
- Bench constraints;
- attacks and Energy timing;
- matchup-specific value.

## Next useful work

Extend the capacity model to three and four eligible channels.

That can quantify the nonlinear value of Secret Box when a real line simultaneously needs, for example, an Item, Tool, Supporter, and Stadium, and compare that against the probability of paying its three-card discard requirement.
