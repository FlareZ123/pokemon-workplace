# Competing connector deadlines: urgency as a resource-allocation constraint

## Question

How does a universal connecto's value change when the setup target is needed earlier than Prize rescue?

The preceding `results/competing_connector_policy/` model gives both objectives the same deadline. This extension separates them:

- the setup target must reach hand by `setup_deadline`;
- every initially Prized modeled critical must be rescued by `rescue_turns`.

The connector remains a single Computer Search-like, cost-2 preserving action. It can be held or spent on either target under the flexible policy.

Implementation: `tools/competing_connector_deadlines.py`  
Reproducer and independent labeled-card validation: `results/competing_connector_deadlines/reproduce.py`

## Model

The deck composition and setup conditioning follow the preceding competing-connector result.

The illustrative baseline uses:

- 60 cards;
- 6 Prize cards;
- valid 7-card opening;
- 12 protected setup starters;
- 4 critical non-starters;
- 2 rescue Supporters;
- 2 setup-target copies;
- 1 universal connector;
- 20 disposable non-starters;
- discard cost 2.

Rescue is due by turn 4. The setup deadline varies from turn 1 through turn 4.

As before, four policies use the same deck slots:

- connector unavailable;
- connector searches rescue only;
- connector searches setup only;
- connector can choose either target from the current state.

Every modeled turn begins with one random draw and provides one ordinary Supporter play.

## Baseline result

Condition on at least one modeled critical being initially Prized.

| Setup deadline | No connector | Rescue-only | Setup-only | Flexible | Flexible gain over best single-purpose |
| ---: | ---: | ---: | ---: | ---: | ---: |
| Turn 1 | 6.491432% | 8.819364% | 8.430905% | 10.758838% | 1.939474 pp |
| Turn 2 | 7.294606% | 9.917252% | 9.666630% | 12.278854% | 2.361602 pp |
| Turn 3 | 8.083309% | 10.996805% | 10.841677% | 13.732233% | 2.735428 pp |
| Turn 4 | 8.857541% | 12.058535% | 11.950575% | 15.114299% | 3.055764 pp |

The turn-4 row reproduces the equal-deadline model exactly.

## Finding 1: deadline pressure destroys option value before connector capacity changes

The connector still has one search at every deadline. Its discard cost and target set are unchanged.

Moving the setup deadline from turn 4 to turn 1 lowers flexible success by **4.355462 percentage points**.

The gain from flexible target allocation also falls from **3.055764** to **1.939474 points**.

The earlier deadline leaves fewer natural draws before the setup channel must be resolved. It also removes future states in which the connector can be held while waiting to see whether setup arrives naturally.

This is a temporal form of connector contention. A flexible search can have broad card-text reach while its strategic option value shrinks sharply when one target expires early.

## Finding 2: an early deadline can make a sparse setup channel dominate the dedicated use

With only one setup-target copy and rescue still due by turn 4:

| Setup deadline | Rescue-only | Setup-only | Flexible |
| ---: | ---: | ---: | ---: |
| Turn 1 | 4.645533% | 5.342003% | 6.566858% |
| Turn 2 | 5.268056% | 6.274076% | 7.657815% |
| Turn 3 | 5.891407% | 7.176479% | 8.718009% |
| Turn 4 | 6.515941% | 8.040959% | 9.739620% |

The setup-only policy is stronger than rescue-only throughout this sparse-target regime.

The flexible policy remains stronger because it can use the connector for rescue in states where setup arrived naturally and can redirect the same connector to setup when that channel is still missing.

Target density and deadline therefore interact. A fixed reservation rule for a universal search loses information contained in both the remaining outs and the time left to use them.

## Finding 3: equal-horizon models can overstate how long a choice remains available

A same-deadline model allows the optimizer to defer both objectives until the common horizon.

That assumption is unsuitable for many Archetype-Line-Specific lines. An attacker, Stadium, Tool, Energy enabler, or lock component may be mandatory on the first meaningful attack turn while a Prized singleton is only relevant later.

Representing only the final horizon preserves too much future flexibility. The state needs a deadline per objective, or another equivalent representation of expiring action value.

## Validation

The reproducer performs two independent checks.

First, it builds a labeled 10-card model with:

- 3-card accepted opening;
- 2 Prize cards;
- 3 setup starters;
- 2 critical non-starters;
- 1 rescue Supporter;
- 1 setup target;
- 1 universal connector;
- 2 disposable cards;
- discard cost 1;
- 2 rescue turns.

It exhaustively enumerates accepted openings, disjoint Prize sets, all future natural draws, and all legal modeled actions for setup deadlines 1 and 2. The labeled and category models agree to floating-point precision.

Second, setting `setup_deadline == rescue_turns` is checked against `tools/competing_connector_policy.py`. All four policy probabilities match the preceding equal-deadline implementation.

## Interpretation

A useful connector representation needs both resource capacity and temporal validity.

For a universal search, the state should preserve:

- remaining target copies;
- current hand access;
- Prize state;
- discard payability;
- whether the connector has been spent;
- each objective's remaining action windows.

This extension strengthens the general connector-domination result. Opportunity cost depends on which uses remain available when the search is eventually spent.

## Limitations

The model remains an abstract exact baseline.

It does not include:

- ordinary Prize-taking;
- targeted search for the connector;
- graded or card-specific DCI;
- alternative Prize recovery;
- different Supporter demands after setup;
- lock effects;
- Bench constraints;
- Energy attachment bandwidth;
- card-specific setup sequencing;
- opponent interaction;
- matchup-specific objective values.

The setup objective is still represented as acquiring one card. A real line may require playing that card, satisfying a target restriction, attaching Energy, evolving, or consuming another action window before its deadline.

## Next useful work

A strong next step is a real Expanded deck line with an actual early setup deadline.

The repository now has a conservative Trainer search compiler and typed target allocator. Combining those with this deadline state would allow a real connector to choose among legally searchable resources while preserving discard cost, target multiplicity, Supporter timing, and the deadline of the downstream line.
