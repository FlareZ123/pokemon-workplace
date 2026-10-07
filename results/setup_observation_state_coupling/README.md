# Setup events are both observations and state transitions

## Question

Can an opponent mulligan be modeled as a pure information observation?

No.

In the Pokémon TCG setup process, the same opponent mulligan that reveals information about the opponent's deck construction also grants the other player the option to draw a bonus card. The event therefore changes both:

- the observer's belief about the opponent;
- the observer's physical hand and deck state.

This result composes two existing exact Aichi models:

- `tools/aichi_setup_inference.py` for Bayesian inference from exact opponent mulligan counts;
- `tools/iron_thorns_mulligan_bonus.py` for the corresponding change in Kazuma Iron Thorns first-turn Volt Cyclone reachability.

Reproducer: `results/setup_observation_state_coupling/reproduce.py`

## Aichi comparison

Use an equal prior over two published 2026 CL Aichi Open League lists:

- Kazuma Iron Thorns: 4 forced setup Basics;
- Takahiro Ando Vileplume Control: 14 forced setup Basics.

Their per-attempt mulligan probabilities are approximately:

- Iron Thorns: 60.0500%;
- Vileplume: 13.8591%.

For each exact observed opponent mulligan count `k`, the table shows:

1. the prior-predictive probability of seeing exactly that count before the opponent keeps;
2. the posterior probability that the opponent is Iron Thorns;
3. the represented probability that Kazuma's Iron Thorns player reaches the scoped first-turn Volt Cyclone line after taking those `k` bonus cards.

| Exact opponent mulligans | Observation mass | P(Iron Thorns | count) | Represented Volt Cyclone |
| ---: | ---: | ---: | ---: |
| 0 | 63.045447244% | 31.683463534% | 34.008906144% |
| 1 | 17.964148941% | 66.771789624% | 37.884578127% |
| 2 | 8.030262894% | 89.698087341% | 41.551388399% |
| 3 | 4.440051532% | 97.417777597% | 45.013092009% |
| 4 | 2.613293734% | 99.391966571% | 48.274114878% |
| 5 | 1.561944259% | 99.859011341% | 51.339472431% |

The first six count outcomes contain 97.655148603% of the equal-prior observation mass.

## Finding 1: the same event moves belief and resources in the same direction

More observed mulligans make a low-Basic Iron Thorns opponent increasingly likely.

At the same time, each mulligan grants another bonus card to the observing Iron Thorns player, increasing the probability of reaching the represented ALS.

For example:

- zero mulligans imply only a 31.68% posterior on Iron Thorns and leave the line at 34.01%;
- one mulligan raises the Iron posterior to 66.77% and the line to 37.88%;
- two mulligans raise them to 89.70% and 41.55%.

A setup transcript is therefore not merely evidence attached to an otherwise unchanged game state.

## Finding 2: a belief-only setup model loses a physical state mutation

A Bayesian classifier can update archetype probabilities correctly while still producing the wrong gameplay state if it ignores the bonus cards caused by the same mulligans.

Conversely, a simulator can draw the bonus cards while missing the opponent information revealed by how many mulligans occurred and by any revealed mulligan contents.

A stronger setup transition should carry both outputs:

`setup_event -> (new physical state, public observation)`

The belief update then consumes the observation, while the gameplay policy consumes the mutated physical state.

## Finding 3: matchup uncertainty changes expected ALS consistency

Before observing the opponent's exact mulligan count, with a 50/50 prior over these two candidate lists, the matchup-averaged represented Volt Cyclone probability is **37.002651373%**.

The zero-bonus value is 34.008906144%.

Thus, under this toy two-archetype prior, opponent mulligans add about **2.993745229 percentage points** of expected line reachability before any opponent card effect is considered.

This number is prior-specific. The structural point is broader: setup uncertainty and setup resource generation are coupled through the same random event.

## Method

For a candidate with mulligan probability `q`, the likelihood of exactly `k` mulligans followed by a keep is:

`q^k * (1-q)`.

The posterior uses those exact-count likelihoods under equal priors.

The gameplay state uses the same `k` as the number of bonus cards taken, then applies the already validated exact Iron Thorns first-turn model.

The two components are independently reproducible and are composed without Monte Carlo sampling.

## Limits

This result deliberately uses only exact mulligan count as the observation.

It does not yet combine:

- the actual cards revealed in mulligan hands;
- optional setup policies;
- other candidate archetypes;
- opponent-specific tactical decisions after the archetype posterior changes;
- Trainers' Mail or broader Iron Thorns access routes;
- any decision to take fewer than the maximum available bonus cards.

The Iron Thorns reachability objective is monotone in the fixed bonus-card counts tested by the underlying result, making full bonus-card uptake appropriate for this scoped line.

## Representation consequence

Setup should be represented as an observation-emitting state transition rather than as a separate pregame classifier followed by an unrelated initial-state sampler.

That representation can naturally support later work where the newly inferred matchup changes which cards should be preserved, discarded, benched, searched, or committed during the first turn.
