# Quick Ball allocation frontier: contention as an option state

## Question

The existing Quick Ball connector-contention result compares two first-window models:

- a physical model where each Quick Ball copy can search one Basic Pokémon;
- a reusable-edge counterfactual that lets one Quick Ball satisfy both a required Basic attacker and the Tapu Lele-GX route to Gladion.

At the 12-disposable-card baseline, the physical joint success rate is 13.057113%, while the reusable-edge graph reports 26.715925%.

What exactly is the 13.658811 percentage-point gap?

This result resolves that gap by preserving every Pareto-maximal outcome available in each opening and Prize state.

Implementation: `tools/quick_ball_allocation_frontier.py`  
Reproducer: `results/quick_ball_allocation_frontier/reproduce.py`

## State and outcome

The deck model matches `results/quick_ball_connector_contention/`:

- 60 cards;
- 6 Prize cards;
- accepted 7-card opening;
- 1 Tapu Lele-GX;
- 1 required Basic attacker;
- 10 other setup-eligible starters;
- 4 modeled critical non-starter singletons;
- 2 Gladion-like rescue Supporters;
- 4 Quick Ball;
- 12 dedicated disposable non-starters in the baseline;
- filler cards.

The calculation conditions on a valid opening and at least one modeled critical card being Prized.

Each state is evaluated on two binary coordinates:

`(attacker established, Gladion accessible)`

A Quick Ball search consumes one physical Quick Ball and one designated disposable card. Tapu Lele-GX keeps the same setup-trigger semantics as the previous result. If it is the only starter in the opening, it is consumed by the starting Active role and cannot later supply Wonder Tag from hand.

The model records the Pareto frontier of reachable coordinate pairs instead of collapsing the state immediately to one preferred action.

## Baseline frontier distribution

| Pareto frontier | Probability |
| --- | ---: |
| neither channel available: `((0,0),)` | 40.869952% |
| Gladion only: `((0,1),)` | 21.853400% |
| choice between Gladion or attacker: `((0,1),(1,0))` | 13.658811% |
| attacker only: `((1,0),)` | 10.560723% |
| both channels: `((1,1),)` | 13.057113% |

The masses sum to one up to floating-point precision.

## Finding 1: the previous graph overstatement is exactly the choice-state mass

The physical joint success rate is the mass of `((1,1),)`:

**13.057113%**

The reusable-edge graph effectively treats every state in the choice frontier as though both outputs could be achieved. Its joint rate is therefore:

`13.057113% + 13.658811% = 26.715925%`

This exactly reproduces the previous reusable-edge result.

So the earlier **13.658811-point overstatement** has a concrete interpretation. It is the set of states where the available resources can complete either missing channel, while physical Quick Ball capacity prevents completion of both.

This gives a stronger representation of connector contention. The lost mass is a real allocation opportunity rather than a generic consistency failure.

## Finding 2: target value determines how the choice mass should be spent

For non-negative additive downstream values `A` for attacker completion and `G` for Gladion access, the optimal expected utility is:

`p11 * (A + G) + p10 * A + p01 * G + pchoice * max(A, G)`

where the `p` terms correspond to the five frontier classes above.

The connector still has one physical search. The `max(A, G)` term means the choice states are allocated according to the current downstream value of the two channels.

If attacker completion has greater value in a state, the Quick Ball should serve the attacker. If Gladion access has greater value, the same physical Quick Ball should serve Tapu Lele-GX.

With equal unit values for both channels, the optimal expected number of completed channels in the baseline is **0.721871613**.

This utility is an abstract evaluation layer. It is not a win-rate estimate.

## Finding 3: rescue-priority and attacker-priority projections recover useful marginal views

If every choice state is allocated to Gladion, the conditional Gladion-access probability is:

`13.057113% + 21.853400% + 13.658811% = 48.569324%`

That exactly reproduces the strict opening-window result from `results/quick_ball_lele_access/`.

If every choice state is allocated to the attacker, attacker establishment becomes:

`13.057113% + 10.560723% + 13.658811% = 37.276648%`

The frontier therefore contains both single-purpose projections without rerunning a different physical model.

This is useful for larger planners because action allocation can be postponed until a downstream objective is known.

## Finding 4: discard flexibility exposes more allocation states

Vary only the number of dedicated disposable non-starters:

| Disposable cards | Both | Choice | Attacker only | Gladion only | Neither |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 7.788644% | 6.688874% | 10.545315% | 24.149331% | 50.827835% |
| 8 | 10.737693% | 11.027936% | 10.578597% | 22.849445% | 44.806329% |
| 12 | 13.057113% | 13.658811% | 10.560723% | 21.853400% | 40.869952% |
| 16 | 14.841821% | 15.102014% | 10.518595% | 21.117580% | 38.419990% |
| 20 | 16.176902% | 15.768579% | 10.470514% | 20.597945% | 36.986060% |
| 24 | 17.138910% | 15.971688% | 10.427612% | 20.251339% | 36.210450% |

As the discard gate becomes easier to pay, more states reach either the joint-success frontier or the allocation-choice frontier.

This clarifies the interaction between DCI and connector contention. Scarce discardable material can hide a later connector-allocation problem. Once payment becomes realistic, the policy question of which target deserves the search becomes more common.

## Validation

The category model is exact and uses no Monte Carlo sampling.

The reproducer independently enumerates a labeled ten-card deck over every accepted opening and every disjoint Prize set. It reconstructs the available physical Quick Ball allocations and compares the complete frontier distribution against the category model to floating-point precision.

It also imports the previous `quick_ball_connector_contention` model and proves three cross-result identities:

1. `P(((1,1),))` equals the previous physical joint-success result;
2. `P(((1,1),)) + P(choice)` equals the previous reusable-edge counterfactual;
3. the previous graph overstatement equals `P(choice)` exactly.

These checks are repeated across several disposable-card counts.

## Interpretation

A shared connector should carry a reachable-outcome frontier until the model has enough downstream information to choose its use.

A binary joint-success metric discards useful information in states where one of two goals can still be achieved. A reusable-edge graph makes the opposite error by awarding both goals.

The Pareto frontier keeps the finite resource constraint and preserves the decision that remains available.

This is a concrete form of connector domination and option value. Search reachability describes possible targets. Physical connector count limits simultaneous completion. Strategic value decides which reachable target should receive the scarce search.

## Limitations

This is still an opening-window model. It excludes later random draws, Item lock, Ability lock, Bench saturation, other Pokémon search cards, ordinary Prize-taking, Energy and evolution requirements for the attacker, competing Supporters, opponent interaction, and matchup-specific values.

The required attacker channel ends when the Basic attacker is established. A real Archetype-Line-Specific objective may require Energy, evolution, switching, Stadium access, or an attack by a deadline.

The additive utility helper is deliberately minimal. Larger planners can consume the frontier directly and apply a state-dependent continuation value instead.

## Next useful work

A high-value continuation is to add one or more later random draws and per-channel deadlines while carrying the frontier forward.

That would allow a policy to defer Quick Ball when future information has value, spend it early when the attacker deadline is urgent, or redirect it to Tapu Lele-GX when Prize rescue becomes the binding channel.
